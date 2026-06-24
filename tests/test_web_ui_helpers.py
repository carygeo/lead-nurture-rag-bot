from __future__ import annotations

import json

from requests.exceptions import JSONDecodeError

from lead_nurture_rag.web_helpers import (
    DEFAULT_CAMPAIGN,
    DEFAULT_COMPANY_URL,
    default_campaign_json,
    format_response_payload,
)


def test_default_company_url_is_getsupernews_domain() -> None:
    assert DEFAULT_COMPANY_URL == "https://getsupernews.com"
    assert DEFAULT_CAMPAIGN["company_name"] == "Supernews"
    assert DEFAULT_CAMPAIGN["root_url"] == "https://getsupernews.com"
    assert DEFAULT_CAMPAIGN["allowed_domains"] == ["getsupernews.com"]
    assert DEFAULT_CAMPAIGN["seed_pages"] == ["https://getsupernews.com/"]
    assert DEFAULT_CAMPAIGN["target_persona"] == "mobile news readers, publishers, media teams, and news consumers"
    assert "bite-sized news" in DEFAULT_CAMPAIGN["offer"]


def test_default_campaign_json_is_pretty_printed_valid_json() -> None:
    payload = json.loads(default_campaign_json())

    assert payload["company_name"] == "Supernews"
    assert payload["root_url"] == "https://getsupernews.com"


def test_format_response_payload_falls_back_to_text_for_non_json_response() -> None:
    class NonJsonResponse:
        status_code = 500
        text = "Internal Server Error"

        def json(self):
            raise JSONDecodeError("Expecting value", self.text, 0)

    assert format_response_payload(NonJsonResponse()) == {
        "status_code": 500,
        "body": "Internal Server Error",
    }
