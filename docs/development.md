# Development

## Install dev dependencies

```bash
uv sync --extra test
```

## Run tests

```bash
uv run python -m pytest -q
```

## Run the API

```bash
uv run uvicorn lead_nurture_rag.app:app --reload
```

## Run the Streamlit UI

```bash
uv run streamlit run src/lead_nurture_rag/web.py
```

## Useful local commands

### Ingest campaign config

```bash
uv run python scripts/ingest_campaign.py campaigns/example.json
```

### Reset runtime data

Runtime data lives under `data/` and is ignored by git. To start fresh, stop the API and move the data directory out of the way:

```bash
mv data data.before-reset-$(date +%Y%m%d-%H%M%S)
```

Then restart the API.

## Testing strategy

The tests cover:

- agent scoring behavior,
- observation analysis,
- observation persistence,
- scheduling/hot-lead transitions,
- crawler behavior,
- categorization,
- campaign ingestion,
- retriever behavior,
- SQLite store behavior.

## Code structure

```text
src/lead_nurture_rag/
├── agent.py         # lead nurturing loop
├── app.py           # FastAPI app and endpoints
├── categorizer.py   # page/chunk metadata rules
├── crawler.py       # campaign crawler
├── models.py        # Pydantic models
├── observation.py   # observation analysis
├── retriever.py     # local TF-IDF knowledge base
├── store.py         # SQLite persistence
└── web.py           # Streamlit UI
```

## Design principles

- Keep the prototype local-first and easy to run.
- Make every conversation turn inspectable.
- Keep lead scoring explainable before introducing ML models.
- Avoid guessing protected demographic traits.
- Keep retrieval replaceable.
- Keep email integration separate from the core agent loop.

## Adding a new feature

Recommended workflow:

1. Add or update tests first.
2. Implement the smallest change that makes tests pass.
3. Run the full test suite.
4. Update docs if behavior or setup changes.
5. Commit with a conventional commit message.

## Future development ideas

- Add `POST /draft/email` for email-specific draft generation.
- Add campaign profile objects and prompt templates.
- Add vector DB support behind the `KnowledgeBase` interface.
- Add a review queue for hot leads.
- Add lead timeline UI in Streamlit.
- Add evaluation fixtures for cold/warm/hot transitions.
