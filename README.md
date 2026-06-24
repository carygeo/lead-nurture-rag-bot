# Lead nurture RAG bot

Prototype chatbot for testing a lead-generation / lead-nurturing loop before wiring the same logic into email.

The prototype lets you:

- Ingest company or website knowledge into a small local RAG store.
- Crawl a campaign website from seed URLs with domain limits, page filtering, and per-chunk categorization.
- Chat as a potential lead.
- Retrieve relevant company context on each turn.
- Score the lead as `cold`, `warm`, or `hot` based on interest, pain, objections, and buying signals.
- Generate a value-led nurturing reply with a next-best action.
- Persist conversation turns and lead state locally in SQLite.

## Architecture

- `KnowledgeBase`: local TF-IDF retrieval over stable chunks. It enriches each chunk with categorization metadata and indexes both text and metadata. It is intentionally simple and rebuildable; swap this layer later for Chroma/Qdrant/OpenAI embeddings.
- `Campaign crawler`: domain-limited crawler that starts from campaign seed URLs, skips noisy pages, extracts main content, and tags page/chunk metadata.
- `LeadNurtureAgent`: agent loop that retrieves context, scores the lead, chooses a next action, and drafts a response.
- `ConversationStore`: SQLite persistence for turns and lead scores.
- `FastAPI`: API for ingesting knowledge, chatting, and listing leads.
- `Streamlit`: quick test UI.

## Quick start

```bash
uv sync --extra test
cp .env.example .env
uv run uvicorn lead_nurture_rag.app:app --reload
```

In a second terminal:

```bash
uv run streamlit run src/lead_nurture_rag/web.py
```

Open the Streamlit URL, paste company/site knowledge in the sidebar, and chat as a lead.

## Optional LLM mode

If `OPENAI_API_KEY` is set, the agent uses an LLM to write responses from the retrieved context. If it is not set, the prototype uses a deterministic local fallback so you can test the loop without credentials.

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Do not commit `.env`.

## API examples

Crawl a campaign website:

```bash
curl -X POST http://localhost:8000/ingest/campaign \
  -H 'Content-Type: application/json' \
  -d @campaigns/example.json
```

Or from the command line:

```bash
uv run python scripts/ingest_campaign.py campaigns/example.json
```

The crawler starts from `seed_pages`, only follows links on `allowed_domains`, skips noisy pages like privacy/terms/login/careers, extracts main page text, categorizes each page/chunk, and stores stable chunks in `data/knowledge.json`.

Each chunk receives metadata such as:

```json
{
  "company_name": "Example Construction AI",
  "page_type": "solution",
  "intent_stage": "consideration",
  "topics": ["payment_application_validation", "risk_reduction"],
  "personas": ["project_team"],
  "industries": ["construction"],
  "questions_answered": ["pain_point"]
}
```

This metadata is included in the retrieval index so lead questions like “Can this reduce lien waiver risk?” match both page text and conceptual tags.

Ingest text:

```bash
curl -X POST http://localhost:8000/ingest/text \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "company-profile",
    "text": "BuildCo AI validates subcontractor payment applications, finds missing lien waivers, and summarizes risk before approvals."
  }'
```

Chat:

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "lead_id": "demo-lead",
    "message": "We spend too much time checking payment apps. Can this reduce missing lien waivers?"
  }'
```

List leads:

```bash
curl http://localhost:8000/leads
```

## Lead temperature logic

- `cold`: weak or generic engagement; continue nurture with a light value point and qualification question.
- `warm`: clear pain/interest; offer a case study, workflow example, or business-specific proof point.
- `hot`: demo, budget, schedule, pricing, or purchase timing signal; ask for a concrete contact appointment/demo time.

Conversation pipeline:

```text
initial educational/value communication
→ retrieve company knowledge relevant to the lead's question
→ test comfort/interest with one focused question
→ detect pain, objections, and buying signals
→ if warm, offer proof/workflow example
→ if hot, route to schedule_contact and ask for appointment timing
```

## Development

```bash
uv run python -m pytest -q
```

## Next integration steps

1. Replace TF-IDF retrieval with Chroma or Qdrant plus embeddings.
2. Add source-specific metadata: company page, service line, industry, persona, objection type.
3. Add a campaign/persona prompt layer for specific outbound motions.
4. Add email adapter that reuses `LeadNurtureAgent.respond()` for each reply thread.
5. Add CRM export and human-review queue for hot leads.
