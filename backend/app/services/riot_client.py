import httpx
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.core.config import settings
from app.models.schemas import MatchData

logger = logging.getLogger(__name__)


class RiotAPIClient:
    """Client for interacting with Riot TFT API."""
    
    BASE_URLS = {
        "americas": "https://americas.api.riotgames.com",
        "europe": "https://europe.api.riotgames.com",
        "asia": "https://asia.api.riotgames.com",
    }
    
    PLATFORM_URLS = {
        "na1": "https://na1.api.riotgames.com",
        "euw1": "https://euw1.api.riotgames.com",
        "kr": "https://kr.api.riotgames.com",
    }
    
    def __init__(self, api_key: Optional[str] = None, region: Optional[str] = None):
        self.api_key = api_key or settings.riot_api_key
        self.region = region or settings.riot_api_region
        self.base_url = self.BASE_URLS.get(self.region, self.BASE_URLS["americas"])
        self.headers = {"X-Riot-Token": self.api_key}
        
    async def get_summoner_by_name(self, summoner_name: str, platform: str = "na1") -> Dict[str, Any]:
        """Get summoner information by name."""
        url = f"{self.PLATFORM_URLS[platform]}/tft/summoner/v1/summoners/by-name/{summoner_name}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def get_summoner_by_puuid(self, puuid: str, platform: str = "na1") -> Dict[str, Any]:
        """Get summoner information by PUUID."""
        url = f"{self.PLATFORM_URLS[platform]}/tft/summoner/v1/summoners/by-puuid/{puuid}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def get_match_ids_by_puuid(
        self, 
        puuid: str, 
        count: int = 20,
        start: int = 0
    ) -> List[str]:
        """Get match IDs for a player."""
        url = f"{self.base_url}/tft/match/v1/matches/by-puuid/{puuid}/ids"
        params = {"start": start, "count": count}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_match_details(self, match_id: str) -> MatchData:
        """Get detailed match information."""
        url = f"{self.base_url}/tft/match/v1/matches/{match_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            return MatchData(
                match_id=data["metadata"]["match_id"],
                game_datetime=data["info"]["game_datetime"],
                game_length=data["info"]["game_length"],
                tft_set_number=data["info"]["tft_set_number"],
                participants=data["info"]["participants"]
            )
    
    async def get_challenger_players(self, platform: str = "na1") -> List[Dict[str, Any]]:
        """Get list of challenger players."""
        url = f"{self.PLATFORM_URLS[platform]}/tft/league/v1/challenger"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("entries", [])
    
    async def get_grandmaster_players(self, platform: str = "na1") -> List[Dict[str, Any]]:
        """Get list of grandmaster players."""
        url = f"{self.PLATFORM_URLS[platform]}/tft/league/v1/grandmaster"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("entries", [])
    
    async def get_master_players(self, platform: str = "na1") -> List[Dict[str, Any]]:
        """Get list of master players."""
        url = f"{self.PLATFORM_URLS[platform]}/tft/league/v1/master"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("entries", [])
    
    async def rate_limit_safe_request(self, coro, delay: float = 1.2):
        """Execute request with rate limiting."""
        result = await coro
        await asyncio.sleep(delay)
        return result
