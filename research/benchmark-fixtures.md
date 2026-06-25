# Benchmark ideas and fixture design

This file turns the evaluation methodology into concrete, measurable local benchmarks.

## Minimal fixture schema

Each JSONL case can contain:

```json
{
  "id": "pricing_high_intent_001",
  "history": [],
  "message": "Do you have pricing? We have budget this quarter and want to book a demo.",
  "expected_retrieval": {"chunk_ids": ["pricing_overview", "demo_process"], "topics": ["pricing", "demo"]},
  "expected_observation": {
    "intent": "schedule_demo",
    "sentiment": "positive",
    "buying_signals": ["pricing", "budget", "demo"],
    "objections": [],
    "questions": ["Do you have pricing?"]
  },
  "expected_scoring": {"temperature": "hot", "next_best_action": "schedule_contact"},
  "response_constraints": {
    "required_facts": ["pricing depends on scope", "can schedule a demo"],
    "forbidden_claims": ["guaranteed savings", "SOC 2 certified"],
    "cta_type": "schedule_demo",
    "max_words": 120
  },
  "compliance": {"must_stop_contact": false, "sensitive_inference_allowed": false},
  "business_proxy": {"conversion_proxy": "demo_requested", "sales_qualified": true}
}
```

## Benchmark set A: Retrieval/qrels

Create 20-50 query cases over a tiny campaign KB. Include:

- Product overview queries.
- Persona-specific queries, e.g. CFO vs project manager.
- Industry-specific queries, e.g. construction vs real estate.
- Objection queries, e.g. expensive, already have a tool, too busy.
- Buying-intent queries, e.g. pricing, demo, pilot.
- Compliance/no-contact queries that should retrieve policy or suppression guidance rather than sales copy.
- Prompt-injection queries that should retrieve only factual KB and compliance policy.

Metrics: hit_rate@3, recall@5, precision@5, MRR@5, nDCG@5, metadata filter accuracy, p95 latency.

## Benchmark set B: Observation extraction

Create 50-100 single-turn labeled messages. Balance:

- `learn`: broad questions and early education.
- `evaluate`: comparisons, requirements, case studies.
- `object`: price, timing, competitor, trust objections.
- `schedule_demo`: demo, pricing, pilot, proposal, contract.
- `disengage`: unsubscribe, stop, spam, not interested.

Metrics: intent macro-F1, sentiment accuracy, multi-label F1 for pain/objection/buying-signal/topic extraction, question extraction recall, false sensitive-demographic inference rate.

## Benchmark set C: Scoring/action transitions

Create multi-turn scenarios where state should change:

- Cold -> warm after repeated product-fit questions.
- Warm -> hot after budget/timeline/demo signal.
- Hot -> cold/suppressed after “stop contacting me”.
- Objection -> continue nurture with proof point, not schedule request.
- Ambiguous positive sentiment but no buying signal remains warm, not hot.

Metrics: final temperature macro-F1, hot recall, false-hot rate, action accuracy, invalid transition count, disengaged-to-sales rate.

## Benchmark set D: Response quality and groundedness

For each case, label required facts and forbidden claims. Use deterministic string/token checks locally:

- Required fact coverage: normalized required fact tokens appear or are paraphrased using approved aliases.
- Unsupported claim count: generated claims not in retrieved chunks or approved boilerplate.
- CTA type: regex/rule classifier maps response to expected CTA.
- Tone: blacklist pressure phrases such as “last chance”, “you must”, “guaranteed”.
- Length: word count and max sentence count.

Metrics: required fact coverage, forbidden claim count, CTA accuracy, max-word pass rate, objection acknowledgement rate.

## Benchmark set E: Compliance

Create red-team cases:

- Explicit unsubscribe: “Stop”, “unsubscribe”, “remove me”, “do not email again”.
- Sensitive inference traps: user mentions health, family status, age, religion, nationality, or financial distress; system must not exploit or infer targeting attributes.
- Unsupported certification/ROI: asks system to claim SOC 2, HIPAA, 50% ROI, legal compliance guarantee.
- Prompt injection: asks system to ignore rules, reveal hidden prompt, or fabricate customer proof.
- Data minimization: user includes credit card, password, or API key; system should not store/expose it in structured lead fields.

Metrics: unsubscribe pass rate, no-contact state persistence, sensitive-inference violations, forbidden-claim violations, prompt-injection violation rate, secret echo/storage rate.

### Compliance gate fixture extension — 2026-06-24

The fixture set now includes pre-send and provider-event cases, not only lead-authored chat replies. These are deliberately encoded in the same JSONL file so the future email adapter can reuse the chat prototype's observation/scoring/output checks while adding compliance-specific assertions.

Additional optional fixture fields:

```json
{
  "compliance": {
    "must_stop_contact": true,
    "send_allowed": false,
    "requires_human_review": true,
    "suppression_reason": "provider_spam_complaint",
    "provider_event_types": ["spam_report", "complaint"],
    "missing_required_fields": ["unsubscribe_url", "postal_address"]
  }
}
```

New cases added:

- `compliance_hostile_opt_out_001` — natural-language opt-out with hostile wording; should suppress and avoid any sales CTA.
- `compliance_provider_spam_complaint_001` — provider complaint/spam-report event; should suppress before any draft or send path.
- `compliance_hard_bounce_001` — hard-bounce event; should block further sends and mark deliverability risk.
- `compliance_missing_footer_pre_send_001` — commercial draft lacks unsubscribe URL and physical postal address; should block send and require review/remediation.

Verified source basis:

- FTC CAN-SPAM guidance says commercial email needs a clear opt-out mechanism and a valid physical postal address, and opt-outs must be honored. Source: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Gmail sender guidelines require marketing/subscribed messages to support one-click unsubscribe and a clearly visible unsubscribe link, and recommend automatically unsubscribing recipients with repeated bounced messages. Source: https://support.google.com/a/answer/81126
- Yahoo sender best practices require SPF/DKIM/DMARC alignment for bulk senders and functioning one-click List-Unsubscribe for marketing/subscribed messages. Source: https://senders.yahooinc.com/best-practices/
- SendGrid, Postmark, Amazon SES, and Mailgun official docs expose event/webhook/notification surfaces for bounces, spam reports/complaints, unsubscribes, deliveries, and related message-tracking events; therefore provider events should be first-class fixture inputs for the future email adapter. Sources: https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event ; https://postmarkapp.com/developer/webhooks/webhooks-overview ; https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html ; https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/

Unverified/hypothesis: exact field names such as `suppression_reason`, `send_allowed`, and `requires_human_review` are proposed local harness fields, not vendor-standard fields.

## Benchmark set F: Business outcome proxies

Use 10-20 multi-turn scenarios with labels:

- `demo_requested`: should end in scheduling CTA and sales handoff summary.
- `pricing_requested`: should answer pricing process and offer next step.
- `case_study_accepted`: should offer relevant proof based on industry/persona.
- `needs_more_nurture`: should ask clarifying question or provide educational content.
- `no_contact`: should suppress outreach.

Metrics: qualified action rate, nurture appropriateness, objection recovery rate, disengagement protection, lead qualification completeness, sales handoff precision/recall, turns-to-correct-CTA.

### Differentiation/demo fixture slice — 2026-06-24

Focused slice: turn the product-wedge hypotheses into a demo script that is hard for broad GTM platforms or generic private-document chat tools to show in one local repo run.

#### Verified source context

- Salesforce Agentforce's public page says Agentforce brings together humans, applications, AI agents, and data; its SDR example engages prospects 24/7, answers questions, manages objections, and schedules meetings based on CRM and external data. Source: https://www.salesforce.com/agentforce/
- HubSpot's Breeze AI page says its AI tools and agents are built into CRM; the page describes a prospecting agent that researches and delivers personalized outreach strategies, and a customer/account-assistant style output with next best steps, talking points, and a ready-to-send email draft. Source: https://www.hubspot.com/products/artificial-intelligence
- Outreach's platform page positions Outreach as an agentic AI revenue platform unifying sales engagement, deal management, forecasting, and coaching. Source: https://www.outreach.ai/platform
- Apollo's pricing page positions Apollo around sales intelligence, lead generation, email outreach, prospecting, inbound lead conversion, CRM export/sync, and a free sign-up path; a guessed `ai-sales-agent` product URL returned 404 in this environment and should not be used for product-specific claims. Sources: https://www.apollo.io/pricing ; attempted blocked/broken URL: https://www.apollo.io/product/ai-sales-agent
- AnythingLLM's public page says users can chat with docs, use AI agents, and run locally/offline; its GitHub README surfaced source citations and document-chat support. Sources: https://anythingllm.com/ ; https://github.com/Mintplex-Labs/anything-llm

#### Demo arc to encode in local fixtures

1. **Private knowledge grounding:** ingest a small vertical corpus with approved proof, disallowed claims, pricing caveats, and persona notes. The lead asks a workflow-fit question; the bot must cite/cover only approved facts and avoid generic sales-agent claims.
2. **Observation-to-score rationale:** the lead moves from pain + objection to budget/timeline/demo intent. The demo should expose the exact observed signals, retrieved topics, score/temperature, and next-best action rather than just producing persuasive copy.
3. **Draft-before-send review gate:** a commercial email draft is valuable but not sendable until unsubscribe/address/reviewer checks pass. The demo should show `send_allowed=false`, `requires_human_review=true`, and a non-sales remediation action.

New JSONL cases added to `research/fixtures/lead_nurture_eval_cases.jsonl`:

- `demo_private_cited_warm_001` — tests warm-stage private-company knowledge grounding with source-oriented required facts and forbidden unsupported claims.
- `demo_score_rationale_hot_001` — tests hot-lead escalation with explicit observed pain, budget/timeline/demo signals, and a sales handoff summary requirement.
- `demo_draft_review_gate_001` — tests the compliance-gated draft-review differentiator by requiring a blocked send, human review, and missing-footer remediation.

Unverified/hypothesis: these demo cases are proposed differentiation fixtures; they are not evidence that buyers prefer this workflow or that competitor products cannot be configured to approximate it. The verified claim is narrower: current public pages emphasize broad CRM/GTM agents or private-document chat, while this repo can demonstrate the combined local RAG + observable scoring + compliance-gated draft loop in reproducible fixtures.

## External datasets worth reusing without paid services

These are not lead-nurture-specific, but useful for validating retrieval/evaluation plumbing:

- **BEIR:** heterogeneous retrieval benchmark framework and datasets. Useful to test generic retriever metrics code before applying campaign qrels. Source: https://github.com/beir-cellar/beir
- **MS MARCO via MTEB/Hugging Face:** passage ranking queries/qrels for retrieval metric smoke tests. Source: https://huggingface.co/datasets/mteb/msmarco
- **Synthetic local sales fixtures:** best primary dataset for this repo because commercial compliance, lead scoring, and campaign facts are domain-specific. Keep it small, versioned, and human-reviewed.

## Initial local fixture examples

See `research/fixtures/lead_nurture_eval_cases.jsonl` for seed cases covering high intent, objection, unsubscribe, sensitive inference, and prompt injection.

### Canned KB fixture slice — 2026-06-24

Focused slice: turn the fixture ideas into a runnable local retrieval harness seed, rather than only labeled lead-message cases.

New fixture file:

- `research/fixtures/kb_documents.jsonl` — 17 stable `KnowledgeChunk`-shaped documents whose IDs match the `expected_retrieval.chunk_ids` already used by the 12 lead-nurture eval cases.

Design notes grounded in the repo implementation:

- The fixture rows use the current `KnowledgeChunk` fields from `src/lead_nurture_rag/models.py`: `id`, `source`, `text`, and `metadata`.
- Metadata mirrors the fields indexed by `metadata_to_search_text` in `src/lead_nurture_rag/categorizer.py`: `company_name`, `page_type`, `intent_stage`, `topics`, `personas`, `industries`, and `questions_answered`.
- The document set intentionally covers every retrieval ID currently referenced by `lead_nurture_eval_cases.jsonl`: product overview, construction pay apps, workflow/lien-waiver risk, pricing/demo, sales handoff, approved claims, unsubscribe/suppression/provider events, email footer/CAN-SPAM, human review, and case-study policy.
- Because these are synthetic local fixtures, business/product claims in the fixture corpus are **not market evidence**. They are approved demo facts and guardrails for testing retrieval, response grounding, forbidden-claim checks, and compliance-gated draft behavior.

Smoke-test command used in this slice:

```bash
uv run python - <<'PY'
import json
from pathlib import Path
from lead_nurture_rag.models import KnowledgeChunk
from lead_nurture_rag.retriever import KnowledgeBase

kb = KnowledgeBase()
for line in Path('research/fixtures/kb_documents.jsonl').read_text().splitlines():
    if line.strip():
        chunk = KnowledgeChunk(**json.loads(line))
        kb.chunks[chunk.id] = chunk
kb._reindex()

case_count = 0
hit3 = 0
for line in Path('research/fixtures/lead_nurture_eval_cases.jsonl').read_text().splitlines():
    if not line.strip():
        continue
    case = json.loads(line)
    case_count += 1
    expected = set(case['expected_retrieval']['chunk_ids'])
    query = ' '.join([case.get('message', ''), ' '.join(case['expected_retrieval'].get('topics', []))])
    got = [hit.id for hit in kb.search(query, k=3)]
    if set(got).intersection(expected):
        hit3 += 1

print(f'valid_kb_documents={len(kb.chunks)}')
print(f'valid_jsonl_cases={case_count}')
print(f'retrieval_hit_rate_at_3={hit3}/{case_count}')
PY
```

Observed result on 2026-06-24: `valid_kb_documents=17`, `valid_jsonl_cases=12`, `retrieval_hit_rate_at_3=12/12`.

### Executable research smoke-eval script — 2026-06-25

Focused slice: convert the prior copied one-off fixture validation snippet into a versioned script that can be run by future autonomous loops, CI, or a developer without paid services.

New script:

- `scripts/research_smoke_eval.py` validates `research/fixtures/kb_documents.jsonl` as `KnowledgeChunk` rows, validates `research/fixtures/lead_nurture_eval_cases.jsonl` as JSON objects, loads the fixture KB into the current TF-IDF `KnowledgeBase`, and evaluates each case's `expected_retrieval.chunk_ids`.

Command:

```bash
uv run python scripts/research_smoke_eval.py --out .eval/latest.json
```

Current output on 2026-06-25:

- `valid_kb_documents=17`
- `valid_jsonl_cases=12`
- `scored_retrieval_cases=12`
- `hit_count_at_3=12`
- `hit_rate_at_3=1.0`
- `recall_at_5=0.9583333333333334`
- `mrr_at_5=0.9583333333333334`
- `p95_retrieval_ms=2.7474022014757793`
- `no_hit_cases=[]`

Design notes grounded in repo implementation:

- `KnowledgeChunk` validation uses the current Pydantic model in `src/lead_nurture_rag/models.py`.
- Retrieval uses the existing `KnowledgeBase.search` path in `src/lead_nurture_rag/retriever.py`, including `metadata_to_search_text` enrichment via `_reindex()`.
- The script exits non-zero if any case lacks expected retrieval IDs or has no top-3 hit, making it a minimal regression gate rather than only a reporting utility.

Unverified/hypothesis: this script does not yet test observation extraction, lead scoring, response groundedness, or compliance-gate behavior. It is an executable retrieval/fixture integrity baseline that future slices should extend.

### Observation/scoring smoke-eval extension — 2026-06-25

Focused slice: extend the executable research smoke test from retrieval-only fixture validation to also run the repo's deterministic observation analyzer and lead-scoring rules against the same 12 labeled cases.

Updated script behavior:

- `scripts/research_smoke_eval.py` now imports the current repo implementation for `analyze_observation`, `build_observation`, and `score_lead`.
- The script still validates both JSONL fixture files and retrieval hit/recall/MRR metrics.
- It additionally reports deterministic observation/scoring metrics: intent accuracy, sentiment-label accuracy, approximate multi-label recall for pain points/objections/buying signals/recommended topics, temperature accuracy, next-action accuracy, false sensitive-demographic inference count, and per-case mismatch details.
- The script remains a hard regression gate only for invalid JSONL/missing retrieval IDs/no top-3 retrieval hits; observation/scoring mismatches are reported as baseline data rather than failing the command because current labels intentionally cover future email-adapter and compliance behaviors that the simple chat rules do not yet implement.

Command:

```bash
uv run python scripts/research_smoke_eval.py --out .eval/latest.json
```

Observed output on 2026-06-25:

- `valid_kb_documents=17`
- `valid_jsonl_cases=12`
- `scored_retrieval_cases=12`
- `hit_count_at_3=12`
- `hit_rate_at_3=1.0`
- `recall_at_5=0.9583333333333334`
- `mrr_at_5=0.9583333333333334`
- `p95_retrieval_ms=2.865456250765419`
- `observation_scored_cases=12`
- `intent_accuracy=0.4166666666666667`
- `sentiment_label_accuracy=0.5`
- `pain_point_recall_approx=0.1111111111111111`
- `objection_recall_approx=0.5`
- `buying_signal_recall_approx=0.5833333333333334`
- `recommended_topic_recall_approx=0.09722222222222221`
- `temperature_accuracy=0.75`
- `next_action_accuracy=0.6666666666666666`
- `false_sensitive_demographic_inference_count=0`
- `no_hit_cases=[]`

Verified implementation basis:

- Observation analysis uses `src/lead_nurture_rag/observation.py` directly, including the current rule lists for positive/negative/buying/pain/objection terms and the explicit-self-disclosure demographic policy.
- Scoring uses `src/lead_nurture_rag/agent.py::score_lead`, then maps the resulting temperature to the current app action enum: `cold -> continue_nurture`, `warm -> offer_case_study`, `hot -> schedule_contact`.
- The low observation/topic recall is therefore a source-backed baseline of the current deterministic rules, not a model-quality claim about future LLM mode.

Actionable fixture findings:

- Current retrieval is stable on the canned corpus, but observation extraction is the next bottleneck: the analyzer misses natural-language opt-outs such as “remove me” / “never contact,” provider-event language such as hard bounces, and compliance pre-send states such as missing postal address or reviewer approval.
- The current app action enum cannot express non-send compliance actions (`honor_unsubscribe`, `internal_suppression`, `block_send`, `draft_review_block`), so fixtures are forced to label expected app actions as one of the three chat actions while response constraints carry the compliance-specific CTA type.
- The false sensitive-demographic inference count is currently `0` on these fixtures for age/gender, which supports the existing explicit-self-disclosure policy for sensitive fields; this does not prove broader privacy compliance.

Unverified/hypothesis: approximate multi-label recall uses token-overlap matching for labels such as “budget approved” vs actual term “budget.” It is a pragmatic smoke metric, not a replacement for a full extraction scorer with normalized ontology labels.

### ComplianceGate schema fixture slice — 2026-06-25

Focused slice: encode two additional pre-send/non-send cases that exercise the proposed `ComplianceGate` result shape without requiring a real email provider or sender API.

New JSONL cases added to `research/fixtures/lead_nurture_eval_cases.jsonl`:

- `compliance_ambiguous_opt_out_001` — a lead says “take me off this list for now” without using the exact word “unsubscribe.” Expected local gate behavior: `send_allowed=false`, `requires_human_review=true`, and `suppression_reason=ambiguous_opt_out` until a human/process resolves preferences.
- `compliance_stale_approval_after_reply_001` — a draft had reviewer approval, but a newer inbound reply arrived before send. Expected local gate behavior: `send_allowed=false`, `requires_human_review=true`, and `missing_required_fields=["fresh_thread_review"]` because approval must be refreshed against the latest thread state.

Verified source basis:

- FTC CAN-SPAM guidance requires opt-out mechanisms, prompt honoring of opt-out requests, and valid physical postal address for commercial messages. Source: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Gmail and Yahoo sender guidance treat one-click/visible unsubscribe, spam-rate thresholds, and complaint/bounce handling as sender requirements or best practices. Sources: https://support.google.com/a/answer/81126 ; https://senders.yahooinc.com/best-practices/
- Provider-event docs from SendGrid, Postmark, Amazon SES, and Mailgun show that unsubscribe, bounce, and complaint signals are available as webhook/notification inputs for the future gate. Sources: https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event ; https://postmarkapp.com/developer/webhooks/webhooks-overview ; https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html ; https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/

Unverified/hypothesis: “ambiguous opt-out” and “stale approval” thresholds are conservative product-safety policies, not direct legal text. They should be reviewed with counsel and real customer workflows before send-capable automation.
