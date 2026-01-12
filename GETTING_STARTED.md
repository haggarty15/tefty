# Getting Started with TFT Strategic Advisor

This guide will help you get up and running quickly.

## Quick Start (5 minutes)

### 1. Prerequisites Check

Make sure you have installed:
- Python 3.9 or higher: `python3 --version`
- Node.js 18 or higher: `node --version`
- npm: `npm --version`

### 2. Get API Keys

You'll need two API keys:

**Riot Games API Key** (Required for data ingestion):
1. Visit https://developer.riotgames.com/
2. Sign in with your Riot account
3. Generate a Development API Key (24-hour key for testing)

**OpenAI API Key** (Required for advice generation):
1. Visit https://platform.openai.com/api-keys
2. Sign in or create an account
3. Create a new API key
4. Note: This will incur costs based on usage (~$0.01-0.10 per advice request)

### 3. Run Setup Script

From the project root directory:

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create Python virtual environment
- Install backend dependencies
- Install frontend dependencies
- Create `.env` file template

### 4. Configure Environment

Edit `backend/.env` with your API keys:

```bash
cd backend
nano .env  # or use your preferred editor
```

Add your keys:
```
RIOT_API_KEY=RGAPI-your-key-here
OPENAI_API_KEY=sk-your-key-here
```

### 5. Start the Backend

```bash
# From the backend directory
source venv/bin/activate
python -m app.main
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Start the Frontend

In a **new terminal window**:

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

### 7. Access the Application

Open your browser to: http://localhost:3000

You should see the TFT Strategic Advisor interface!

## First Time Setup (Optional but Recommended)

To get meaningful advice, you need to populate the database with match data:

### Option 1: Quick Demo (Minimal Setup)

Just load the playbooks without match data:

```bash
cd backend
source venv/bin/activate
python -m app.utils.load_playbooks
```

The app will work but will have limited statistical context.

### Option 2: Full Setup (Recommended)

This will take 10-20 minutes but provides full functionality:

1. **Ingest High-ELO Matches**:
```bash
curl -X POST "http://localhost:8000/api/data/ingest/high-elo?platform=na1&matches_per_player=5&max_players=20"
```

Wait for this to complete (may take 5-10 minutes due to API rate limits).

2. **Compute Statistics**:
```bash
curl -X POST "http://localhost:8000/api/data/compute-stats?patch=12"
```

3. **Load Playbooks**:
```bash
cd backend
source venv/bin/activate
python -m app.utils.load_playbooks
```

## Testing the Application

### Using the Web Interface

1. Go to http://localhost:3000
2. Fill in a sample game state:
   - Set Version: 12
   - Stage: 4-2
   - Level: 7
   - Gold: 30
   - Health: 60
3. Click "Add Champion" under Board
   - Name: Ashe
   - Stars: 2
   - Items: Guinsoo, Giant Slayer
4. Add Active Traits: Evoker, Sniper
5. Add context: "Should I pivot or push levels?"
6. Click "Get Strategic Advice"

### Using the API Directly

```bash
curl -X POST "http://localhost:8000/api/advice" \
  -H "Content-Type: application/json" \
  -d '{
    "set_version": "12",
    "stage": "4-2",
    "level": 7,
    "gold": 30,
    "health": 60,
    "board": [
      {"name": "Ashe", "stars": 2, "items": ["Guinsoo", "Giant Slayer"]}
    ],
    "active_traits": ["Evoker", "Sniper"],
    "context": "Should I pivot or push levels?"
  }'
```

## Troubleshooting

### Backend won't start

**Problem**: ModuleNotFoundError
- **Solution**: Make sure virtual environment is activated and dependencies installed
  ```bash
  cd backend
  source venv/bin/activate
  pip install -r requirements.txt
  ```

**Problem**: API key errors
- **Solution**: Check that `.env` file exists and contains valid keys

### Frontend won't start

**Problem**: Cannot find module
- **Solution**: Install dependencies
  ```bash
  cd frontend
  npm install
  ```

**Problem**: Port 3000 already in use
- **Solution**: Kill the process or use a different port
  ```bash
  # Edit vite.config.ts and change port to 3001
  ```

### No advice generated

**Problem**: Empty or generic advice
- **Solution**: Make sure you've loaded playbooks and/or ingested match data

**Problem**: OpenAI API errors
- **Solution**: 
  - Check API key is valid
  - Check you have credits in your OpenAI account
  - Check API quota/rate limits

### Data ingestion fails

**Problem**: 403 Forbidden from Riot API
- **Solution**: 
  - Check API key is valid and not expired (dev keys expire after 24 hours)
  - Check rate limits haven't been exceeded

**Problem**: 404 Not Found
- **Solution**: The PUUID or platform might be incorrect

## Next Steps

1. **Customize Playbooks**: Edit files in `backend/data/playbooks/` to add your own strategies
2. **Ingest More Data**: Run ingestion for multiple patches and regions
3. **Experiment**: Try different game states and see how the advice changes
4. **Deploy**: Use Docker Compose for production deployment

## Getting Help

- Check the main README.md for detailed documentation
- Review the API documentation at http://localhost:8000/docs
- Check logs in the terminal for error messages

## Resources

- [Riot Games API Documentation](https://developer.riotgames.com/apis)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
