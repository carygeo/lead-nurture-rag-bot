from __future__ import annotations

from typing import Any


BLOCKING_EVENT_TYPES = {"spam_report", "complaint", "bounce", "dropped", "unsubscribe"}


def _lower(value: Any) -> str:
    return str(value or "").strip().lower()


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


class ProviderEventNormalizer:
    """Normalize raw provider event fixtures into ComplianceGate inputs.

    This is a deliberately small adapter boundary for research fixtures. It maps
    provider-specific event names from SendGrid, Postmark, Amazon SES, and
    Mailgun into the local `compliance` dictionary consumed by ComplianceGate.
    It does not validate provider signatures, persist raw payloads, or cover each
    provider's full event schema.
    """

    @staticmethod
    def normalize(provider: str, raw_event: dict[str, Any]) -> dict[str, Any]:
        provider_key = _lower(provider)
        if provider_key == "sendgrid":
            return ProviderEventNormalizer._normalize_sendgrid(raw_event)
        if provider_key == "postmark":
            return ProviderEventNormalizer._normalize_postmark(raw_event)
        if provider_key in {"amazon_ses", "ses", "aws_ses"}:
            return ProviderEventNormalizer._normalize_ses(raw_event)
        if provider_key == "mailgun":
            return ProviderEventNormalizer._normalize_mailgun(raw_event)
        return {
            "must_stop_contact": False,
            "provider_event_types": [],
            "suppression_reason": None,
            "source_event_name": _lower(raw_event.get("event") or raw_event.get("RecordType") or raw_event.get("notificationType")),
        }

    @staticmethod
    def _result(source_event_name: str, provider_event_types: list[str], suppression_reason: str | None) -> dict[str, Any]:
        event_types = _dedupe(provider_event_types)
        blocking = bool(BLOCKING_EVENT_TYPES.intersection(event_types))
        return {
            "must_stop_contact": blocking,
            "send_allowed": False if blocking else True,
            "provider_event_types": event_types,
            "suppression_reason": suppression_reason,
            "source_event_name": source_event_name,
        }

    @staticmethod
    def _normalize_sendgrid(raw_event: dict[str, Any]) -> dict[str, Any]:
        event = _lower(raw_event.get("event"))
        if event == "spamreport":
            return ProviderEventNormalizer._result(event, ["spam_report", "complaint"], "provider_spam_complaint")
        if event in {"unsubscribe", "group_unsubscribe"}:
            return ProviderEventNormalizer._result(event, ["unsubscribe"], "provider_unsubscribe")
        if event == "bounce":
            return ProviderEventNormalizer._result(event, ["bounce"], "hard_bounce")
        if event == "dropped":
            return ProviderEventNormalizer._result(event, ["dropped"], "provider_dropped")
        return ProviderEventNormalizer._result(event, [], None)

    @staticmethod
    def _normalize_postmark(raw_event: dict[str, Any]) -> dict[str, Any]:
        record_type = _lower(raw_event.get("RecordType") or raw_event.get("record_type"))
        event_name = record_type
        if record_type == "spamcomplaint":
            return ProviderEventNormalizer._result(event_name, ["spam_report", "complaint"], "provider_spam_complaint")
        if record_type == "subscriptionchange":
            suppress = _lower(raw_event.get("SuppressSending") or raw_event.get("SuppressSendingReason"))
            if suppress and suppress not in {"false", "none", "0"}:
                return ProviderEventNormalizer._result(event_name, ["unsubscribe"], "provider_unsubscribe")
        if record_type == "bounce":
            bounce_type = _lower(raw_event.get("Type") or raw_event.get("type"))
            if "hard" in bounce_type or bounce_type in {"bademailaddress", "blocked"}:
                return ProviderEventNormalizer._result(event_name, ["bounce"], "hard_bounce")
            return ProviderEventNormalizer._result(event_name, ["bounce"], "provider_bounce")
        return ProviderEventNormalizer._result(event_name, [], None)

    @staticmethod
    def _normalize_ses(raw_event: dict[str, Any]) -> dict[str, Any]:
        notification_type = _lower(raw_event.get("notificationType") or raw_event.get("eventType"))
        if notification_type == "complaint":
            return ProviderEventNormalizer._result(notification_type, ["spam_report", "complaint"], "provider_spam_complaint")
        if notification_type == "bounce":
            bounce = raw_event.get("bounce") or {}
            bounce_type = _lower(bounce.get("bounceType"))
            reason = "hard_bounce" if bounce_type == "permanent" else "provider_bounce"
            return ProviderEventNormalizer._result(notification_type, ["bounce"], reason)
        return ProviderEventNormalizer._result(notification_type, [], None)

    @staticmethod
    def _normalize_mailgun(raw_event: dict[str, Any]) -> dict[str, Any]:
        event = _lower(raw_event.get("event") or (raw_event.get("event-data") or {}).get("event"))
        severity = _lower(raw_event.get("severity") or (raw_event.get("event-data") or {}).get("severity"))
        if event == "complained":
            return ProviderEventNormalizer._result(event, ["spam_report", "complaint"], "provider_spam_complaint")
        if event == "unsubscribed":
            return ProviderEventNormalizer._result(event, ["unsubscribe"], "provider_unsubscribe")
        if event == "failed":
            reason = "hard_bounce" if severity == "permanent" else "provider_bounce"
            return ProviderEventNormalizer._result(event, ["bounce", "dropped"], reason)
        return ProviderEventNormalizer._result(event, [], None)
