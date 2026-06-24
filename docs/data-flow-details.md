# Data flow details

This document supplements the architecture docs with a connection-oriented view of the system.

## End-to-end connections

```mermaid
flowchart LR
    subgraph KnowledgeSources[Knowledge sources]
        Site[Website]
        Text[Manual text]
        Campaign[Campaign config]
    end

    subgraph Backend[FastAPI backend]
        Health[GET /health]
        IngestText[POST /ingest/text]
        IngestUrl[POST /ingest/url]
        IngestCampaign[POST /ingest/campaign]
        Chat[POST /chat]
        Leads[GET /leads]
        Observations[GET /leads/:id/observations]
    end

    subgraph Core[Core services]
        Crawler[Crawler]
        KB[KnowledgeBase]
        Agent[LeadNurtureAgent]
        Analyzer[Observation analyzer]
        Store[ConversationStore]
    end

    subgraph Storage[Local storage]
        KnowledgeJson[(knowledge.json)]
        SQLite[(leads.sqlite)]
    end

    Site --> IngestUrl
    Campaign --> IngestCampaign
    Text --> IngestText
    IngestCampaign --> Crawler
    Crawler --> KB
    IngestUrl --> KB
    IngestText --> KB
    KB --> KnowledgeJson

    Chat --> Store
    Chat --> Agent
    Agent --> Analyzer
    Agent --> KB
    Agent --> Store
    Store --> SQLite
    Leads --> Store
    Observations --> Store
```

## Runtime request/response boundary

The `POST /chat` response intentionally returns more than just the reply. This makes the prototype debuggable.

Returned data includes:

- the generated reply,
- the current lead state,
- retrieved context,
- structured observation analysis,
- next action,
- scoring rationale.

That makes it possible to inspect why a lead became warm or hot instead of treating the bot as a black box.
