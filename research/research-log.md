# Research log

## 2026-06-24 20:22 EDT — Evaluation methodology and benchmark plan

Task: Research evaluation methodology and metrics for lead-nurture RAG systems, with measurable local benchmarks and source URLs.

Actions:

- Reviewed the repo concept and existing README/docs for a local FastAPI/Streamlit/SQLite/TF-IDF lead-nurture RAG prototype.
- Verified source URLs for RAG/RAG evaluation, retrieval metrics, compliance, and rubric inspiration.
- Created research methodology notes focused on no-paid-service local evaluation.
- Added seed JSONL evaluation cases for retrieval, observation extraction, scoring/action, response constraints, compliance, and business outcome proxies.

Key findings:

- RAG evaluation should be decomposed into retrieval, grounded response quality, and answer relevance/faithfulness; RAGAS, TruLens, and DeepEval provide useful metric categories, but the local prototype can approximate them with qrels, required facts, forbidden claims, and deterministic rubric checks.
- Retrieval should use standard IR metrics: hit rate, recall@k, precision@k, MRR, nDCG, MAP/average precision, metadata accuracy, and latency.
- Observation extraction is a classification + multi-label extraction problem: macro-F1, per-label precision/recall/F1, evidence coverage, question extraction recall, and sensitive-demographic false inference rate.
- Lead scoring/action evaluation needs cost-sensitive checks: hot lead recall, false-hot rate, action accuracy, invalid transitions, and zero tolerance for routing unsubscribed leads to sales.
- Compliance fixtures should be included in CI, especially unsubscribe/stop, CAN-SPAM-like email constraints, sensitive inference, unsupported claims, prompt injection, and data minimization.
- Business outcome proxies can be tested offline with scenario labels such as demo requested, pricing requested, case-study accepted, needs more nurture, and no contact.

Sources:

- https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/
- https://www.trulens.org/getting_started/core_concepts/rag_triad/
- https://deepeval.com/docs/metrics-introduction
- https://deepeval.com/docs/metrics-ragas
- https://github.com/beir-cellar/beir
- https://huggingface.co/datasets/mteb/msmarco
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html
- https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall
- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- https://oag.ca.gov/privacy/ccpa
- https://gdpr.eu/email-encryption/
- https://www.nngroup.com/articles/ten-usability-heuristics/

Files created:

- `research/evaluation-methodology.md`
- `research/benchmark-fixtures.md`
- `research/fixtures/lead_nurture_eval_cases.jsonl`
- `research/research-log.md`


## 2026-06-24 20:23 EDT — Competitive landscape baseline

Focus question: Where does a local-first lead-nurture RAG bot fit relative to AI lead-generation, sales-engagement, CRM AI, and local/private RAG tools?

New findings:

- Sales intelligence and GTM platforms such as Apollo, Clay, ZoomInfo, Cognism, Seamless.AI, Demandbase, Common Room, and Unify emphasize data breadth, enrichment, intent signals, workflows, and CRM sync.
- Sales engagement tools such as Outreach, Salesloft, Regie.ai, Instantly, Smartlead, and lemlist emphasize sequencing, deliverability, multichannel outreach, AI agents, and sales workflow execution.
- CRM-native AI tools such as Salesforce, HubSpot, and Close own system-of-record workflows and can add AI inside existing sales operations.
- Local/private RAG tools such as Onyx, AnythingLLM, and PrivateGPT are strong on private knowledge ingestion but are not visibly specialized around lead observation scoring and next-best nurture responses.

Measurable output produced:

- Added `research/competitive-landscape.md`.
- Added competitor categories, verified source URLs, visible pricing where static pages exposed it, and blocked/dynamic-pricing follow-up notes.

Key sources:

- https://www.apollo.io/pricing
- https://www.clay.com/pricing
- https://www.commonroom.io/pricing/
- https://instantly.ai/pricing
- https://www.lemlist.com/pricing
- https://onyx.app/pricing
- https://anythingllm.com/

Actionable insights / open questions:

- Position this repo as a knowledge-grounded scoring and response brain, not a replacement for Apollo/Clay data or Outreach/Salesloft orchestration.
- The local/private angle likely matters most to founder-led sales, consultants/agencies, and privacy-conscious teams; this is a customer-discovery hypothesis, not proven.
- Future research should manually validate dynamic/blocked pricing pages and CRM marketplaces.

Confidence: Medium-high for category positioning from primary sources; medium for exact pricing because several pages are dynamic, quote-only, blocked, or partially extracted.

Next run recommendation: Build a competitor matrix with fields for AI claims, private/local claims, explainability, integrations, deployment, and gaps vs prototype.

## 2026-06-24 20:28 EDT — Email compliance and human-review baseline

Focus question: What constraints should shape a future email-based nurture adapter for this RAG bot?

New findings:

- US CAN-SPAM requires accurate headers, non-deceptive subject lines, physical postal address, opt-out, honoring opt-outs within 10 business days, and sender responsibility for vendors/agents.
- Gmail/Yahoo bulk sender requirements make authentication, low spam rate, one-click unsubscribe, visible unsubscribe links, bounce handling, and complaint monitoring product requirements rather than optional ops details.
- UK PECR, GDPR direct-marketing objection/profiling rights, CASL, and SMS/call consent rules add jurisdiction and channel-specific risk.
- Draft-before-send with human review should be the first email mode; send-capable automation needs hard blockers for suppression, complaints, missing unsubscribe/address, missing approval, and jurisdictional consent gaps.

Measurable output produced:

- Added `research/email-outreach-compliance-human-review.md`.
- Added compliance backlog items and design implications for `ComplianceGate`, suppression state, reviewer IDs, approval timestamps, provider events, and invariants.

Key sources:

- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- https://support.google.com/a/answer/81126
- https://senders.yahooinc.com/best-practices/
- https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/electronic-and-telephone-marketing/electronic-mail-marketing/
- https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
- https://ised-isde.canada.ca/site/canada-anti-spam-legislation/en

Actionable insights / open questions:

- Add fixture cases proving suppressed/unsubscribed leads never produce sendable messages.
- Add compliance fields to future lead/message models before any sender API integration.
- Define first-jurisdiction scope before testing real outbound flows.

Confidence: High for cited regulatory/provider constraints; medium for architecture details because they require product/legal review before implementation.

Next run recommendation: Convert compliance findings into JSONL fixtures and model invariants that CI can enforce.

## 2026-06-24 21:00 EDT — Compliance fixtures and provider-event guardrails

Focus question: How should the offline benchmark fixtures encode email compliance blockers, provider events, and pre-send human-review gates for the future email adapter?

New findings:

- Verified current access to FTC CAN-SPAM, Gmail sender guidelines, Yahoo sender best practices, and major provider webhook/notification docs. None were blocked in this run.
- Provider events are compliance inputs, not merely analytics: SendGrid, Postmark, Amazon SES, and Mailgun official docs expose webhook/notification/event surfaces for bounces, complaints/spam reports, unsubscribes, delivery failures, and related events.
- A future email adapter should run compliance checks before draft generation and again before send; provider spam complaints and hard bounces should update suppression state before any model-authored follow-up is allowed.
- Fixture schema needs explicit local assertions such as `send_allowed`, `suppression_reason`, `requires_human_review`, `provider_event_types`, and `missing_required_fields` so CI can fail on unsafe sendability, not just poor chat quality.

Key sources:

- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- https://support.google.com/a/answer/81126
- https://senders.yahooinc.com/best-practices/
- https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event
- https://postmarkapp.com/developer/webhooks/webhooks-overview
- https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html
- https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/

Measurable output produced:

- Added 4 compliance-focused JSONL cases to `research/fixtures/lead_nurture_eval_cases.jsonl` for hostile opt-out, provider spam complaint, hard bounce, and missing unsubscribe/postal-address pre-send blocker.
- Documented the compliance-gate fixture extension in `research/benchmark-fixtures.md`.
- Added provider-event sources to `research/sources.md`.
- Added provider-event compliance finding to `research/email-outreach-compliance-human-review.md`.

Actionable insights / open questions:

- Add a real `ComplianceGate` interface before sender integration; it should return typed blocked-send reasons, not just free-text warnings.
- The current app action enum only has `continue_nurture`, `offer_case_study`, and `schedule_contact`; future email mode likely needs explicit non-send actions such as `honor_unsubscribe`, `block_send`, and `internal_suppression`.
- Confirm which provider API will be first so event names and payload fields can move from proposed harness fields to concrete adapter fixtures.

Confidence: High for verified source availability and provider-event categories; medium for proposed fixture field names because they are local design hypotheses pending implementation.

Next run recommendation: Focus on integration architecture by mapping a minimal `ComplianceGate` + email provider webhook adapter data model onto the current SQLite/agent loop.

## 2026-06-24 21:34 EDT — Integration architecture adapter boundary

Focus question: What is the smallest source-backed email/CRM integration boundary that preserves the repo's local-first observation/scoring loop while adding compliance gates and human review?

New findings:

- SendGrid, Postmark, and Mailgun official docs support a provider-webhook normalization pattern for inbound email replies before calling the current `LeadNurtureAgent.respond` loop.
- Close's developer portal explicitly describes pushing leads, contacts, activities, and custom data via REST API, and syncing data out with webhooks/event log; this makes Close a comparatively small CRM export target for a first adapter hypothesis.
- HubSpot docs were reachable but dynamic/static extraction did not expose enough details in this run; HubSpot mapping remains blocked pending manual browser or API-reference validation.
- Salesforce REST API docs returned HTTP 403 from this environment, so no Salesforce object-mapping claims were made.

Key sources:

- https://www.twilio.com/docs/sendgrid/for-developers/parsing-email/setting-up-the-inbound-parse-webhook
- https://postmarkapp.com/developer/user-guide/inbound
- https://documentation.mailgun.com/docs/mailgun/user-manual/receive-forward-store/receive-http
- https://developer.close.com/
- https://developers.hubspot.com/docs/api-reference/crm-contacts-v3/guide
- https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm

Measurable output produced:

- Added an integration architecture slice to `research/email-outreach-compliance-human-review.md` with a proposed adapter boundary, local data-model deltas, and CI invariants.
- Added email/CRM integration sources and blocked-source notes to `research/sources.md`.
- Added two integration-focused technical open questions to `research/open-questions.md`.

Actionable insights / open questions:

- Build the first implementation as provider inbound webhook -> normalizer -> compliance gate -> draft queue, not provider send automation.
- Prefer a narrow CRM export (`score`, `temperature`, `next_action`, `rationale`, `review_status`) before two-way CRM sync.
- Manually validate HubSpot/Salesforce docs in a browser before committing to object mappings or marketplace positioning.

Confidence: Medium-high for inbound email provider webhook pattern and Close API use-case fit from primary docs; low for HubSpot/Salesforce mappings because current access was dynamic/blocked.

Next run recommendation: Rotate to product wedge/customer discovery and turn the integration finding into 5-7 interview questions about whether founders want a draft queue, CRM export, or send-capable automation first.

## 2026-06-24 22:09 EDT — Product wedge and customer discovery interview plan

Focus question: Which early wedge should this local-first lead-nurture RAG bot test first, and what customer-discovery questions can falsify it?

New findings:

- Apollo's current pricing/product page continues to support the “data-first GTM platform” contrast: public text emphasizes sales intelligence, prospecting, inbound qualification, enrichment, deal execution, AI assistant, CRM/export workflows, and free sign-up.
- Close's current pricing/product page supports the “CRM/action workspace” contrast: public text emphasizes CRM, calling/email/SMS, workflows, lead pipeline management, Chloe AI sales agent, imports, API/event-log access, and a claim of 11,500+ businesses.
- AnythingLLM's current product page supports the existence of a local/offline/private knowledge-AI packaging pattern for non-developers, including local/offline document chat and locally running defaults where nothing is shared unless allowed.
- HubSpot's attempted `state-of-sales` URL returned HTTP 404/static fallback from this environment; static fallback text exposed general HubSpot product navigation for Smart CRM, Breeze AI agents, small-business/startup packaging, and AI prospecting, but no report-specific claim should be made from this run.
- YC's startup library index was reachable and contains “talk to users” material, but a previously known direct “how to talk to users” slug returned 404; logged as a broken-source finding.

Key sources:

- https://www.apollo.io/pricing
- https://close.com/pricing
- https://anythingllm.com/
- https://www.hubspot.com/state-of-sales
- https://www.ycombinator.com/library
- https://www.ycombinator.com/library/6g-how-to-talk-to-users

Measurable output produced:

- Added a dated product-wedge/customer-discovery slice to `research/open-questions.md`.
- Added source-index entries and blocked-source notes to `research/sources.md`.
- Produced 4 falsifiable wedge hypotheses and 8 interview questions focused on draft-review intelligence, privacy-sensitive enablement, vertical demos, and CRM-light outputs.
- Revalidated `research/fixtures/lead_nurture_eval_cases.jsonl`: 9 valid JSONL cases.

Actionable insights / open questions:

- Test the first wedge as “cited draft + score rationale + human review,” not automatic sending; this aligns with the repo's current local chat/scoring loop and compliance research.
- Ask users to rank costly failure modes before implementing more integrations; false-hot handoff, missed hot lead, hallucinated claims, ignored opt-outs, and sensitive-data leakage imply different eval priorities.
- Demand remains unverified until at least 5 interviews document current workflows, sensitive-knowledge constraints, and willingness-to-pay/time-saved signals.

Confidence: Medium for competitive/context facts from current primary pages; low-to-medium for wedge hypotheses because they are product-discovery assumptions pending interviews. HubSpot report-specific and YC direct-article claims are blocked/broken.

Next run recommendation: Rotate to differentiation/demo strategy by turning the product-wedge hypotheses into one concrete demo script and fixture additions for a cited, draft-before-send review queue.
