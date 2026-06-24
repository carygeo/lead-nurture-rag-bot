from __future__ import annotations

import json
from typing import Any

DEFAULT_COMPANY_URL = "https://getsupernews.com"

DEFAULT_CAMPAIGN: dict[str, Any] = {
    "company_name": "Supernews",
    "root_url": "https://getsupernews.com",
    "allowed_domains": ["getsupernews.com"],
    "seed_pages": ["https://getsupernews.com/"],
    "crawl_depth": 1,
    "max_pages": 25,
    "target_persona": "business owner or marketing lead",
    "offer": "AI-powered customer newsletter and content workflow",
}


def default_campaign_json() -> str:
    return json.dumps(DEFAULT_CAMPAIGN, indent=2)


def format_response_payload(response: Any) -> Any:
    """Return JSON when available, otherwise a display-safe fallback payload."""
    try:
        return response.json()
    except ValueError:
        return {
            "status_code": getattr(response, "status_code", None),
            "body": getattr(response, "text", ""),
        }
