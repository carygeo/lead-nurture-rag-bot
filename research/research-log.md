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
