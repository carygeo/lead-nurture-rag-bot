# Open Questions

## Product and market

1. Which early customer segment values local/private knowledge grounding most: founder-led sales, consultants/agencies, vertical B2B sellers, or teams with sensitive sales enablement docs?
2. Is the strongest wedge a standalone chat/review tool, an API layer, or a plugin for an existing CRM/sales-engagement platform?
3. What proof would convince users that explainable cold/warm/hot scoring is better than generic CRM lead scoring?
4. Do buyers care about local-first/private mode enough to trade off built-in contact databases and mature sequence tooling?
5. Which vertical should supply the first high-quality demo corpus: construction, professional services, B2B SaaS, or local businesses?

## Evaluation methodology

1. What is the minimum fixture set that catches regressions in retrieval, observation extraction, score/action, response quality, and compliance?
2. Should the first benchmark be fully deterministic, LLM-judged, or hybrid?
3. How should scoring metrics be cost-weighted so false-hot sales handoffs and missed unsubscribe requests are penalized more than minor temperature disagreements?
4. What user-facing explanation standard is sufficient for a score rationale?
5. How should benchmark cases encode source-grounded required facts versus optional personalization?

## Compliance and operations

1. Which jurisdictions are in scope for the first email prototype?
2. What consent/lawful-basis fields must exist before any send-capable adapter is merged?
3. How should natural-language opt-out detection be evaluated across terse, ambiguous, and hostile replies?
4. What approval expiry and reviewer identity requirements are needed for draft-before-send mode?
5. Which provider events must be stored before scaling outbound volume: bounces, complaints, delivery failures, unsubscribe clicks, replies, and spam-rate warnings?

## Technical architecture

1. When does TF-IDF become insufficient compared with embeddings/vector DBs for lead-nurture retrieval?
2. What data model lets observation/scoring plug into teammate `rag-b2b-crm` without forcing this repo to adopt its whole stack?
3. How should prompt injection from lead messages be isolated from company knowledge and system instructions?
4. What is the clean interface for replacing deterministic fallback responses with LLM responses while preserving tests?
5. How should evaluation reports be generated and surfaced in CI?
6. Which first integration target has the lowest-risk object surface for the prototype: Close lead/contact/activity export, Postmark/SendGrid inbound-email draft queue, or HubSpot custom-object sync after manual docs validation?
7. What minimal provider-event table fields are enough to make suppression decisions auditable without storing unnecessary raw email content?
