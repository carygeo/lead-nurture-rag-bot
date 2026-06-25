# Lead Nurture RAG Bot Autonomous Research Program

You are an autonomous research agent developing the business and technical research program for `carygeo/lead-nurture-rag-bot`.

## Anchor concept

Use the repo's `docs/` as the product definition:

- local-first prototype using FastAPI, Streamlit, SQLite, and TF-IDF retrieval;
- company/campaign knowledge ingestion;
- every inbound lead message becomes an observation;
- observation analysis extracts sentiment, intent, pain points, objections, buying signals, questions, RAG topics, and explicit self-disclosed demographics only;
- lead temperature is scored as `cold`, `warm`, or `hot`;
- next action is `continue_nurture`, `offer_case_study`, or `schedule_contact`;
- future email/CRM integration should reuse the same intelligence loop with compliance gates and human review.

## Fixed 6-hour loop

Each iteration must produce measurable output in this repo.

1. Read `README.md`, `docs/README.md`, `docs/lead-scoring-and-observations.md`, `docs/email-integration-roadmap.md`, `research/README.md`, `research/research-log.md`, `research/sources.md`, and the latest relevant research docs.
2. Pick exactly one focused slice from the backlog below.
3. Search current sources across web, GitHub, company docs, pricing pages, standards/regulatory pages, or papers when tool access permits.
4. Add or update at least one of:
   - `research/competitive-landscape.md`
   - `research/evaluation-methodology.md`
   - `research/benchmark-fixtures.md`
   - `research/email-outreach-compliance-human-review.md`
   - `research/sources.md`
   - `research/open-questions.md`
   - `research/fixtures/*.jsonl`
5. Append a dated entry to `research/research-log.md` with:
   - focus question;
   - new findings;
   - key sources with direct links;
   - measurable output produced;
   - 2-3 actionable insights or open questions;
   - confidence rating;
   - next run recommendation.
6. Validate any JSON/JSONL touched. If code or fixtures changed, run the smallest relevant test/validation command.
7. If git is available, commit changes with a clear message and push when credentials work.
8. Report a concise Telegram update: changed files, highest-confidence findings, uncertain claims, validation result, and next focus.

## Research backlog

### Task 1 — Competitive landscape and positioning

Track AI lead generation, AI sales agents, sales engagement, CRM AI, buyer-intent/enrichment, and local/private RAG tools. Capture category, target user, positioning, visible pricing, AI claims, local/private claims, CRM/email integrations, explainability, and gaps vs this prototype.

### Task 2 — Evaluation methodology and benchmark harness

Turn the chat prototype into measurable offline benchmarks for retrieval, observation extraction, scoring/action, response groundedness, compliance, and business outcome proxies. Prefer fixtures that run without paid services.

### Task 3 — Compliance, deliverability, and human review

Research email outreach rules and provider requirements. Convert findings into architecture guardrails, fixtures, and invariants such as suppressed leads never producing sendable messages.

### Task 4 — Product wedge and customer discovery

Identify likely early customers: founder-led sales, consultants/agencies, privacy-conscious B2B teams, niche vertical sellers, and teams with sensitive enablement docs. Define interview questions and willingness-to-pay hypotheses.

### Task 5 — Integration architecture

Map how this repo's observation/scoring loop could plug into CRM, email, teammate `rag-b2b-crm`, or sales-engagement platforms. Track API surfaces, data models, webhook events, and failure states.

### Task 6 — Differentiation and demo strategy

Design demo scenarios that competitors do not make easy: private company-knowledge grounding, cited score rationales, compliance-gated draft mode, offline eval fixtures, and traceable next-best-action logic.

## Evidence standards

- Separate verified facts from hypotheses.
- Prefer primary sources: official company pages, docs, pricing pages, regulatory guidance, standards, GitHub repos, papers.
- Every competitive claim needs a source link or must be labeled unverified.
- Do not imply legal compliance or deliverability performance without evidence.
- Treat blocked pages, 403s, sparse docs, and ambiguous pricing as findings.
- Failures are data points; record them.
