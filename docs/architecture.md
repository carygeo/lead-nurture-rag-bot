# Architecture

The prototype separates ingestion, retrieval, observation analysis, lead scoring, response generation, and persistence so each part can be replaced independently later.

## Component diagram

```mermaid
flowchart TB
    subgraph Inputs
        Manual[Manual text knowledge]
        Site[Company website / campaign site]
        Lead[Lead messages]
    end

    subgraph Ingestion
        TextAPI[POST /ingest/text]
        UrlAPI[POST /ingest/url]
        CampaignAPI[POST /ingest/campaign]
        Crawler[Campaign crawler]
        Categorizer[Categorizer]
    end

    subgraph Knowledge
        Chunks[Knowledge chunks]
        Metadata[Chunk metadata]
        TFIDF[TF-IDF index]
        KnowledgeJson[(data/knowledge.json)]
    end

    subgraph Conversation
        API[FastAPI]
        Web[Streamlit UI]
        Agent[LeadNurtureAgent]
        Observation[Observation analyzer]
        Scoring[Lead scoring]
        Reply[Response generator]
    end

    subgraph Persistence
        SQLite[(data/leads.sqlite)]
        Turns[Conversation turns]
        Observations[Observation records]
        Leads[Lead state]
    end

    Manual --> TextAPI --> Categorizer
    Site --> UrlAPI --> Categorizer
    Site --> CampaignAPI --> Crawler --> Categorizer
    Categorizer --> Chunks
    Chunks --> Metadata
    Chunks --> KnowledgeJson
    Chunks --> TFIDF

    Lead --> Web --> API --> Agent
    API --> Agent
    Agent --> Observation --> Scoring
    Agent --> TFIDF
    TFIDF --> Agent
    Scoring --> Agent
    Agent --> Reply
    Reply --> API --> Web

    API --> Turns --> SQLite
    API --> Observations --> SQLite
    API --> Leads --> SQLite
```

## Main modules

### `app.py`

FastAPI entry point. It wires together:

- `KnowledgeBase(DATA_DIR / "knowledge.json")`
- `ConversationStore(DATA_DIR / "leads.sqlite")`
- `LeadNurtureAgent(kb)`

It exposes ingestion, chat, lead listing, and observation endpoints.

### `retriever.py`

Small local knowledge base. It:

- normalizes text,
- splits text into stable overlapping chunks,
- assigns stable chunk IDs,
- categorizes chunks,
- persists chunks to JSON,
- indexes chunk text plus metadata with `TfidfVectorizer`,
- returns `SearchHit` records with relevance scores.

This is intentionally simple. The public shape is close enough that it can later be swapped for Chroma, Qdrant, pgvector, or a managed embedding service.

### `crawler.py`

Campaign-oriented crawler. It:

- accepts `CampaignConfig`,
- starts from seed pages,
- limits crawling to allowed domains,
- skips noisy pages,
- extracts main body text,
- categorizes pages,
- returns `CrawledDocument` objects for ingestion.

### `categorizer.py`

Metadata enrichment. It identifies page and chunk attributes such as:

- page type,
- intent stage,
- topics,
- personas,
- industries,
- questions answered.

Metadata is included in the retrieval index so conceptual searches can match even when exact wording differs.

### `observation.py`

Turns a lead message into a structured observation analysis:

- sentiment,
- intent,
- pain points,
- objections,
- buying signals,
- questions,
- recommended RAG topics,
- explicitly self-disclosed demographics.

The demographic policy is conservative: age range and gender are recorded only when explicitly self-disclosed. The system does not guess protected traits.

### `agent.py`

The core loop:

1. Build and analyze observation.
2. Expand the retrieval query with recommended RAG topics.
3. Retrieve relevant company knowledge.
4. Score the lead.
5. Choose the next action.
6. Generate either an LLM reply or deterministic fallback reply.
7. Return a complete `AgentTurnResult`.

### `store.py`

SQLite persistence for:

- conversation turns,
- current lead state,
- observation analysis records.

## Replaceable seams

```mermaid
flowchart LR
    Agent[LeadNurtureAgent] --> Retriever[KnowledgeBase interface]
    Agent --> Response[Response generation]
    Agent --> Scoring[Scoring rules]
    API[FastAPI] --> Store[ConversationStore]

    Retriever -. replace .-> VectorDB[Chroma / Qdrant / pgvector]
    Response -. replace .-> LLM[LLM provider / prompt profiles]
    Scoring -. replace .-> Model[ML scoring model]
    Store -. replace .-> CRM[CRM / data warehouse]
```

The goal is not to make the first version production-grade. The goal is to validate the conversation logic, lead-state transitions, and knowledge-grounded response strategy before adding email and CRM integrations.
