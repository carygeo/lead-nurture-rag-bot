# Lead Nurture RAG Bot Research

This folder turns the repo's lead-generation concept into an auditable research program.

## North star

Validate whether a small, local-first RAG prototype can become a defensible **lead nurture intelligence engine**: company knowledge ingestion -> retrieval -> observation analysis -> cold/warm/hot scoring -> next-best nurture response -> later email/CRM integration.

## Research question

What combination of local/private knowledge ingestion, explainable observation scoring, stage-appropriate response generation, compliance guardrails, and email/CRM integration would make a lightweight lead-nurture RAG bot useful enough for founder-led sales, consultants/agencies, or privacy-conscious B2B teams before adopting a full sales-engagement platform?

## Current artifacts

- `program.md` — autonomous 6-hour research loop instructions.
- `research-log.md` — append-only session summaries and evidence trail.
- `competitive-landscape.md` — initial competitor scan across AI lead gen, sales engagement, CRM AI, and local RAG tools.
- `evaluation-methodology.md` — local-first metrics and benchmark plan.
- `benchmark-fixtures.md` — fixture design for offline evaluation.
- `email-outreach-compliance-human-review.md` — compliance and human-review constraints for future email mode.
- `sources.md` — curated source index.
- `open-questions.md` — unresolved product, market, technical, compliance, and methodology questions.
- `fixtures/lead_nurture_eval_cases.jsonl` — seed benchmark cases.

## Initial measurable baselines

- Fixture inventory: `research/fixtures/lead_nurture_eval_cases.jsonl` contains seed cases for high-intent, objection, unsubscribe, sensitive inference, and prompt-injection scenarios.
- Evaluation dimensions: retrieval, observation extraction, lead score/action, response groundedness, compliance, and business-outcome proxies.
- Evidence standard: primary/company/docs sources first; mark blocked, dynamic, or quote-only pages explicitly.

## Suggested validation command

```bash
python3 - <<'PY'
import json
from pathlib import Path
path = Path('research/fixtures/lead_nurture_eval_cases.jsonl')
count = 0
for line_no, line in enumerate(path.read_text().splitlines(), 1):
    if not line.strip():
        continue
    json.loads(line)
    count += 1
print(f'valid_jsonl_cases={count}')
PY
```

## Relationship to existing docs

This research program is intentionally driven by the product architecture already documented in `docs/`:

- Chat prototype is the test surface.
- Every inbound message is an observation.
- Lead scoring and next action are measurable outputs.
- Future email mode must be draft-first, compliance-gated, and human-reviewable.
