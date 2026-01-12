from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class TFTSet(str, Enum):
    """TFT set versions."""
    SET_10 = "10"
    SET_11 = "11"
    SET_12 = "12"


class Position(BaseModel):
    """Position on the TFT board."""
    row: int = Field(..., ge=0, le=3, description="Row position (0-3)")
    col: int = Field(..., ge=0, le=6, description="Column position (0-6)")


class Champion(BaseModel):
    """Champion on the board."""
    name: str
    stars: int = Field(..., ge=1, le=3)
    items: List[str] = []
    position: Optional[Position] = None


class GameSnapshot(BaseModel):
    """Current game state snapshot provided by user."""
    set_version: TFTSet = Field(..., description="Current TFT set")
    stage: str = Field(..., description="Current stage (e.g., '4-2')")
    level: int = Field(..., ge=1, le=10, description="Player level")
    gold: int = Field(..., ge=0, description="Current gold")
    health: int = Field(..., ge=0, le=100, description="Current health")
    
    # Board state
    board: List[Champion] = Field(default_factory=list)
    bench: List[Champion] = Field(default_factory=list)
    
    # Available resources
    available_augments: List[str] = Field(default_factory=list)
    shop_champions: List[str] = Field(default_factory=list)
    
    # Traits/synergies active
    active_traits: List[str] = Field(default_factory=list)
    
    # Additional context
    context: Optional[str] = Field(None, description="Additional context or questions")


class StrategicOption(BaseModel):
    """A strategic option with explanation."""
    rank: int
    title: str
    description: str
    reasoning: str
    key_stats: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0)


class StrategicAdvice(BaseModel):
    """RAG-generated strategic advice."""
    snapshot: GameSnapshot
    options: List[StrategicOption]
    general_advice: str
    retrieved_context: List[str] = Field(default_factory=list)


class MatchData(BaseModel):
    """TFT match data from Riot API."""
    match_id: str
    game_datetime: int
    game_length: float
    tft_set_number: int
    participants: List[Dict[str, Any]]


class CompStats(BaseModel):
    """Statistics for a team composition."""
    comp_name: str
    patch: str
    champions: List[str]
    avg_placement: float
    play_rate: float
    top4_rate: float
    win_rate: float
    sample_size: int
    key_augments: List[str] = []
    key_items: Dict[str, List[str]] = Field(default_factory=dict)


class AugmentStats(BaseModel):
    """Statistics for an augment."""
    augment_name: str
    patch: str
    pick_rate: float
    avg_placement: float
    top4_rate: float
    win_rate: float
    sample_size: int
    synergistic_comps: List[str] = []


class HealthStatus(BaseModel):
    """API health check response."""
    status: str
    version: str
    database_connected: bool
    riot_api_configured: bool
