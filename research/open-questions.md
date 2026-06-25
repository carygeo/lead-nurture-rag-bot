# Open Questions

## Product and market

1. Which early customer segment values local/private knowledge grounding most: founder-led sales, consultants/agencies, vertical B2B sellers, or teams with sensitive sales enablement docs?
2. Is the strongest wedge a standalone chat/review tool, an API layer, or a plugin for an existing CRM/sales-engagement platform?
3. What proof would convince users that explainable cold/warm/hot scoring is better than generic CRM lead scoring?
4. Do buyers care about local-first/private mode enough to trade off built-in contact databases and mature sequence tooling?
5. Which vertical should supply the first high-quality demo corpus: construction, professional services, B2B SaaS, or local businesses?

### Product wedge and customer discovery slice — 2026-06-24

Focus: turn the integration-architecture finding into customer-discovery hypotheses for the first wedge. This section is not evidence of demand; it is a source-backed interview plan and falsifiable positioning test.

#### Verified context from current primary sources

- Apollo positions around prospecting, inbound lead qualification, enrichment, deal execution, AI assistant, CRM/export workflows, and a free sign-up path. Its pricing page frames the product as a sales-intelligence platform that can turn prospecting hours into minutes and qualify/act on inbound leads in seconds. Source: https://www.apollo.io/pricing
- Close positions as a CRM with email, calling, SMS, workflows, lead pipeline management, API/event-log access, and Chloe AI sales agent. Its pricing page says it is trusted by 11,500+ businesses and supports importing from other CRMs/spreadsheets/manual entry. Source: https://close.com/pricing
- HubSpot's current public site text surfaced “Smart CRM,” small-business/startup packaging, Breeze AI agents, and an AI prospecting agent, but the attempted `state-of-sales` URL returned HTTP 404 from this environment; use HubSpot only as general market context until a stable report/product URL is validated. Attempted source: https://www.hubspot.com/state-of-sales
- AnythingLLM's public page is direct evidence that local/private knowledge AI can be packaged for non-developers: it says the desktop app can chat with docs locally/offline, use local or cloud LLMs, and that locally running defaults mean “Nothing is shared unless you allow it.” Source: https://anythingllm.com/
- Y Combinator's startup library was reachable and includes repeated “talk to users” material, but the previously known direct article URL returned 404; treat the library as methodology background and do not cite the broken slug as a stable source. Reachable index: https://www.ycombinator.com/library ; blocked/broken slug: https://www.ycombinator.com/library/6g-how-to-talk-to-users

#### Wedge hypotheses to test, not yet verified

1. **Draft-review intelligence wedge:** founder-led sales teams may want “tell me what to say next and why” before they want another automated sender. This repo can test that with local RAG citations, cold/warm/hot rationale, and human-review draft output.
2. **Privacy-sensitive enablement wedge:** consultants/agencies and niche B2B sellers may hesitate to upload proprietary offer notes, client examples, pricing rationale, or compliance caveats into a generic SaaS sales assistant. Local/offline RAG could matter if the interviewee has genuinely sensitive enablement material.
3. **Vertical-demo wedge:** a narrow construction/professional-services corpus may be more convincing than a generic SaaS demo because the observation/scoring loop can use persona-specific objections, buying triggers, and proof assets.
4. **CRM-light wedge:** teams already using a CRM may prefer advisory exports (`score`, `temperature`, `next_action`, `rationale`, `review_status`) over a replacement CRM. Teams without CRM discipline may prefer a simple review queue and CSV/export workflow first.

#### Interview questions for the next 5-7 discovery calls

1. Walk me through the last time a cold or lukewarm inbound/outbound reply needed a thoughtful follow-up. What sources did you check before replying?
2. Where do your best sales answers live today: website, docs, pitch deck, founder notes, customer calls, Slack, CRM notes, or in someone's head?
3. What makes a lead “hot” in your actual workflow? Which signals are decisive versus merely encouraging?
4. What information would you not want to paste into a cloud sales assistant? Is local/private mode a must-have, nice-to-have, or irrelevant?
5. Would a cited draft plus score rationale save time even if it never sent automatically? What would make you trust or distrust it?
6. Where should the first useful output land: review inbox, CRM note/task, email draft, Slack alert, CSV, or API?
7. What compliance, brand, or approval rule would force a human to review every generated nurture message?
8. If the tool were wrong, which failure would be most costly: false-hot handoff, missed hot lead, hallucinated claim, ignored opt-out, off-brand tone, or sensitive-data leakage?

#### Evidence to collect before claiming demand

- At least 5 interviews with named segment tags and documented current workflow.
- A ranked list of lead-warming signals from users, compared with the repo's current `cold`/`warm`/`hot` rubric.
- Two real or sanitized knowledge corpora that can be ingested locally and used in fixture scenarios.
- A willingness-to-pay signal: time saved per week, existing tool spend, or concrete pilot commitment.
- Explicit trade-off data: whether users would sacrifice contact-database breadth or automated sending for local/private, cited draft intelligence.

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
