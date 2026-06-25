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

## 2026-06-24 22:43 EDT — Differentiation and demo strategy fixtures

Focus question: What concrete local demo can show a differentiated lead-nurture intelligence loop rather than a generic sales AI agent, CRM assistant, or private-document chatbot?

New findings:

- Salesforce Agentforce's public page supports the broad enterprise AI-agent contrast: it describes Agentforce as bringing together humans, applications, AI agents, and data; its SDR example engages prospects 24/7, answers questions, manages objections, and schedules meetings based on CRM and external data.
- HubSpot's Breeze AI page supports the CRM-native agent contrast: it describes AI tools/agents built into CRM, a prospecting agent that researches and delivers personalized outreach strategies, and next-best-step/talking-point/ready-to-send email-draft outputs.
- Outreach's platform page supports the revenue-orchestration contrast: it positions Outreach as an agentic AI revenue platform unifying sales engagement, deal management, forecasting, and coaching.
- AnythingLLM remains useful as the private/local RAG contrast: its product page says chat with docs and AI agents can run locally/offline, and the GitHub README surfaced document chat with source citations.
- Apollo's pricing page remained reachable and supports the data/prospecting/email-outreach contrast; a guessed Apollo AI Sales Agent URL returned HTTP 404, so no product-specific claims were made from that URL.

Key sources:

- https://www.salesforce.com/agentforce/
- https://www.hubspot.com/products/artificial-intelligence
- https://www.outreach.ai/platform
- https://www.apollo.io/pricing
- https://www.apollo.io/product/ai-sales-agent — attempted; returned HTTP 404 in this environment.
- https://anythingllm.com/
- https://github.com/Mintplex-Labs/anything-llm

Measurable output produced:

- Added a dated differentiation/demo slice to `research/benchmark-fixtures.md`.
- Added 3 demo-oriented JSONL fixtures to `research/fixtures/lead_nurture_eval_cases.jsonl`: private cited warm lead, hot score-rationale handoff, and compliance-gated draft review.
- Added differentiation/demo sources and the Apollo broken-source note to `research/sources.md`.
- Revalidated `research/fixtures/lead_nurture_eval_cases.jsonl`: 12 valid JSONL cases.

Actionable insights / open questions:

- The demo should show three panes: retrieved private knowledge/citations, observed lead signals with score rationale, and draft/review/compliance state. That is more specific than “AI writes sales email.”
- Keep competitor claims narrow: public pages verify broad positioning, not an absence of configurable score rationales or review gates in every competitor.
- Next implementation question: should the repo add a tiny canned demo corpus so these fixtures can be exercised end-to-end without inventing chunk IDs?

Confidence: Medium-high for cited public positioning and local fixture validity; medium for differentiation because it is a demo hypothesis, not buyer-demand proof. Apollo AI-sales-agent URL is blocked/broken (404).

Next run recommendation: Rotate back to competitive matrix or evaluation harness by adding a minimal canned campaign corpus and a deterministic fixture-runner that checks required/forbidden facts and compliance flags.

## 2026-06-24 23:19 EDT — Evaluation harness canned KB fixture

Focus question: What is the smallest local campaign/policy corpus that lets the existing lead-nurture eval cases exercise retrieval deterministically before a full benchmark runner exists?

New findings:

- The current eval cases already reference 17 expected chunk IDs, but there was no matching canned KB fixture file; retrieval assertions could not be run end-to-end from research fixtures alone.
- The repo's `KnowledgeChunk` model and TF-IDF `KnowledgeBase` are sufficient for a no-service smoke test when a JSONL fixture is loaded directly into `kb.chunks` and indexed with `_reindex()`.
- Mirroring `metadata_to_search_text` fields in the fixture metadata improves retrieval stability because the local retriever indexes both document text and metadata terms.
- A 17-document synthetic BuildCo AI corpus can cover all 12 existing eval cases across product overview, construction pay-app workflow, lien waiver risk, pricing/demo, sales handoff, approved claims, opt-out/suppression, provider events, email footer/CAN-SPAM, human review, and case-study policy.

Key sources:

- https://github.com/carygeo/lead-nurture-rag-bot/blob/main/src/lead_nurture_rag/models.py
- https://github.com/carygeo/lead-nurture-rag-bot/blob/main/src/lead_nurture_rag/retriever.py
- https://github.com/carygeo/lead-nurture-rag-bot/blob/main/src/lead_nurture_rag/categorizer.py
- Local docs reviewed: `docs/lead-scoring-and-observations.md`, `docs/email-integration-roadmap.md`, `research/evaluation-methodology.md`, and `research/benchmark-fixtures.md`.

Measurable output produced:

- Added `research/fixtures/kb_documents.jsonl` with 17 valid JSONL `KnowledgeChunk`-shaped rows.
- Updated `research/benchmark-fixtures.md` with the canned-KB slice, fixture design notes, and smoke-test command.
- Updated `research/README.md` and `research/sources.md` so the fixture inventory and source index mention the canned KB corpus and repo implementation sources.
- Validation result: `valid_kb_documents=17`, `valid_jsonl_cases=12`, `retrieval_hit_rate_at_3=12/12` using the current TF-IDF retriever.

Actionable insights / open questions:

- Add a real `scripts.evaluate` or `scripts/research_smoke_eval.py` next so this validation command becomes versioned executable code rather than a copied one-off snippet.
- Add exact required/forbidden response checks after retrieval smoke tests pass; the canned KB now gives those checks source text to inspect.
- Treat the synthetic BuildCo AI facts as fixture-only demo knowledge, not evidence of a real product, legal compliance, deliverability performance, or buyer demand.

Confidence: High that the JSONL fixture matches current repo model fields and gives 12/12 retrieval hit@3 on existing cases; medium that this remains stable after future chunking/retriever changes because the smoke test loads pre-chunked documents directly.

Next run recommendation: Continue the evaluation-harness slice by committing a tiny executable evaluation script that validates JSONL, checks expected retrieval hit@k, and optionally verifies forbidden/required facts against generated responses.

## 2026-06-24 23:53 EDT — Competitive matrix: AI SDR and conversational engagement

Focus question: How do newer AI-SDR and conversational lead-engagement products position themselves relative to a local-first, source-grounded lead-nurture RAG intelligence layer?

New findings:

- 11x's public home page verifies digital-AI-worker positioning for Sales/RevOps/GTM leaders and exposes outbound/inbound qualification, lead nurture/reactivation, website visitor retargeting, automated meeting scheduling, CRM/Slack/G2 integrations, and API language. Its guessed pricing URL returned 404 in this environment.
- Artisan's public pages verify AI BDR / AI employee positioning: Ava finds and prioritizes high-intent leads, runs campaigns, handles replies/objections, books meetings, and uses human escalation rules. Its pricing page exposed a free-trial/10,000-credit/$300-credit offer, but exact paid plans were not extracted from static text.
- Drift now redirects to Salesloft's Drift platform page; Salesloft public text verifies AI chat agents, “turn website visitors into pipeline,” and revenue-orchestration positioning across sales engagement and revenue intelligence. Exact Salesloft pricing was not extracted.
- Pipedrive's AI Sales Assistant page verifies CRM-native assistant positioning around analyzing actions/past performance, suggesting actions, personalized notifications, and progress updates. Pipedrive pricing was blocked by an “Attention Required”/403-style page.
- 6sense, Lusha, Reply.io, and a guessed Qualified/Piper URL were blocked, Cloudflare-protected, or 404 from this environment; these are logged as blocked-source findings and not used for substantive product claims.

Key sources:

- https://www.11x.ai/
- https://www.artisan.co/ ; https://www.artisan.co/pricing
- https://www.drift.com/products/drift-engage/ ; https://www.salesloft.com/platform/drift ; https://www.salesloft.com/pricing
- https://www.pipedrive.com/en/features/ai-sales-assistant
- Blocked/broken attempts: https://www.11x.ai/pricing ; https://www.6sense.com/platform/revenue-ai/ ; https://www.lusha.com/pricing/ ; https://reply.io/ ; https://reply.io/ai-sales-agents/ ; https://www.qualified.com/products/piper ; https://www.pipedrive.com/en/pricing

Measurable output produced:

- Added a dated AI-SDR/conversational-engagement matrix section to `research/competitive-landscape.md` with category, positioning, pricing/access, AI claims, CRM/email/lead-engagement surfaces, and gap-vs-prototype fields.
- Added corresponding source-index entries and blocked-source notes to `research/sources.md`.
- Revalidated `research/fixtures/lead_nurture_eval_cases.jsonl`: 12 valid JSONL cases.

Actionable insights / open questions:

- Do not position the repo as another autonomous sender or meeting-booker; crowded AI-SDR products already lead with execution automation.
- The clearer differentiator remains an intelligence/review layer: private campaign knowledge ingestion, source citations, observed-signal extraction, explainable temperature scoring, and compliance-gated drafts that can later export to AI-SDR/CRM tools.
- Follow-up should manually validate blocked/dynamic AI-SDR pricing and stable product URLs, especially 6sense, Lusha, Reply.io, and Qualified/Piper, before expanding matrix rows.

Confidence: Medium-high for fetched 11x, Artisan, Salesloft/Drift, and Pipedrive page claims; low for exact pricing and blocked products because several URLs were 403, Cloudflare-protected, dynamic, or 404.

Next run recommendation: Rotate to evaluation harness by adding a tiny executable research smoke-eval script for JSONL validation and retrieval hit@k, using the existing canned KB fixture.

## 2026-06-25 00:26 EDT — Evaluation harness executable smoke test

Focus question: Can the prior one-off JSONL/retrieval validation snippet be turned into a versioned, repeatable research smoke test that future loops and CI can run without paid services?

New findings:

- The repo's current `KnowledgeChunk` Pydantic model is sufficient to validate the canned KB fixture rows before retrieval assertions run.
- The current TF-IDF `KnowledgeBase.search` path can be exercised directly from research fixtures by loading fixture chunks into `kb.chunks` and calling `_reindex()`; this keeps the benchmark grounded in repo behavior instead of a separate mock retriever.
- The existing 12 eval cases and 17 KB chunks remain internally consistent: all 12 cases have expected retrieval IDs and at least one expected top-3 retrieval hit.
- This smoke test is intentionally narrow: it validates fixture integrity and retrieval metrics only, not observation extraction, scoring/action, response groundedness, or compliance gates.

Key sources:

- https://github.com/carygeo/lead-nurture-rag-bot/blob/main/src/lead_nurture_rag/models.py
- https://github.com/carygeo/lead-nurture-rag-bot/blob/main/src/lead_nurture_rag/retriever.py
- https://github.com/carygeo/lead-nurture-rag-bot/blob/main/scripts/research_smoke_eval.py
- Local research docs reviewed: `research/evaluation-methodology.md`, `research/benchmark-fixtures.md`, and fixture files under `research/fixtures/`.

Measurable output produced:

- Added `scripts/research_smoke_eval.py`, a versioned executable that validates both JSONL fixture files, computes `hit_rate_at_3`, `recall_at_5`, `mrr_at_5`, and `p95_retrieval_ms`, optionally writes JSON output, and exits non-zero on missing expected retrieval IDs or top-3 misses.
- Updated `research/README.md` to point the default validation command at the new script.
- Updated `research/benchmark-fixtures.md` with the executable smoke-eval slice, current observed metrics, and limitations.
- Updated `research/sources.md` with the new script as a repo implementation source.
- Validation result from `uv run python scripts/research_smoke_eval.py --out .eval/latest.json`: `valid_kb_documents=17`, `valid_jsonl_cases=12`, `scored_retrieval_cases=12`, `hit_count_at_3=12`, `hit_rate_at_3=1.0`, `recall_at_5=0.9583333333333334`, `mrr_at_5=0.9583333333333334`, `p95_retrieval_ms=2.7474022014757793`, `no_hit_cases=[]`.

Actionable insights / open questions:

- Add a follow-on observation/scoring evaluator that runs the deterministic `LeadNurtureAgent` or observation analyzer against the same cases and reports intent/action accuracy.
- Add response-constraint checks for required facts, forbidden claims, max words, and CTA type; the fixture schema already contains these labels.
- Decide whether future CI should commit benchmark JSON reports, store them as artifacts, or only print them in job logs.

Confidence: High for fixture validity and retrieval smoke metrics because the script uses current repo models/retriever and completed successfully; medium for benchmark stability because TF-IDF ranking can shift when fixture text or metadata changes.

Next run recommendation: Continue the evaluation-harness slice by extending the script to run observation extraction and score/action checks against `expected_observation` and `expected_scoring`, then rotate back to compliance fixtures if unsafe-action failures appear.

## 2026-06-25 01:02 EDT — Evaluation harness observation/scoring baseline

Focus question: Can the executable research smoke test expose the current deterministic observation analyzer and score/action behavior against the existing labeled lead-nurture fixtures, without adding paid services or LLM judges?

New findings:

- The prior retrieval-only smoke test now validates the next pipeline stage by calling the repo's actual `analyze_observation`, `build_observation`, and `score_lead` implementations.
- Retrieval remains stable on the canned corpus: all 12 cases have a top-3 expected hit, with `hit_rate_at_3=1.0`, `recall_at_5=0.9583333333333334`, and `mrr_at_5=0.9583333333333334`.
- The current deterministic observation/scoring rules are much weaker than retrieval on the same fixtures: `intent_accuracy=0.4166666666666667`, `sentiment_label_accuracy=0.5`, approximate `pain_point_recall=0.1111111111111111`, `objection_recall=0.5`, `buying_signal_recall=0.5833333333333334`, `recommended_topic_recall=0.09722222222222221`, `temperature_accuracy=0.75`, and `next_action_accuracy=0.6666666666666666`.
- The analyzer did not infer age/gender on the sensitive-inference fixtures: `false_sensitive_demographic_inference_count=0`. This supports the current explicit-self-disclosure policy for age/gender fields only; it is not a legal/privacy compliance claim.
- The mismatch report shows concrete implementation gaps: natural-language opt-outs such as “remove me” / “never contact,” provider events such as hard bounces/spam complaints, and pre-send compliance states such as missing postal address/reviewer approval are not represented well by the current chat-oriented rules or three-action enum.

Key sources:

- https://github.com/carygeo/lead-nurture-rag-bot/blob/main/src/lead_nurture_rag/observation.py
- https://github.com/carygeo/lead-nurture-rag-bot/blob/main/src/lead_nurture_rag/agent.py
- https://github.com/carygeo/lead-nurture-rag-bot/blob/main/scripts/research_smoke_eval.py
- Local fixture/source docs reviewed: `research/fixtures/lead_nurture_eval_cases.jsonl`, `research/fixtures/kb_documents.jsonl`, `research/evaluation-methodology.md`, and `research/benchmark-fixtures.md`.

Measurable output produced:

- Extended `scripts/research_smoke_eval.py` to report observation/scoring metrics and detailed mismatch records in addition to retrieval metrics.
- Updated `research/benchmark-fixtures.md` with the observation/scoring smoke-eval slice, observed metrics, verified implementation basis, and limitations.
- Updated `research/README.md` and `research/sources.md` so the default validation description and source index reflect the expanded smoke test.
- Validation result from `uv run python scripts/research_smoke_eval.py --out .eval/latest.json`: `valid_kb_documents=17`, `valid_jsonl_cases=12`, `scored_retrieval_cases=12`, `hit_count_at_3=12`, `hit_rate_at_3=1.0`, `recall_at_5=0.9583333333333334`, `mrr_at_5=0.9583333333333334`, `p95_retrieval_ms=2.865456250765419`, `observation_scored_cases=12`, `intent_accuracy=0.4166666666666667`, `sentiment_label_accuracy=0.5`, `temperature_accuracy=0.75`, `next_action_accuracy=0.6666666666666666`, `false_sensitive_demographic_inference_count=0`, `no_hit_cases=[]`.

Actionable insights / open questions:

- Add an explicit compliance/preference detector before sender integration; the current analyzer only treats `unsubscribe`/`stop` as disengagement and misses other opt-out wording and provider-event suppression inputs.
- Add future action states such as `honor_unsubscribe`, `internal_suppression`, `block_send`, and `draft_review_block`, or keep a separate compliance action field so fixtures do not overload the chat-only next-action enum.
- Decide whether to improve rule lists first for deterministic CI baselines or add a normalized ontology layer before measuring extraction F1 more strictly.

Confidence: High for validation metrics because they were generated by the current repo code and JSONL fixtures in this run; medium for approximate multi-label recall because the scorer uses pragmatic token-overlap matching rather than a full ontology-aware evaluator.

Next run recommendation: Rotate to compliance fixtures or integration architecture by designing a minimal `ComplianceGate` result schema/actions that can convert the observed opt-out/provider/pre-send mismatches into typed non-send decisions.

## 2026-06-25 01:34 EDT — ComplianceGate schema and fixtures

Focus question: What minimal typed `ComplianceGate` result schema can convert opt-out/provider/pre-send mismatches into non-send decisions before future email automation is added?

New findings:

- FTC CAN-SPAM guidance supports treating opt-outs and missing physical postal address/opt-out mechanism as pre-send blockers for commercial email; this is a source-backed product guardrail, not a legal-compliance certification.
- Gmail and Yahoo sender guidance make unsubscribe handling and low spam complaint rates operational requirements/best practices; both source pages were reachable in this run, and the proposed gate treats unsubscribe/spam/bounce signals as machine-readable blockers.
- SendGrid, Postmark, Amazon SES, and Mailgun docs were reachable and continue to support first-class provider-event inputs for bounces, complaints/spam reports, unsubscribes, and delivery failures.
- A future gate should emit typed fields separate from the current chat `next_action` enum: `send_allowed`, `draft_allowed`, `requires_human_review`, `compliance_action`, `blocked_reasons`, `suppression_reason`, `missing_required_fields`, `provider_event_types`, and `review_requirements`.
- Added two conservative fixture hypotheses: ambiguous opt-out language should block commercial follow-up until reviewed/suppressed, and reviewer approval should become stale when the thread changes before send.

Key sources:

- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- https://support.google.com/a/answer/81126
- https://senders.yahooinc.com/best-practices/
- https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event
- https://postmarkapp.com/developer/webhooks/webhooks-overview
- https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html
- https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/

Measurable output produced:

- Added a dated `ComplianceGate result schema slice` to `research/email-outreach-compliance-human-review.md`.
- Added a dated `ComplianceGate schema fixture slice` to `research/benchmark-fixtures.md`.
- Added 2 JSONL evaluation cases to `research/fixtures/lead_nurture_eval_cases.jsonl`: `compliance_ambiguous_opt_out_001` and `compliance_stale_approval_after_reply_001`.
- Updated `research/sources.md` with the source set used for the schema/fixture slice.
- Validation result from `uv run python scripts/research_smoke_eval.py --out .eval/latest.json`: `valid_kb_documents=17`, `valid_jsonl_cases=14`, `scored_retrieval_cases=14`, `hit_count_at_3=14`, `hit_rate_at_3=1.0`, `recall_at_5=0.9166666666666666`, `mrr_at_5=0.9642857142857143`, `p95_retrieval_ms=2.478395000252931`, `observation_scored_cases=14`, `intent_accuracy=0.35714285714285715`, `sentiment_label_accuracy=0.5`, `temperature_accuracy=0.7857142857142857`, `next_action_accuracy=0.7142857142857143`, `false_sensitive_demographic_inference_count=0`, `no_hit_cases=[]`.

Actionable insights / open questions:

- Implement `ComplianceGate` as a separate pre-draft/pre-send result rather than overloading `LeadNurtureAgent`'s three chat actions.
- Add hard checks in the smoke-eval script for `send_allowed=false` and `must_stop_contact=true` compliance fixtures once a gate function exists.
- Review the conservative “ambiguous opt-out” and “stale approval” policies with legal/product stakeholders before any sender API integration.

Confidence: High for cited opt-out, footer, spam-rate, and provider-event source availability; medium for the proposed schema and fixture policy thresholds because they are local design hypotheses pending implementation and review.

Next run recommendation: Continue compliance/integration architecture by adding a tiny `ComplianceGate` interface or pseudocode spec that maps the 14 fixtures' `compliance` fields into typed blocker decisions, then extend `scripts/research_smoke_eval.py` with non-failing compliance-gate baseline metrics.

## 2026-06-25 02:19 EDT — ComplianceGate executable invariant baseline

Focus question: Can the research harness turn the proposed `ComplianceGate` schema into deterministic fixture invariants before a real email adapter is implemented?

New findings:

- The current primary source set for opt-out/footer and provider-event guardrails remains reachable from this environment: FTC CAN-SPAM, Gmail sender guidelines, Yahoo sender best practices, SendGrid Event Webhook, Postmark Webhooks, Amazon SES event notifications, and Mailgun tracking docs all returned HTTP 200 in this run.
- A fixture-level invariant check exposed one schema gap in the original `unsubscribe_001` case: it had `must_stop_contact=true` but no explicit `send_allowed=false`. That gap is now fixed with `send_allowed=false` and `suppression_reason="explicit_unsubscribe"`.
- The harness now reports a non-LLM compliance inventory: 14 cases with tracked compliance fields, 8 explicit send-block cases, 5 stop-contact cases, 5 human-review cases, 2 provider-event cases, 3 missing-required-field cases, 2 internal-draft-allowed cases, and 0 invariant violations.
- This is a fixture-consistency baseline, not an application behavior result: no actual `ComplianceGate` implementation exists yet, and no legal compliance or deliverability performance is claimed.

Key sources:

- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- https://support.google.com/a/answer/81126
- https://senders.yahooinc.com/best-practices/
- https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event
- https://postmarkapp.com/developer/webhooks/webhooks-overview
- https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html
- https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/

Measurable output produced:

- Extended `scripts/research_smoke_eval.py` with `evaluate_compliance_fixture_invariants` and fail-fast behavior for contradictory compliance fixture labels.
- Updated `research/fixtures/lead_nurture_eval_cases.jsonl` so `unsubscribe_001` has explicit `send_allowed=false` and `suppression_reason="explicit_unsubscribe"`.
- Added the executable-invariant slice to `research/benchmark-fixtures.md` and `research/email-outreach-compliance-human-review.md`.
- Added the rechecked source set to `research/sources.md`.
- Validation result from `uv run python scripts/research_smoke_eval.py --out .eval/latest.json`: `valid_kb_documents=17`, `valid_jsonl_cases=14`, `scored_retrieval_cases=14`, `hit_count_at_3=14`, `hit_rate_at_3=1.0`, `recall_at_5=0.9166666666666666`, `mrr_at_5=0.9642857142857143`, `p95_retrieval_ms=2.144978750948212`, `observation_scored_cases=14`, `intent_accuracy=0.35714285714285715`, `sentiment_label_accuracy=0.5`, `temperature_accuracy=0.7857142857142857`, `next_action_accuracy=0.7142857142857143`, `false_sensitive_demographic_inference_count=0`, `compliance_fixture_cases=14`, `compliance_send_block_cases=8`, `compliance_fixture_invariant_violations=[]`, `no_hit_cases=[]`.

Actionable insights / open questions:

- Implement a real `ComplianceGate.evaluate_pre_draft` / `evaluate_pre_send` function next and compare returned fields against the now-consistent JSONL labels.
- Keep compliance actions separate from the chat-only `next_action` enum; the harness confirms typed blocker fields are easier to validate than overloading `continue_nurture`.
- Decide whether compliance invariant failures should always fail CI or be reported separately while the adapter is still unimplemented.

Confidence: High for fixture validity and source reachability because the validation command and HTTP checks completed in this run; medium for the proposed invariant thresholds because they are product/engineering guardrails pending legal/product review.

Next run recommendation: Implement a minimal pure-Python `ComplianceGate` module or spec that maps fixture `compliance` inputs into typed gate outputs, then extend the smoke eval to compare actual gate decisions against expected labels.

## 2026-06-25 02:56 EDT — Integration architecture: minimal ComplianceGate implementation

Focus question: Can the proposed compliance-gate fixture schema become a small deterministic `ComplianceGate` implementation that blocks unsafe email sends before a real provider adapter exists?

New findings:

- The current primary source set for opt-out/footer and provider-event guardrails remains reachable from this environment: FTC CAN-SPAM, Gmail sender guidelines, Yahoo sender best practices, SendGrid Event Webhook, Postmark Webhooks, Amazon SES event notifications, and Mailgun tracking docs all returned HTTP 200 at 2026-06-25 02:56 EDT.
- A minimal gate can remain separate from the chat-only `next_action` enum and still cover the current source-backed blocker classes: explicit/ambiguous stop-contact labels, provider spam/bounce/unsubscribe events, missing commercial-email footer/reviewer/fresh-thread fields, and unresolved human review.
- The gate comparison now checks 8 fixtures with explicit `send_allowed` labels: current result is `compliance_gate_send_allowed_accuracy=1.0` and `compliance_gate_mismatches=[]`.
- The implementation is deliberately conservative: ambiguous opt-out plus review maps to `draft_review_block`; provider complaints and hard bounces suppress provider sends and recipient-facing sales drafts; missing footer/reviewer fields can still allow internal remediation drafts while blocking sends.

Key sources:

- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- https://support.google.com/a/answer/81126
- https://senders.yahooinc.com/best-practices/
- https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event
- https://postmarkapp.com/developer/webhooks/webhooks-overview
- https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html
- https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/

Measurable output produced:

- Added `src/lead_nurture_rag/compliance_gate.py` with `ComplianceGateResult`, `ComplianceGate.evaluate_pre_send`, and `ComplianceGate.evaluate_pre_draft`.
- Extended `scripts/research_smoke_eval.py` to compare actual gate decisions to fixture labels via `evaluate_compliance_gate_against_fixtures`.
- Added `tests/test_compliance_gate.py` with four focused unit tests.
- Updated `research/email-outreach-compliance-human-review.md`, `research/benchmark-fixtures.md`, and `research/sources.md` with the implementation slice and source basis.
- Validation result from `uv run python scripts/research_smoke_eval.py --out .eval/latest.json && uv run pytest tests/test_compliance_gate.py`: `valid_kb_documents=17`, `valid_jsonl_cases=14`, `hit_rate_at_3=1.0`, `recall_at_5=0.9166666666666666`, `mrr_at_5=0.9642857142857143`, `compliance_fixture_invariant_violations=[]`, `compliance_gate_checked_cases=8`, `compliance_gate_send_allowed_accuracy=1.0`, `compliance_gate_mismatches=[]`, and 4 compliance-gate unit tests passed.

Actionable insights / open questions:

- Wire `ComplianceGate` into a future email normalizer/draft endpoint before adding any provider send API; do not let lead temperature or LLM output override `send_allowed=false`.
- Add raw provider webhook fixtures next so SendGrid/Postmark/Mailgun/SES event payloads normalize into the current `compliance` dictionary before gate evaluation.
- Decide whether ambiguous opt-out should always suppress immediately or permit an internal reviewer-only clarification path; current behavior is conservative but still a product/legal policy hypothesis.

Confidence: High for fixture validity and deterministic gate metrics because the smoke eval and unit tests passed; high for cited source reachability; medium for exact gate thresholds and enum names because they are implementation hypotheses pending product/legal review. No legal compliance or deliverability performance is claimed.

Next run recommendation: Rotate to integration architecture by adding raw provider-event JSONL fixtures plus a normalizer spec/table that maps SendGrid/Postmark/Mailgun/SES bounce, complaint, and unsubscribe events into `ComplianceGate` inputs.
