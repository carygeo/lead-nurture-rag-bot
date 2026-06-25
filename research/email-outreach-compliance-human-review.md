# Email outreach compliance and human-review constraints for AI lead nurture bots

Date: 2026-06-24
Scope: initial repo research for future email adapter architecture: inbound webhook/poller, normalization, identity mapping, compliance checks, suppression/bounces/spam complaints, and draft-before-send human review. This is product/engineering research, not legal advice.

## Key findings and source URLs

- **US CAN-SPAM applies to commercial email and makes senders responsible even when vendors/agents send on their behalf.** Requirements include accurate header/from/routing info, non-deceptive subject lines, clear ad identification where applicable, valid physical postal address, clear opt-out mechanism, opt-out processing for at least 30 days after send, honoring opt-outs within 10 business days, and monitoring outsourced senders. Source: FTC, "CAN-SPAM Act: A Compliance Guide for Business" — https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- **Mailbox-provider rules now impose deliverability/compliance gates, especially for bulk senders.** Gmail requires SPF/DKIM, DMARC alignment for 5,000+/day senders, RFC 5322 formatting, TLS, low spam rate below 0.3%, one-click unsubscribe plus visible unsubscribe for marketing/subscribed messages, and auto-unsubscribe for repeated bounces. Source: Google, "Email sender guidelines" — https://support.google.com/a/answer/81126
- **Yahoo has similar bulk-sender rules.** Requires SPF/DKIM, valid DMARC policy, aligned From domain, one-click List-Unsubscribe, visible unsubscribe link, unsubscribe honored within 2 days, spam rate below 0.3%, reverse DNS, and bounce/complaint monitoring. Source: Yahoo Sender Hub, "Best practices" — https://senders.yahooinc.com/best-practices/
- **UK PECR treats email/SMS marketing to individuals as consent-first, with a narrow soft opt-in for prior customers; B2B corporate emails are less restrictive but objections still need suppression.** Messages must not conceal identity and must include a valid contact/unsubscribe address. Source: ICO, "Electronic mail marketing" — https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/electronic-and-telephone-marketing/electronic-mail-marketing/
- **EU/UK GDPR affects lead enrichment, profiling, scoring, and automated prioritization.** GDPR Article 21 gives a right to object at any time to personal-data processing for direct marketing, including related profiling; after objection, data must no longer be processed for that purpose and the right must be clearly presented by first communication. Source: GDPR text via EUR-Lex — https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
- **Automated decision-making/profiling can trigger rights to explanation, contestation, and human intervention where decisions are solely automated and have legal or similarly significant effects.** Lead scoring is usually lower risk than credit/employment, but human review and override are prudent where scores affect access, pricing, eligibility, or aggressive outreach. Sources: GDPR Article 22 via EUR-Lex — https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng ; ICO, "Automated decision-making, including profiling" — https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/automated-decision-making-and-profiling/
- **Canada CASL is consent-heavy and reaches commercial electronic messages.** CASL focuses on commercial electronic messages and asks businesses to obtain consent before sending; it also covers address harvesting, misleading electronic representations, and spam reporting. Source: Government of Canada, "Canada's anti-spam legislation" — https://ised-isde.canada.ca/site/canada-anti-spam-legislation/en
- **Channel expansion risk:** if nurture extends from email to SMS/calls/WhatsApp, telemarketing/robotext consent rules become a separate high-risk regime. Source for US consumer-facing robocall/robotext concerns: FCC, "Stop Unwanted Robocalls and Texts" — https://www.fcc.gov/consumers/guides/stop-unwanted-robocalls-and-texts
- **Provider events are compliance inputs, not just analytics.** Official provider docs expose webhooks/notifications/events for bounces, spam reports/complaints, unsubscribes, deliveries, failures, and subscription changes. These events should update suppression state before a model generates or sends follow-up drafts. Sources: SendGrid Event Webhook — https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event ; Postmark Webhooks — https://postmarkapp.com/developer/webhooks/webhooks-overview ; Amazon SES event notifications — https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html ; Mailgun tracking docs — https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/

## Primary risks for AI lead generation/nurture bots

- **Unlawful outreach basis:** scraped/enriched emails without valid consent or legitimate-interest assessment can violate CASL, PECR/GDPR, platform terms, or sector rules.
- **Missing or ineffective opt-out:** AI-generated replies could omit unsubscribe language, ignore natural-language opt-outs, or continue processing a suppressed lead.
- **Vendor/agent accountability:** delegating generation/sending to an AI or email provider does not remove sender liability.
- **Deliverability failure:** no SPF/DKIM/DMARC, high bounce rate, spam complaints, missing one-click unsubscribe, or non-RFC-compliant headers can block campaigns even where content is lawful.
- **Misleading personalization or identity:** generated claims may imply a prior relationship, human-only authorship, false urgency, or unverified facts.
- **Profiling/data protection:** lead scoring, inferred demographics, and enrichment may require notice, minimization, objection handling, and retention controls.
- **Human-review gaps:** "draft-before-send" fails if reviewers lack context, cannot edit, rubber-stamp, or if emergency/follow-up paths bypass the queue.
- **Auditability gaps:** without immutable logs, cannot prove consent source, lawful basis, unsubscribe timing, reviewer approval, or exact content sent.

## Design implications for this repo's future email architecture

- Add a **ComplianceGate** before draft generation and again before send: checks suppression, unsubscribe, bounce/complaint status, jurisdiction, campaign consent/lawful basis, sender domain health, and message classification (commercial vs transactional/relationship).
- Treat **suppression as global and irreversible by default** unless a verified re-subscribe event occurs. Normalize natural-language opt-outs such as "stop", "unsubscribe", "remove me", and "do not contact" from inbound emails.
- Store lead-level compliance fields: `email`, `jurisdiction`, `consent_status`, `consent_source`, `lawful_basis`, `suppressed_at`, `suppression_reason`, `bounce_status`, `complaint_status`, `last_unsubscribe_seen_at`, `retention_delete_at`.
- Store message-level fields: `campaign_id`, `thread_id`, `message_id`, `in_reply_to`, `from_domain`, `commercial_classification`, `unsubscribe_url`, `list_unsubscribe_header`, `postal_address_included`, `reviewer_id`, `approved_at`, `sent_at`, `provider_event_ids`.
- Implement **draft-only AI by default**: model can propose subject/body/next action but cannot call sender directly. Review UI must show retrieved evidence, lead history, compliance flags, risky claims, and required footer/unsubscribe components.
- Add **send blockers** for missing physical address/unsubscribe, deceptive-risk subject, suppressed recipient, unresolved bounce/complaint, missing reviewer approval, stale approval after lead replies, missing consent basis in strict jurisdictions, or high provider spam/bounce thresholds.
- Use **provider event webhooks** to update suppression state for bounces, complaints, unsubscribe clicks, and delivery failures; reconcile with inbound mailbox opt-outs.
- Separate **transactional/service replies from marketing nurture** because legal requirements differ; do not let the model choose category without rule-based validation.
- Minimize/instrument profiling: avoid inferring sensitive attributes; when scoring uses personal data, maintain explanation fields and allow manual override/deletion.
- Build tests around compliance invariants: suppressed leads never produce sendable messages; unsubscribe language is preserved; approvals are required; provider complaint/bounce events block future outreach.

## Integration architecture slice — 2026-06-24

Focus: map the current local chat loop (`LeadNurtureAgent.respond`, `ConversationStore`, observations, lead score/action) onto a minimal future email/CRM adapter without changing the repo's local-first prototype boundary.

### Verified integration facts from current primary sources

- **Inbound email can be normalized into webhook payloads before reaching the agent.** SendGrid's Inbound Parse Webhook docs describe configuring inbound parse to process/parse incoming email; Postmark's inbound processing docs say inbound emails are processed and delivered to the application via webhook in formatted JSON; Mailgun's receiving docs describe receiving messages via HTTP through a route `forward()` action and expose parsed fields such as message body/attachments. Sources: https://www.twilio.com/docs/sendgrid/for-developers/parsing-email/setting-up-the-inbound-parse-webhook ; https://postmarkapp.com/developer/user-guide/inbound ; https://documentation.mailgun.com/docs/mailgun/user-manual/receive-forward-store/receive-http
- **Close is a plausible first CRM adapter target because its developer portal explicitly supports pushing leads, contacts, activities, and custom data into Close via REST API, and syncing data out with webhooks/event log.** This fits the repo's small `leads`, `turns`, and `observations` store better than a full enterprise CRM integration. Source: https://developer.close.com/
- **HubSpot developer docs were reachable but rendered as a JavaScript-heavy/dynamic page from this environment; the static fetch did not expose enough content to verify contact/custom-object details in this run.** Treat HubSpot contact/custom-object mapping as blocked pending manual browser/API-reference validation. Sources attempted: https://developers.hubspot.com/docs/api-reference/crm-contacts-v3/guide ; https://developers.hubspot.com/docs/api-reference/crm-objects-v3/guide ; https://developers.hubspot.com/docs/api/webhooks
- **Salesforce REST API docs were blocked with HTTP 403 from this environment.** Do not make Salesforce object-mapping claims from this run. Source attempted: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm

### Proposed minimal adapter boundary (hypothesis, not yet implemented)

Keep the current agent as the intelligence core and add adapters around it:

```text
Inbound email provider webhook
  -> EmailNormalizer(email provider payload -> clean_body, sender, thread_id, provider_message_id)
  -> IdentityMapper(sender/thread/campaign -> lead_id)
  -> ComplianceGate.pre_draft(lead_id, campaign_id, provider_events, suppression state)
  -> LeadNurtureAgent.respond(lead_id, history, clean_body, company_name)
  -> DraftRecord(reply, next_action, observation, score, retrieved_context, blocked_reasons)
  -> HumanReviewQueue
  -> ComplianceGate.pre_send(approval, required footer/unsubscribe/address, stale-thread check)
  -> Provider sender API only after approval
  -> CRMExporter(summary, score, temperature, next_action, citations, review status)
```

### Minimal local data-model deltas to research before implementation

- `email_identities`: `lead_id`, `email`, `domain`, `crm_contact_id`, `provider`, `created_at`, `last_seen_at`.
- `email_threads`: `thread_id`, `lead_id`, `provider_thread_id`, `campaign_id`, `last_provider_message_id`, `last_inbound_at`, `last_outbound_at`.
- `drafts`: `draft_id`, `lead_id`, `thread_id`, `body`, `subject`, `next_action`, `score_snapshot`, `retrieved_context_ids`, `blocked_reasons`, `created_at`.
- `review_events`: `draft_id`, `reviewer_id`, `decision`, `edited_body_hash`, `approved_at`, `expires_at`.
- `provider_events`: `provider`, `event_id`, `event_type`, `message_id`, `lead_id`, `thread_id`, `received_at`, `raw_json_hash`, `suppression_effect`.
- `crm_exports`: `crm_system`, `crm_object_id`, `lead_id`, `export_type`, `exported_at`, `status`, `error`.

These field names are local design hypotheses. The source-backed requirement is the need to ingest inbound email webhooks/provider events and export lead/contact/activity-like records; exact schemas should be provider-specific once the first integration target is selected.

### Architecture invariants for fixtures/CI

1. A provider complaint, hard bounce, or unsubscribe event must update suppression state before any agent-authored follow-up is considered sendable.
2. `LeadNurtureAgent.respond` may draft language, but no provider send call should be reachable without a fresh human-review approval and a passing `pre_send` gate.
3. CRM export should carry score/action/rationale as advisory intelligence, not as evidence of legal compliance or guaranteed lead quality.
4. Blocked/dynamic CRM docs are integration risk: first adapter should favor the provider with the clearest docs and smallest object surface.

## Methodology backlog items

1. Build a jurisdiction matrix for US CAN-SPAM, Canada CASL, UK PECR/UK GDPR, EU ePrivacy/GDPR, and Australia Spam Act: consent basis, B2B exceptions, opt-out timing, sender identity, address/footer, penalties.
2. Define a consent/lawful-basis data model and fixtures for common acquisition sources: inbound form, webinar signup, customer relationship, purchased list, scraped public email, conference badge scan, CRM import.
3. Create compliance test fixtures in `research/fixtures/` for natural-language unsubscribe, OOO, hard bounce, soft bounce, spam complaint, consent withdrawal, and resubscribe.
4. Evaluate email providers/APIs for webhook support: SendGrid, Postmark, Amazon SES, Mailgun, Gmail/Workspace. Compare bounce/complaint events, suppression APIs, List-Unsubscribe header support, audit logs, and sandboxing.
5. Draft human-review UX requirements: reviewer identity, edit diff, approval expiry, compliance checklist, blocked-send reasons, escalation to legal/admin, and reviewer performance metrics.
6. Add an evaluation suite for AI drafts: hallucinated claims, deceptive subject lines, missing unsubscribe, over-personalization, sensitive inference, unsupported offers/pricing, and tone/brand compliance.
7. Confirm current repo data retention and deletion approach for lead histories, observations, and scoring; add backlog tasks for GDPR/CCPA access/deletion/export workflows if real personal data will be stored.
8. Add deliverability methodology: test domains, SPF/DKIM/DMARC setup checklist, Postmaster/Yahoo complaint metrics, warm-up limits, bounce thresholds, and automatic campaign pause criteria.
9. Legal review trigger list: non-US campaigns, purchased/scraped lists, health/financial/employment/children-related offers, SMS/call expansion, automated eligibility/pricing decisions, or any claim that AI is acting as a human representative.
