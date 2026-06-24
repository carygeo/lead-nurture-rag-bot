from __future__ import annotations

import json
import re
from collections import deque
from dataclasses import dataclass, field
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from .categorizer import categorize_page
from .retriever import normalize_text

NOISE_PATH_PARTS = (
    "privacy", "terms", "cookie", "login", "signin", "signup", "careers", "jobs",
    "wp-json", "tag/", "category/", "author/", "cart", "checkout",
)


class CampaignConfig(BaseModel):
    company_name: str
    root_url: str
    allowed_domains: list[str] = Field(default_factory=list)
    seed_pages: list[str] = Field(default_factory=list)
    crawl_depth: int = 1
    max_pages: int = 25
    target_persona: str | None = None
    offer: str | None = None

    def normalized_seeds(self) -> list[str]:
        return self.seed_pages or [self.root_url]

    def domains(self) -> set[str]:
        domains = set(self.allowed_domains)
        domains.add(urlparse(self.root_url).netloc.lower())
        return {d.lower().removeprefix("www.") for d in domains}


@dataclass
class CrawledDocument:
    url: str
    title: str
    text: str
    metadata: dict = field(default_factory=dict)


def canonicalize_url(url: str) -> str:
    clean, _fragment = urldefrag(url)
    parsed = urlparse(clean)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") or "/"
    return parsed._replace(scheme=scheme, netloc=netloc, path=path, query="").geturl()


def should_skip_url(url: str, allowed_domains: set[str]) -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc.lower().removeprefix("www.")
    if parsed.scheme not in {"http", "https"}:
        return True
    if domain not in allowed_domains:
        return True
    path = parsed.path.lower()
    if any(part in path for part in NOISE_PATH_PARTS):
        return True
    if path.endswith((".jpg", ".jpeg", ".png", ".gif", ".svg", ".zip", ".mp4", ".mp3")):
        return True
    return False


def _metadata_text(soup: BeautifulSoup) -> str:
    values: list[str] = []
    if soup.title and soup.title.string:
        values.append(soup.title.string)
    for attrs in (
        {"name": "description"},
        {"property": "og:title"},
        {"property": "og:description"},
        {"name": "twitter:title"},
        {"name": "twitter:description"},
    ):
        tag = soup.find("meta", attrs=attrs)
        content = tag.get("content") if tag else None
        if content:
            values.append(content)
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        if not script.string:
            continue
        try:
            payload = json.loads(script.string)
        except json.JSONDecodeError:
            continue
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if isinstance(item, dict):
                for key in ("name", "description", "url"):
                    value = item.get(key)
                    if isinstance(value, str):
                        values.append(value)
    return normalize_text(" ".join(dict.fromkeys(values)))


TEXT_BUNDLE_KEYS = (
    "children",
    "label",
    "title",
    "description",
    "subtitle",
    "heading",
    "subheading",
    "text",
    "alt",
)


def _decode_js_string(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except json.JSONDecodeError:
        return value.replace(r"\n", " ").replace(r"\"", '"')


def _looks_like_copy(value: str) -> bool:
    value = normalize_text(value)
    if len(value) < 4 or len(value) > 320:
        return False
    if not re.search(r"[A-Za-z]{3}", value):
        return False
    if re.fullmatch(r"[a-z0-9_./:-]+", value, flags=re.IGNORECASE):
        return False
    if any(token in value for token in ("className", "function", "@license", "http://www.w3.org")):
        return False
    if any(token in value for token in ("[", "]", "--", "var(", "hsl(", "px-", "text-", "bg-")):
        return False
    low = value.lower()
    if any(
        phrase in low
        for phrase in (
            "article not found",
            "page not found",
            "return to home",
            "analysis isn't available",
            "fort myers",
            "mostly clear",
            "hot, humid",
        )
    ):
        return False
    return True


def extract_bundle_copy(js_text: str) -> str:
    """Extract user-visible marketing copy from a minified SPA bundle.

    Many customer/prototype sites are client-rendered and the first HTML
    response contains only metadata plus an app shell. Their useful page copy
    often appears in minified JavaScript as object properties like
    `children:"..."` or `label:"..."`. Keep extraction conservative so the RAG
    store gets visible copy rather than arbitrary implementation code.
    """
    values: list[str] = []
    key_pattern = "|".join(re.escape(key) for key in TEXT_BUNDLE_KEYS)
    for match in re.finditer(rf"(?:{key_pattern}):\"((?:[^\"\\]|\\.){{2,320}})\"", js_text):
        value = _decode_js_string(match.group(1))
        if _looks_like_copy(value):
            values.append(normalize_text(value))
    return normalize_text(" ".join(dict.fromkeys(values)))


def _same_origin_asset_url(page_url: str, asset_src: str) -> str | None:
    asset_url = canonicalize_url(urljoin(page_url, asset_src))
    page_domain = urlparse(page_url).netloc.lower().removeprefix("www.")
    asset_domain = urlparse(asset_url).netloc.lower().removeprefix("www.")
    if page_domain != asset_domain:
        return None
    return asset_url


def _spa_bundle_text(url: str, soup: BeautifulSoup, timeout: int = 20) -> str:
    values: list[str] = []
    headers = {"User-Agent": "lead-nurture-rag-bot/0.1"}
    for script in soup.find_all("script", src=True):
        asset_url = _same_origin_asset_url(url, script["src"])
        if not asset_url or not asset_url.endswith(".js"):
            continue
        try:
            response = requests.get(asset_url, timeout=timeout, headers=headers)
            response.raise_for_status()
        except requests.RequestException:
            continue
        bundle_copy = extract_bundle_copy(response.text)
        if bundle_copy:
            values.append(bundle_copy)
    return normalize_text(" ".join(dict.fromkeys(values)))


def extract_document(
    url: str,
    html: str,
    company_name: str,
    target_persona: str | None = None,
    offer: str | None = None,
    include_spa_bundle: bool = False,
) -> CrawledDocument:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    metadata_text = _metadata_text(soup)
    bundle_text = _spa_bundle_text(url, soup) if include_spa_bundle else ""
    for tag in soup(["script", "style", "nav", "footer", "noscript", "svg"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    body_text = normalize_text(main.get_text(" "))
    text_parts = [metadata_text]
    if len(body_text.split()) >= 5 and body_text.lower() not in {"edit with"}:
        text_parts.append(body_text)
    if bundle_text:
        text_parts.append(bundle_text)
    text = normalize_text(" ".join(part for part in text_parts if part))
    metadata = categorize_page(url=url, title=title, text=text)
    metadata.update({"company_name": company_name})
    if target_persona:
        metadata["target_persona"] = target_persona
    if offer:
        metadata["offer"] = offer
    return CrawledDocument(url=url, title=title, text=text, metadata=metadata)


def extract_links(base_url: str, html: str, allowed_domains: set[str]) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for anchor in soup.find_all("a", href=True):
        url = canonicalize_url(urljoin(base_url, anchor["href"]))
        if not should_skip_url(url, allowed_domains):
            links.append(url)
    return list(dict.fromkeys(links))


def crawl_campaign(config: CampaignConfig, timeout: int = 20) -> list[CrawledDocument]:
    allowed_domains = config.domains()
    queue = deque((canonicalize_url(seed), 0) for seed in config.normalized_seeds())
    seen: set[str] = set()
    docs: list[CrawledDocument] = []
    headers = {"User-Agent": "lead-nurture-rag-bot/0.1"}

    while queue and len(docs) < config.max_pages:
        url, depth = queue.popleft()
        if url in seen or should_skip_url(url, allowed_domains):
            continue
        seen.add(url)
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()
        if "html" not in response.headers.get("content-type", "text/html"):
            continue
        html = response.text
        doc = extract_document(
            url,
            html,
            config.company_name,
            config.target_persona,
            config.offer,
            include_spa_bundle=True,
        )
        if doc.text:
            docs.append(doc)
        if depth < config.crawl_depth:
            for link in extract_links(url, html, allowed_domains):
                if link not in seen:
                    queue.append((link, depth + 1))
    return docs
