# TFT Strategic Advisor

A full-stack web application that provides AI-powered strategic advice for Teamfight Tactics (TFT) using **Retrieval-Augmented Generation (RAG)** over real match data and expert playbooks.

## Features

- **Data-Driven Analysis**: Ingests match data from Riot Games TFT API
- **Patch-Versioned Statistics**: Computes team composition, augment, and item statistics by patch
- **RAG-Powered Advice**: Uses vector search to retrieve relevant stats and playbooks
- **Strategic Recommendations**: Generates ranked options with explanations and confidence scores
- **React + TypeScript Frontend**: Modern, responsive web interface
- **FastAPI Backend**: High-performance Python backend with async support

## Architecture

### Backend (Python/FastAPI)
- **Riot API Client**: Fetches TFT match data from official Riot Games API
- **Data Ingestion Service**: Caches and processes match data
- **Statistics Engine**: Computes patch-specific stats for compositions, augments, and items
- **Vector Store**: ChromaDB for semantic search over statistics and playbooks
- **RAG Service**: OpenAI-powered generation using retrieved context
- **REST API**: FastAPI endpoints for frontend communication

### Frontend (React/TypeScript)
- **Game State Input**: Form to capture current game snapshot
- **Strategic Advice Display**: Shows ranked recommendations with reasoning
- **API Integration**: Axios-based API client
- **Responsive UI**: Clean, user-friendly interface

### Data Flow
1. User inputs current game state (stage, level, board, augments, etc.)
2. Backend creates semantic query from snapshot
3. Vector store retrieves relevant composition/augment stats and playbooks
4. RAG service generates strategic options using LLM with retrieved context
5. Frontend displays ranked recommendations with explanations

## Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Riot Games API Key ([Get one here](https://developer.riotgames.com/))
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:
```env
RIOT_API_KEY=your_riot_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

6. Run the backend server:
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

### 1. Ingest Match Data

Before using the advisor, you need to ingest TFT match data:

**Option A: Ingest High-ELO Matches**
```bash
curl -X POST "http://localhost:8000/api/data/ingest/high-elo?platform=na1&matches_per_player=10&max_players=50"
```

**Option B: Ingest Specific Player Matches**
```bash
curl -X POST "http://localhost:8000/api/data/ingest/player?puuid=PLAYER_PUUID&count=20"
```

### 2. Compute Statistics

After ingesting matches, compute statistics and store in vector database:
```bash
curl -X POST "http://localhost:8000/api/data/compute-stats?patch=12"
```

### 3. Load Playbooks

The application comes with pre-written playbooks in `backend/data/playbooks/`. These are automatically loaded when you add them via the API:

```bash
curl -X POST "http://localhost:8000/api/playbooks/add?title=Early%20Game&content=$(cat backend/data/playbooks/early_game.md)"
```

### 4. Use the Web Interface

1. Open `http://localhost:3000` in your browser
2. Fill in your current game state:
   - Set version, stage, level, gold, health
   - Add champions on your board and bench
   - Specify active traits
   - Add available augment choices
   - Include any specific questions
3. Click "Get Strategic Advice"
4. Review the ranked strategic options with explanations

## API Endpoints

### Core Endpoints

- `GET /api/health` - Health check
- `POST /api/advice` - Get strategic advice (main endpoint)

### Data Management

- `POST /api/data/ingest/player` - Ingest player match data
- `POST /api/data/ingest/high-elo` - Ingest high-ELO match data
- `POST /api/data/compute-stats` - Compute and store statistics
- `POST /api/playbooks/add` - Add strategic playbook

### Query Endpoints

- `GET /api/stats/compositions` - Query composition statistics
- `GET /api/stats/augments` - Query augment statistics

## Example Request

```json
POST /api/advice
{
  "set_version": "12",
  "stage": "4-2",
  "level": 7,
  "gold": 30,
  "health": 60,
  "board": [
    {"name": "Ashe", "stars": 2, "items": ["Guinsoo", "Giant Slayer"]},
    {"name": "Sejuani", "stars": 2, "items": ["Warmog"]}
  ],
  "active_traits": ["Evoker", "Bruiser"],
  "available_augments": ["Cybernetic Implants", "Jeweled Lotus", "Preparation"],
  "context": "Should I pivot or push levels?"
}
```

## Project Structure

```
tefty/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints.py      # API routes
│   │   ├── core/
│   │   │   └── config.py         # Configuration
│   │   ├── models/
│   │   │   └── schemas.py        # Pydantic models
│   │   ├── services/
│   │   │   ├── riot_client.py    # Riot API client
│   │   │   ├── data_ingestion.py # Data processing
│   │   │   ├── vector_store.py   # ChromaDB interface
│   │   │   └── rag_service.py    # RAG implementation
│   │   └── main.py               # FastAPI app
│   ├── data/
│   │   ├── playbooks/            # Strategic playbooks
│   │   ├── cache/                # Cached match data
│   │   └── chroma_db/            # Vector database
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/             # API client
│   │   ├── types/                # TypeScript types
│   │   ├── App.tsx               # Main app
│   │   └── main.tsx              # Entry point
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **ChromaDB**: Vector database for semantic search
- **Sentence Transformers**: Text embeddings
- **OpenAI API**: LLM for advice generation
- **Pandas/NumPy**: Data processing
- **httpx/aiohttp**: Async HTTP clients

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool
- **Axios**: HTTP client

## RAG Implementation

The app uses a sophisticated RAG pipeline:

1. **Indexing Phase**:
   - Match data → Statistics computation → Text embeddings → Vector store

2. **Retrieval Phase**:
   - User query → Semantic search → Top-K relevant stats/playbooks

3. **Generation Phase**:
   - Retrieved context + User snapshot → LLM prompt → Strategic options

## Configuration

### Environment Variables

**Backend** (`.env`):
- `RIOT_API_KEY`: Your Riot Games API key
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: LLM model (default: gpt-4-turbo-preview)
- `CHROMA_PERSIST_DIRECTORY`: Vector DB path
- `DEBUG`: Enable debug mode

**Frontend**:
- Configured to proxy API requests to backend via Vite

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production

```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
# FastAPI runs directly; use gunicorn or uvicorn for production
```

## Docker Deployment

Build and run with Docker Compose:

```bash
docker-compose up -d
```

## Notes

- **No Third-Party Guide Text**: All strategic advice is based on computed statistics from match data and authored playbooks
- **Patch Versioning**: Statistics are tracked per patch for accuracy
- **Privacy**: All data is stored locally; no user data is shared externally
- **Rate Limiting**: Riot API has rate limits; the client includes delays between requests

## License

See LICENSE file for details.

## Disclaimer

This application is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc.