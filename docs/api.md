# API reference

The API is served by FastAPI from `lead_nurture_rag.app:app`.

Run locally:

```bash
uv run uvicorn lead_nurture_rag.app:app --reload
```

Base URL:

```text
http://localhost:8000
```

FastAPI also exposes interactive docs at:

```text
http://localhost:8000/docs
```

## `GET /health`

Returns service status and current knowledge chunk count.

```bash
curl http://localhost:8000/health
```

Example response:

```json
{
  "ok": true,
  "chunks": 4
}
```

## `POST /ingest/text`

Adds manually supplied company, product, offer, or FAQ text to the knowledge base.

```bash
curl -X POST http://localhost:8000/ingest/text \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "company-profile",
    "text": "BuildCo AI validates subcontractor payment applications and detects missing lien waivers."
  }'
```

Request body:

```json
{
  "source": "company-profile",
  "text": "Knowledge text to chunk and index."
}
```

Response:

```json
{
  "chunk_ids": ["chunk_abc123..."],
  "chunks_total": 1
}
```

## `POST /ingest/url`

Fetches a single URL, extracts page text, chunks it, and adds it to the knowledge base.

```bash
curl -X POST http://localhost:8000/ingest/url \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com/solutions"}'
```

Request body:

```json
{
  "url": "https://example.com/solutions"
}
```

Response:

```json
{
  "chunk_ids": ["chunk_abc123..."],
  "chunks_total": 8
}
```

## `POST /ingest/campaign`

Crawls a campaign website from configured seed pages.

```bash
curl -X POST http://localhost:8000/ingest/campaign \
  -H 'Content-Type: application/json' \
  -d @campaigns/example.json
```

Example body:

```json
{
  "company_name": "Example Construction AI",
  "root_url": "https://example.com",
  "allowed_domains": ["example.com"],
  "seed_pages": ["https://example.com", "https://example.com/solutions"],
  "crawl_depth": 1,
  "max_pages": 10,
  "target_persona": "construction project teams",
  "offer": "AI payment application validation"
}
```

Response includes crawled page metadata:

```json
{
  "company_name": "Example Construction AI",
  "pages_crawled": 2,
  "chunk_ids": ["chunk_abc123..."],
  "chunks_total": 12,
  "pages": [
    {
      "url": "https://example.com/solutions",
      "title": "Solutions",
      "metadata": {
        "company_name": "Example Construction AI",
        "page_type": "solution",
        "intent_stage": "consideration"
      }
    }
  ]
}
```

## `POST /chat`

Runs one lead-nurturing conversation turn.

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "lead_id": "demo-lead",
    "message": "We spend too much time checking payment apps. Can this reduce missing lien waivers?"
  }'
```

Request body:

```json
{
  "lead_id": "demo-lead",
  "message": "Lead message text."
}
```

Response fields:

- `lead`: current lead state.
- `reply`: response to show or send to the lead.
- `retrieved_context`: RAG chunks used by the response generator.
- `next_action`: `continue_nurture`, `offer_case_study`, or `schedule_contact`.
- `observation`: structured analysis of the lead message.
- `rationale`: human-readable scoring explanation.

Example response shape:

```json
{
  "lead": {
    "lead_id": "demo-lead",
    "temperature": "warm",
    "score": 64,
    "signals": ["reduce", "too much time"],
    "objections": [],
    "demographics": {},
    "updated_at": "2026-06-24T00:00:00Z"
  },
  "reply": "That pain is exactly where the strongest value tends to show up...",
  "retrieved_context": [],
  "next_action": "offer_case_study",
  "observation": {
    "sentiment": {"label": "positive", "score": 0.3, "evidence": ["reduce"]},
    "intent": "learn",
    "pain_points": ["too much time", "missing"],
    "objections": [],
    "buying_signals": [],
    "questions": ["Can this reduce missing lien waivers?"],
    "recommended_rag_topics": ["risk_reduction"]
  },
  "rationale": "warm lead scored ..."
}
```

## `GET /leads`

Lists known leads ordered by score and update time.

```bash
curl http://localhost:8000/leads
```

Example response:

```json
[
  {
    "lead_id": "demo-lead",
    "temperature": "hot",
    "score": 88,
    "rationale": "hot lead scored ...",
    "updated_at": "2026-06-24 12:00:00"
  }
]
```

## `GET /leads/{lead_id}/observations`

Returns the structured observation history for a lead.

```bash
curl http://localhost:8000/leads/demo-lead/observations
```

Example response:

```json
[
  {
    "channel": "chat",
    "message": "This is useful. I am the CFO and we have budget for a demo.",
    "analysis": {
      "sentiment": {"label": "positive", "score": 0.6, "evidence": ["useful", "budget", "demo"]},
      "intent": "schedule_demo",
      "buying_signals": ["budget", "demo"],
      "demographics": {
        "occupation": "CFO",
        "inference_policy": "explicit_self_disclosure_only"
      }
    },
    "created_at": "2026-06-24 12:00:00"
  }
]
```
