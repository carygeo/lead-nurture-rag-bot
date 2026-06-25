from __future__ import annotations

from lead_nurture_rag.compliance_gate import ComplianceGate


def test_explicit_unsubscribe_blocks_send_and_draft() -> None:
    result = ComplianceGate.evaluate_pre_draft(
        {
            "must_stop_contact": True,
            "send_allowed": False,
            "suppression_reason": "explicit_unsubscribe",
        }
    )

    assert result.send_allowed is False
    assert result.draft_allowed is False
    assert result.compliance_action == "honor_unsubscribe"
    assert "must_stop_contact" in result.blocked_reasons


def test_missing_footer_blocks_send_but_allows_internal_remediation_draft() -> None:
    result = ComplianceGate.evaluate_pre_send(
        {
            "commercial_email": True,
            "missing_required_fields": ["unsubscribe_url", "postal_address"],
            "requires_human_review": True,
        }
    )

    assert result.send_allowed is False
    assert result.draft_allowed is True
    assert result.requires_human_review is True
    assert result.compliance_action == "draft_review_block"
    assert "missing_required_field:unsubscribe_url" in result.blocked_reasons
    assert "missing_required_field:postal_address" in result.blocked_reasons


def test_provider_spam_complaint_suppresses_send() -> None:
    result = ComplianceGate.evaluate_pre_send(
        {
            "provider_event_types": ["spam_report", "complaint"],
            "suppression_reason": "provider_spam_complaint",
        }
    )

    assert result.send_allowed is False
    assert result.draft_allowed is False
    assert result.compliance_action == "internal_suppression"
    assert result.suppression_reason == "provider_spam_complaint"


def test_empty_compliance_context_allows_send() -> None:
    result = ComplianceGate.evaluate_pre_send({})

    assert result.send_allowed is True
    assert result.draft_allowed is True
    assert result.compliance_action == "allow_send"
    assert result.blocked_reasons == []
