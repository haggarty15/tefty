# TFT Strategic Advisor - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User (Web Browser)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Components:                                             │   │
│  │  • GameSnapshotForm  → Capture game state               │   │
│  │  • ChampionInput     → Add champions/items               │   │
│  │  • AdviceDisplay     → Show recommendations              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  API Client (Axios)                                      │   │
│  │  • POST /api/advice                                      │   │
│  │  • GET /api/health                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI + Python)                    │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Endpoints                          │  │
│  │  /api/advice          → Strategic advice generation       │  │
│  │  /api/data/ingest/*   → Data ingestion                    │  │
│  │  /api/playbooks/add   → Add playbooks                     │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                              │
│                   ▼                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    RAG Service                            │  │
│  │  1. Create query from snapshot                            │  │
│  │  2. Retrieve relevant data                                │  │
│  │  3. Build LLM context                                     │  │
│  │  4. Generate strategic options                            │  │
│  └────────┬───────────────────────────┬────────────────────┘  │
│           │                           │                         │
│           ▼                           ▼                         │
│  ┌────────────────────┐    ┌──────────────────────┐           │
│  │  Vector Store      │    │  OpenAI API          │           │
│  │  (ChromaDB)        │    │  (GPT-4)             │           │
│  │                    │    │                      │           │
│  │  • Comp Stats      │    │  Generate:           │           │
│  │  • Augment Stats   │    │  • Options           │           │
│  │  • Playbooks       │    │  • Reasoning         │           │
│  │                    │    │  • Explanations      │           │
│  │  [Embeddings]      │    └──────────────────────┘           │
│  └────────┬───────────┘                                        │
│           │                                                     │
│           ▲                                                     │
│  ┌────────┴───────────────────────────────────────────────┐   │
│  │              Data Ingestion Service                     │   │
│  │  • Fetch matches from Riot API                          │   │
│  │  • Cache locally                                         │   │
│  │  • Compute statistics                                    │   │
│  │  • Store in vector DB                                    │   │
│  └────────┬───────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Riot API Client                              │ │
│  │  • Get match IDs                                          │ │
│  │  • Get match details                                      │ │
│  │  • Get high-ELO players                                   │ │
│  │  • Rate limiting                                          │ │
│  └────────┬─────────────────────────────────────────────────┘ │
└───────────┼───────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Riot Games API                            │
│  • TFT Match Data                                                │
│  • Player Information                                            │
│  • Ranked Leaderboards                                           │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Data Ingestion Flow

```
Riot API → Match JSON → Local Cache → Statistics Computation
                                            ↓
                                    Text Description
                                            ↓
                                    Embeddings (Sentence Transformers)
                                            ↓
                                    ChromaDB Vector Store
```

### 2. RAG Query Flow

```
User Input → Game Snapshot → Semantic Query
                                   ↓
                         Vector Store Search
                                   ↓
              ┌────────────────────┴────────────────────┐
              ▼                    ▼                    ▼
        Comp Stats          Augment Stats         Playbooks
              │                    │                    │
              └────────────────────┴────────────────────┘
                                   ↓
                            Context Building
                                   ↓
                         LLM Prompt (OpenAI)
                                   ↓
                      Strategic Options Generation
                                   ↓
                         JSON Response to Frontend
```

### 3. Component Interaction

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ POST /api/advice
       │ { snapshot: {...} }
       ▼
┌──────────────────┐
│  API Endpoint    │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐      ┌─────────────────┐
│   RAG Service    │─────→│ Vector Store    │
└──────┬───────────┘      └─────────────────┘
       │                          │
       │                          │ Retrieved context
       │                          ▼
       │                  ┌───────────────┐
       └─────────────────→│   OpenAI      │
                          └───────┬───────┘
                                  │ Generated advice
                                  ▼
                          ┌───────────────┐
                          │   Response    │
                          └───────────────┘
```

## Key Components

### Backend Services

1. **RiotAPIClient**: Handles all Riot API interactions
2. **DataIngestionService**: Processes and caches match data
3. **VectorStoreService**: Manages ChromaDB for semantic search
4. **RAGService**: Orchestrates retrieval and generation
5. **API Endpoints**: FastAPI routes for frontend communication

### Frontend Components

1. **GameSnapshotForm**: User input collection
2. **ChampionInput**: Individual champion entry
3. **AdviceDisplay**: Results visualization
4. **API Service**: Backend communication

### Data Models

1. **GameSnapshot**: Current game state
2. **StrategicAdvice**: Generated recommendations
3. **CompStats**: Composition statistics
4. **AugmentStats**: Augment statistics

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React + TypeScript | UI framework |
| Build Tool | Vite | Fast development and building |
| Backend | FastAPI | REST API server |
| Vector DB | ChromaDB | Semantic search |
| Embeddings | Sentence Transformers | Text to vectors |
| LLM | OpenAI GPT-4 | Advice generation |
| Data Processing | Pandas + NumPy | Statistics computation |
| Deployment | Docker + Docker Compose | Containerization |

## Security & Configuration

- **Environment Variables**: API keys stored in `.env`
- **CORS**: Configured for localhost development
- **Rate Limiting**: Built into Riot API client
- **Data Privacy**: All data stored locally

## Scalability Considerations

- **Caching**: Match data cached locally to reduce API calls
- **Async**: FastAPI async endpoints for concurrent requests
- **Vector Search**: ChromaDB optimized for semantic search
- **Batch Processing**: Statistics computed in batches
