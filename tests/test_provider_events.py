from __future__ import annotations

from lead_nurture_rag.compliance_gate import ComplianceGate
from lead_nurture_rag.provider_events import ProviderEventNormalizer


def test_sendgrid_spamreport_normalizes_to_complaint_suppression() -> None:
    compliance = ProviderEventNormalizer.normalize("sendgrid", {"event": "spamreport", "email": "lead@example.com"})

    assert compliance["must_stop_contact"] is True
    assert compliance["send_allowed"] is False
    assert compliance["provider_event_types"] == ["spam_report", "complaint"]
    assert compliance["suppression_reason"] == "provider_spam_complaint"

    gate = ComplianceGate.evaluate_pre_send(compliance)
    assert gate.send_allowed is False
    assert gate.compliance_action == "internal_suppression"


def test_postmark_hard_bounce_normalizes_to_hard_bounce() -> None:
    compliance = ProviderEventNormalizer.normalize("postmark", {"RecordType": "Bounce", "Type": "HardBounce"})

    assert compliance["must_stop_contact"] is True
    assert compliance["provider_event_types"] == ["bounce"]
    assert compliance["suppression_reason"] == "hard_bounce"


def test_ses_complaint_normalizes_to_complaint_suppression() -> None:
    compliance = ProviderEventNormalizer.normalize(
        "amazon_ses",
        {"notificationType": "Complaint", "complaint": {"complainedRecipients": [{"emailAddress": "lead@example.com"}]}},
    )

    assert compliance["provider_event_types"] == ["spam_report", "complaint"]
    assert compliance["suppression_reason"] == "provider_spam_complaint"


def test_mailgun_permanent_failure_normalizes_to_bounce_and_dropped() -> None:
    compliance = ProviderEventNormalizer.normalize("mailgun", {"event": "failed", "severity": "permanent"})

    assert compliance["provider_event_types"] == ["bounce", "dropped"]
    assert compliance["suppression_reason"] == "hard_bounce"
