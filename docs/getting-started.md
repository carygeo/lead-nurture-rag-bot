# Getting started

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/)
- Optional: an OpenAI API key if you want LLM-written responses instead of deterministic fallback responses.

## Install

```bash
git clone git@github.com:carygeo/lead-nurture-rag-bot.git
cd lead-nurture-rag-bot
uv sync --extra test
cp .env.example .env
```

## Run the API

```bash
uv run uvicorn lead_nurture_rag.app:app --reload
```

Verify:

```bash
curl http://localhost:8000/health
```

Expected shape:

```json
{
  "ok": true,
  "chunks": 0
}
```

The `chunks` number increases after ingesting knowledge.

## Run the chat UI

In another terminal:

```bash
uv run streamlit run src/lead_nurture_rag/web.py
```

Use the sidebar to paste company knowledge, then chat as a lead.

## Optional LLM mode

Without an API key, the app uses deterministic local replies. This is useful for testing lead scoring, observation extraction, retrieval, and persistence without external dependencies.

To enable LLM-written responses, edit `.env`:

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Restart the API after changing `.env`.

## First test flow

1. Start the API.
2. Ingest a small block of company knowledge.
3. Send a chat message from a fake lead.
4. Inspect the response, lead score, observation, and retrieved context.
5. Send a second message with stronger buying intent.
6. Confirm the lead warms up or becomes hot.

### Ingest company knowledge

```bash
curl -X POST http://localhost:8000/ingest/text \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "company-profile",
    "text": "BuildCo AI validates subcontractor payment applications, detects missing lien waivers, flags compliance risk, and summarizes approval issues for construction project teams."
  }'
```

### Chat as a lead

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "lead_id": "demo-lead",
    "message": "We spend too much time checking payment apps. Can this reduce missing lien waiver risk?"
  }'
```

### Send a stronger buying signal

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "lead_id": "demo-lead",
    "message": "This is useful. I am the CFO and we have budget for a demo this week."
  }'
```

### Inspect leads and observations

```bash
curl http://localhost:8000/leads
curl http://localhost:8000/leads/demo-lead/observations
```

## Runtime files

By default, runtime state is written to `data/`:

```text
data/
├── knowledge.json
└── leads.sqlite
```

Override with:

```bash
DATA_DIR=/tmp/lead-nurture-demo uv run uvicorn lead_nurture_rag.app:app --reload
```
