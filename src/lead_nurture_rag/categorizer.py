from __future__ import annotations

import re
from urllib.parse import urlparse

TAXONOMY = {
    "payment_application_validation": {"payment application", "pay app", "pay apps", "lien waiver", "lien waivers", "subcontractor payment"},
    "risk_reduction": {"risk", "compliance", "approval", "audit", "missing", "error", "errors"},
    "pricing": {"pricing", "price", "cost", "budget", "roi"},
    "implementation": {"implementation", "integrate", "integration", "onboarding", "deploy", "workflow"},
    "case_study": {"case study", "customer", "results", "testimonial", "success story"},
    "scheduling": {"demo", "schedule", "book", "appointment", "meeting", "contact"},
}

PAGE_TYPE_PATTERNS = {
    "pricing": {"pricing", "price", "plans"},
    "case_study": {"case-stud", "customers", "testimonial", "success"},
    "solution": {"solution", "service", "product", "platform", "features"},
    "faq": {"faq", "questions", "help"},
    "about": {"about", "company", "team"},
    "contact": {"contact", "demo", "schedule", "book"},
    "blog": {"blog", "article", "insight", "resources"},
}

PERSONAS = {
    "executive": {"executive", "owner", "ceo", "cfo", "vp", "director"},
    "project_team": {"project manager", "project team", "project executive", "operations", "construction team"},
    "finance_team": {"finance", "accounting", "controller", "payables", "ap"},
}

INDUSTRIES = {
    "construction": {"construction", "contractor", "subcontractor", "jobsite", "project team"},
    "real_estate": {"real estate", "developer", "property"},
}

QUESTION_PATTERNS = {
    "how_it_works": {"how it works", "workflow", "process", "platform", "features"},
    "pain_point": {"reduce", "manual", "slow", "risk", "missing", "errors", "bottleneck"},
    "proof": {"case study", "results", "customer", "roi", "testimonial"},
    "pricing": {"pricing", "price", "cost", "budget"},
    "schedule_demo": {"demo", "schedule", "book", "appointment", "meeting"},
}


def _contains(text: str, terms: set[str]) -> bool:
    low = text.lower()
    return any(term in low for term in terms)


def _matches(text: str, mapping: dict[str, set[str]]) -> list[str]:
    return [label for label, terms in mapping.items() if _contains(text, terms)]


def categorize_page(url: str, title: str = "", text: str = "") -> dict:
    parsed = urlparse(url)
    path_text = f"{parsed.path} {title} {text[:2000]}".replace("-", "_").replace("/", " ")
    page_type = "general"
    for label, terms in PAGE_TYPE_PATTERNS.items():
        if _contains(path_text.replace("_", "-"), terms) or _contains(path_text, terms):
            page_type = label
            break
    topics = _matches(path_text, TAXONOMY)
    personas = _matches(path_text, PERSONAS)
    industries = _matches(path_text, INDUSTRIES)
    return {
        "url": url,
        "domain": parsed.netloc.lower(),
        "page_title": title,
        "page_type": page_type,
        "topics": topics,
        "personas": personas,
        "industries": industries,
    }


def categorize_chunk(text: str, page_metadata: dict | None = None) -> dict:
    page_metadata = page_metadata or {}
    topics = set(page_metadata.get("topics", [])) | set(_matches(text, TAXONOMY))
    questions = _matches(text, QUESTION_PATTERNS)
    if _contains(text, QUESTION_PATTERNS["schedule_demo"] | QUESTION_PATTERNS["pricing"]):
        intent_stage = "decision"
    elif _contains(text, QUESTION_PATTERNS["proof"] | {"compare", "evaluate", "benefit", "value"}):
        intent_stage = "consideration"
    else:
        intent_stage = "awareness"
    return {
        **page_metadata,
        "intent_stage": intent_stage,
        "topics": sorted(topics),
        "personas": sorted(set(page_metadata.get("personas", [])) | set(_matches(text, PERSONAS))),
        "industries": sorted(set(page_metadata.get("industries", [])) | set(_matches(text, INDUSTRIES))),
        "questions_answered": questions or ["general_value"],
    }


def metadata_to_search_text(metadata: dict) -> str:
    parts = []
    for key in ("company_name", "page_type", "intent_stage", "topics", "personas", "industries", "questions_answered"):
        value = metadata.get(key)
        if isinstance(value, list):
            parts.extend(str(item).replace("_", " ") for item in value)
        elif value:
            parts.append(str(value).replace("_", " "))
    return " ".join(parts)
