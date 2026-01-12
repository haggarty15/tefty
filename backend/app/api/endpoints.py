from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import logging

from app.models.schemas import (
    GameSnapshot, 
    StrategicAdvice,
    CompStats,
    AugmentStats,
    HealthStatus
)
from app.services.rag_service import RAGService
from app.services.vector_store import VectorStoreService
from app.services.data_ingestion import DataIngestionService
from app.services.riot_client import RiotAPIClient
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
rag_service = RAGService()
vector_store = VectorStoreService()
data_ingestion = DataIngestionService()


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint."""
    riot_configured = bool(settings.riot_api_key)
    
    try:
        # Test vector store connection
        vector_store.comp_collection.count()
        db_connected = True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_connected = False
    
    return HealthStatus(
        status="healthy" if db_connected else "degraded",
        version="1.0.0",
        database_connected=db_connected,
        riot_api_configured=riot_configured
    )


@router.post("/advice", response_model=StrategicAdvice)
async def get_strategic_advice(snapshot: GameSnapshot):
    """
    Get strategic advice for the current game state.
    
    Uses RAG to retrieve relevant statistics and playbooks,
    then generates ranked strategic options.
    """
    try:
        advice = await rag_service.generate_advice(snapshot)
        return advice
    except Exception as e:
        logger.error(f"Error generating advice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/ingest/player")
async def ingest_player_data(
    puuid: str,
    count: int = 20,
    background_tasks: BackgroundTasks = None
):
    """
    Ingest match data for a specific player.
    
    This will fetch matches from Riot API and cache them locally.
    """
    try:
        if background_tasks:
            background_tasks.add_task(
                data_ingestion.ingest_player_matches,
                puuid,
                count
            )
            return {"status": "ingestion_started", "puuid": puuid, "count": count}
        else:
            matches = await data_ingestion.ingest_player_matches(puuid, count)
            return {"status": "completed", "matches_ingested": len(matches)}
    except Exception as e:
        logger.error(f"Error ingesting player data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/ingest/high-elo")
async def ingest_high_elo_data(
    platform: str = "na1",
    matches_per_player: int = 10,
    max_players: int = 50,
    background_tasks: BackgroundTasks = None
):
    """
    Ingest match data from high ELO players.
    
    This will fetch matches from Challenger, Grandmaster, and Master players.
    """
    try:
        if background_tasks:
            background_tasks.add_task(
                data_ingestion.ingest_high_elo_matches,
                platform,
                matches_per_player,
                max_players
            )
            return {"status": "ingestion_started", "platform": platform}
        else:
            matches = await data_ingestion.ingest_high_elo_matches(
                platform, 
                matches_per_player, 
                max_players
            )
            return {"status": "completed", "matches_ingested": len(matches)}
    except Exception as e:
        logger.error(f"Error ingesting high ELO data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/compute-stats")
async def compute_and_store_stats(patch: str):
    """
    Compute statistics from cached match data and store in vector database.
    
    This processes all cached matches and computes comp/augment statistics.
    """
    try:
        import json
        from pathlib import Path
        from app.models.schemas import MatchData
        
        # Load all cached matches
        cache_dir = Path(settings.match_data_cache_dir)
        matches = []
        
        for match_file in cache_dir.glob("*.json"):
            with open(match_file, 'r') as f:
                data = json.load(f)
                matches.append(MatchData(**data))
        
        if not matches:
            raise HTTPException(status_code=404, detail="No cached matches found")
        
        # Compute statistics
        comp_stats = data_ingestion.compute_comp_stats(matches, patch)
        augment_stats = data_ingestion.compute_augment_stats(matches, patch)
        
        # Store in vector database
        vector_store.add_comp_stats(comp_stats)
        vector_store.add_augment_stats(augment_stats)
        
        return {
            "status": "completed",
            "matches_processed": len(matches),
            "comps_indexed": len(comp_stats),
            "augments_indexed": len(augment_stats)
        }
    except Exception as e:
        logger.error(f"Error computing stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/playbooks/add")
async def add_playbook(
    title: str,
    content: str,
    tags: List[str] = None
):
    """
    Add a strategic playbook to the knowledge base.
    
    Playbooks are authored strategic guides that will be retrieved
    during RAG to provide additional context.
    """
    try:
        vector_store.add_playbook(title, content, tags or [])
        return {"status": "success", "title": title}
    except Exception as e:
        logger.error(f"Error adding playbook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/compositions", response_model=List[dict])
async def query_compositions(query: str, n_results: int = 5, patch: str = None):
    """Query for relevant composition statistics."""
    try:
        results = vector_store.query_compositions(query, n_results, patch)
        return results
    except Exception as e:
        logger.error(f"Error querying compositions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/augments", response_model=List[dict])
async def query_augments(query: str, n_results: int = 5, patch: str = None):
    """Query for relevant augment statistics."""
    try:
        results = vector_store.query_augments(query, n_results, patch)
        return results
    except Exception as e:
        logger.error(f"Error querying augments: {e}")
        raise HTTPException(status_code=500, detail=str(e))
