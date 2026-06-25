from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ComplianceAction = Literal[
    "allow_send",
    "draft_review_block",
    "honor_unsubscribe",
    "internal_suppression",
    "block_send",
]

BLOCKING_PROVIDER_EVENTS = {"spam_report", "complaint", "bounce", "dropped", "unsubscribe"}
BLOCKING_MISSING_FIELDS = {"unsubscribe_url", "postal_address", "reviewer_approval", "fresh_thread_review"}


class ComplianceGateResult(BaseModel):
    """Typed pre-draft/pre-send decision for future email adapters.

    The gate is deliberately separate from the chat-only next-action enum. It is a
    deterministic local guardrail layer for opt-outs, suppression events, missing
    commercial-email fields, and human-review state; it is not a legal compliance
    certification or deliverability guarantee.
    """

    send_allowed: bool
    draft_allowed: bool = True
    requires_human_review: bool = False
    compliance_action: ComplianceAction
    blocked_reasons: list[str] = Field(default_factory=list)
    suppression_reason: str | None = None
    missing_required_fields: list[str] = Field(default_factory=list)
    provider_event_types: list[str] = Field(default_factory=list)
    review_requirements: list[str] = Field(default_factory=list)


class ComplianceGate:
    """Minimal deterministic compliance gate for research fixtures.

    Inputs are intentionally plain dictionaries so the future email/webhook
    adapter can normalize provider payloads before calling the gate. The current
    implementation is conservative: any explicit stop-contact label, blocking
    provider event, blocking missing pre-send field, or unresolved human-review
    requirement prevents provider sends.
    """

    @staticmethod
    def evaluate_pre_send(compliance: dict[str, Any] | None) -> ComplianceGateResult:
        data = compliance or {}
        must_stop = bool(data.get("must_stop_contact", False))
        requires_review = bool(data.get("requires_human_review", False))
        provider_events = [str(event) for event in data.get("provider_event_types", [])]
        missing_fields = [str(field) for field in data.get("missing_required_fields", [])]
        review_requirements = [str(item) for item in data.get("review_requirements", [])]
        suppression_reason = data.get("suppression_reason")

        blocked_reasons: list[str] = []
        if must_stop:
            blocked_reasons.append("must_stop_contact")
        for event in provider_events:
            if event in BLOCKING_PROVIDER_EVENTS:
                blocked_reasons.append(f"provider_event:{event}")
        for field in missing_fields:
            if field in BLOCKING_MISSING_FIELDS:
                blocked_reasons.append(f"missing_required_field:{field}")
        if requires_review:
            blocked_reasons.append("requires_human_review")

        send_allowed = not blocked_reasons
        draft_allowed = bool(data.get("draft_allowed", True))

        if must_stop and suppression_reason == "ambiguous_opt_out" and requires_review:
            compliance_action: ComplianceAction = "draft_review_block"
            draft_allowed = bool(data.get("draft_allowed", True))
        elif must_stop:
            compliance_action = "honor_unsubscribe" if suppression_reason in {
                "explicit_unsubscribe",
                "natural_language_opt_out",
                "ambiguous_opt_out",
            } else "internal_suppression"
            draft_allowed = bool(data.get("draft_allowed", False))
        elif provider_events and any(event in BLOCKING_PROVIDER_EVENTS for event in provider_events):
            compliance_action = "internal_suppression"
            draft_allowed = bool(data.get("draft_allowed", False))
        elif not send_allowed and (requires_review or review_requirements):
            compliance_action = "draft_review_block"
        elif not send_allowed:
            compliance_action = "block_send"
        else:
            compliance_action = "allow_send"

        return ComplianceGateResult(
            send_allowed=send_allowed,
            draft_allowed=draft_allowed,
            requires_human_review=requires_review,
            compliance_action=compliance_action,
            blocked_reasons=blocked_reasons,
            suppression_reason=str(suppression_reason) if suppression_reason else None,
            missing_required_fields=missing_fields,
            provider_event_types=provider_events,
            review_requirements=review_requirements,
        )

    @staticmethod
    def evaluate_pre_draft(compliance: dict[str, Any] | None) -> ComplianceGateResult:
        """Use the same conservative labels before draft generation.

        Stop-contact and provider suppression events should normally prevent even
        a sales draft. Missing footer/reviewer fields may still allow internal
        remediation drafts while blocking provider sends.
        """

        result = ComplianceGate.evaluate_pre_send(compliance)
        if result.compliance_action in {"honor_unsubscribe", "internal_suppression"}:
            result.draft_allowed = False
        return result
