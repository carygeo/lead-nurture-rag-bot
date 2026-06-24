# Data flow

This page documents how data moves through the prototype.

## Knowledge ingestion flow

```mermaid
flowchart TD
    Start[Campaign config or manual text] --> InputType{Input type}
    InputType -- Manual text --> TextEndpoint[POST /ingest/text]
    InputType -- Single URL --> UrlEndpoint[POST /ingest/url]
    InputType -- Campaign website --> CampaignEndpoint[POST /ingest/campaign]

    CampaignEndpoint --> Crawler[Fetch seed pages and allowed links]
    UrlEndpoint --> Fetch[Fetch URL]
    TextEndpoint --> Chunk[Chunk text]
    Fetch --> Extract[Extract readable page text]
    Crawler --> Extract
    Extract --> Categorize[Categorize page and chunks]
    Categorize --> Chunk
    Chunk --> StableID[Create stable chunk IDs]
    StableID --> Persist[Persist to data/knowledge.json]
    Persist --> Index[Build TF-IDF index]
```

## Chat turn flow

```mermaid
flowchart TD
    Msg[Lead message] --> History[Load conversation history]
    History --> Obs[Build observation]
    Obs --> Analyze[Analyze sentiment, intent, pain, objections, buying signals, questions]
    Analyze --> Topics[Add recommended RAG topics]
    Topics --> Query[Build retrieval query]
    Query --> Search[Search knowledge base]
    Analyze --> Score[Score lead]
    Score --> Temp{Temperature}
    Temp -- Cold --> Continue[continue_nurture]
    Temp -- Warm --> CaseStudy[offer_case_study]
    Temp -- Hot --> Schedule[schedule_contact]
    Search --> Generate[Generate reply]
    Continue --> Generate
    CaseStudy --> Generate
    Schedule --> Generate
    Generate --> Persist[Persist turns, observation, lead state]
    Persist --> Response[Return API response]
```

## Sequence: one chat request

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI /chat
    participant DB as SQLite
    participant Agent as LeadNurtureAgent
    participant Obs as Observation Analyzer
    participant KB as KnowledgeBase
    participant LLM as Optional LLM

    Client->>API: lead_id + message
    API->>DB: get_history(lead_id)
    DB-->>API: prior turns
    API->>Agent: respond(lead_id, history, message)
    Agent->>Obs: analyze_observation(message, history)
    Obs-->>Agent: structured observation analysis
    Agent->>KB: search(message + recommended topics)
    KB-->>Agent: relevant chunks
    Agent->>Agent: score lead and choose next action
    alt OPENAI_API_KEY is set
        Agent->>LLM: generate grounded nurture reply
        LLM-->>Agent: reply
    else no API key
        Agent->>Agent: deterministic fallback reply
    end
    Agent-->>API: AgentTurnResult
    API->>DB: append observation
    API->>DB: append user and assistant turns
    API->>DB: upsert lead state
    API-->>Client: reply, lead state, next action, retrieved context, observation
```

## Persistence model

```mermaid
erDiagram
    LEADS ||--o{ TURNS : has
    LEADS ||--o{ OBSERVATIONS : has

    LEADS {
        string lead_id PK
        string temperature
        int score
        string rationale
        datetime updated_at
    }

    TURNS {
        int id PK
        string lead_id FK
        string role
        string content
        datetime created_at
    }

    OBSERVATIONS {
        int id PK
        string lead_id FK
        string channel
        string message
        string analysis_json
        datetime created_at
    }
```

## Lead warming flow

```mermaid
stateDiagram-v2
    [*] --> Cold
    Cold --> Cold: generic reply / low signal
    Cold --> Warm: pain point or business-specific question
    Warm --> Warm: evaluation questions / case study interest
    Warm --> Hot: demo, budget, pricing, schedule, proposal, pilot
    Hot --> Warm: objection or negative sentiment
    Warm --> Cold: disengage / strong objection
    Hot --> [*]: schedule_contact
```

## Future email data flow

```mermaid
flowchart LR
    Outbound[Outbound cold email] --> Reply[Inbound email reply]
    Reply --> Adapter[Email adapter]
    Adapter --> Normalize[Normalize sender, thread, body]
    Normalize --> Agent[LeadNurtureAgent.respond]
    Agent --> Review{Human review required?}
    Review -- Hot lead --> Human[Sales / founder review]
    Review -- Safe nurture --> Draft[Draft email response]
    Draft --> Send[Send or queue]
    Agent --> CRM[CRM update]
    Agent --> DB[(Conversation + observations)]
```
