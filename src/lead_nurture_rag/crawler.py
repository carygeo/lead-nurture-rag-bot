from __future__ import annotations

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


def extract_document(url: str, html: str, company_name: str, target_persona: str | None = None, offer: str | None = None) -> CrawledDocument:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "noscript", "svg"]):
        tag.decompose()
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = normalize_text(main.get_text(" "))
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
        doc = extract_document(url, html, config.company_name, config.target_persona, config.offer)
        if doc.text:
            docs.append(doc)
        if depth < config.crawl_depth:
            for link in extract_links(url, html, allowed_domains):
                if link not in seen:
                    queue.append((link, depth + 1))
    return docs
