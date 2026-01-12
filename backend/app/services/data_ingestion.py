import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from collections import defaultdict, Counter

from app.services.riot_client import RiotAPIClient
from app.models.schemas import MatchData, CompStats, AugmentStats
from app.core.config import settings

logger = logging.getLogger(__name__)


class DataIngestionService:
    """Service for ingesting and processing TFT match data."""
    
    def __init__(self, riot_client: Optional[RiotAPIClient] = None):
        self.riot_client = riot_client or RiotAPIClient()
        self.cache_dir = Path(settings.match_data_cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_path(self, match_id: str) -> Path:
        """Get cache file path for a match."""
        return self.cache_dir / f"{match_id}.json"
    
    async def fetch_and_cache_match(self, match_id: str) -> MatchData:
        """Fetch match data and cache it locally."""
        cache_path = self._get_cache_path(match_id)
        
        # Check cache first
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                data = json.load(f)
                return MatchData(**data)
        
        # Fetch from API
        match_data = await self.riot_client.get_match_details(match_id)
        
        # Cache the data
        with open(cache_path, 'w') as f:
            json.dump(match_data.dict(), f)
        
        return match_data
    
    async def ingest_player_matches(
        self, 
        puuid: str, 
        count: int = 20
    ) -> List[MatchData]:
        """Ingest matches for a specific player."""
        match_ids = await self.riot_client.get_match_ids_by_puuid(puuid, count=count)
        matches = []
        
        for match_id in match_ids:
            try:
                match_data = await self.fetch_and_cache_match(match_id)
                matches.append(match_data)
                logger.info(f"Ingested match {match_id}")
            except Exception as e:
                logger.error(f"Failed to ingest match {match_id}: {e}")
        
        return matches
    
    async def ingest_high_elo_matches(
        self, 
        platform: str = "na1", 
        matches_per_player: int = 10,
        max_players: int = 50
    ) -> List[MatchData]:
        """Ingest matches from high ELO players."""
        all_matches = []
        
        # Get high ELO players
        try:
            challenger = await self.riot_client.get_challenger_players(platform)
            grandmaster = await self.riot_client.get_grandmaster_players(platform)
            master = await self.riot_client.get_master_players(platform)
            
            high_elo_players = (challenger + grandmaster + master)[:max_players]
            logger.info(f"Found {len(high_elo_players)} high ELO players")
            
        except Exception as e:
            logger.error(f"Failed to get high ELO players: {e}")
            return []
        
        # Fetch matches for each player
        for player_data in high_elo_players:
            summoner_id = player_data.get("summonerId")
            if not summoner_id:
                continue
                
            try:
                # Get summoner info to get PUUID
                summoner = await self.riot_client.get_summoner_by_puuid(summoner_id, platform)
                puuid = summoner.get("puuid")
                
                if puuid:
                    matches = await self.ingest_player_matches(puuid, count=matches_per_player)
                    all_matches.extend(matches)
                    
            except Exception as e:
                logger.error(f"Failed to ingest matches for player {summoner_id}: {e}")
        
        return all_matches
    
    def extract_composition(self, participant: Dict[str, Any]) -> List[str]:
        """Extract champion composition from participant data."""
        units = participant.get("units", [])
        return sorted([unit.get("character_id", "") for unit in units])
    
    def extract_augments(self, participant: Dict[str, Any]) -> List[str]:
        """Extract augments from participant data."""
        return participant.get("augments", [])
    
    def extract_items(self, participant: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract items per champion."""
        units = participant.get("units", [])
        items_map = {}
        
        for unit in units:
            champion = unit.get("character_id", "")
            items = unit.get("itemNames", [])
            if champion and items:
                items_map[champion] = items
        
        return items_map
    
    def compute_comp_stats(
        self, 
        matches: List[MatchData], 
        patch: str
    ) -> List[CompStats]:
        """Compute statistics for team compositions."""
        comp_data = defaultdict(lambda: {
            "placements": [],
            "augments": Counter(),
            "items": defaultdict(Counter),
            "champions": set()
        })
        
        for match in matches:
            if str(match.tft_set_number) != patch.split(".")[0]:
                continue
                
            for participant in match.participants:
                comp = tuple(self.extract_composition(participant))
                placement = participant.get("placement", 8)
                augments = self.extract_augments(participant)
                items = self.extract_items(participant)
                
                comp_data[comp]["placements"].append(placement)
                comp_data[comp]["augments"].update(augments)
                comp_data[comp]["champions"].update(comp)
                
                for champ, item_list in items.items():
                    comp_data[comp]["items"][champ].update(item_list)
        
        # Compute statistics
        stats = []
        for comp, data in comp_data.items():
            if len(data["placements"]) < 5:  # Minimum sample size
                continue
                
            placements = data["placements"]
            avg_placement = sum(placements) / len(placements)
            top4_rate = sum(1 for p in placements if p <= 4) / len(placements)
            win_rate = sum(1 for p in placements if p == 1) / len(placements)
            
            # Get most common augments
            top_augments = [aug for aug, _ in data["augments"].most_common(5)]
            
            # Get most common items per champion
            key_items = {}
            for champ, item_counter in data["items"].items():
                key_items[champ] = [item for item, _ in item_counter.most_common(3)]
            
            stats.append(CompStats(
                comp_name=f"Comp_{hash(comp) % 10000}",
                patch=patch,
                champions=list(data["champions"]),
                avg_placement=avg_placement,
                play_rate=len(placements) / len(matches),
                top4_rate=top4_rate,
                win_rate=win_rate,
                sample_size=len(placements),
                key_augments=top_augments,
                key_items=key_items
            ))
        
        return sorted(stats, key=lambda x: x.avg_placement)
    
    def compute_augment_stats(
        self, 
        matches: List[MatchData], 
        patch: str
    ) -> List[AugmentStats]:
        """Compute statistics for augments."""
        augment_data = defaultdict(lambda: {
            "placements": [],
            "comps": Counter()
        })
        
        for match in matches:
            if str(match.tft_set_number) != patch.split(".")[0]:
                continue
                
            for participant in match.participants:
                augments = self.extract_augments(participant)
                placement = participant.get("placement", 8)
                comp = tuple(self.extract_composition(participant))
                
                for augment in augments:
                    augment_data[augment]["placements"].append(placement)
                    augment_data[augment]["comps"][comp] += 1
        
        # Compute statistics
        total_picks = sum(len(data["placements"]) for data in augment_data.values())
        stats = []
        
        for augment, data in augment_data.items():
            if len(data["placements"]) < 10:  # Minimum sample size
                continue
                
            placements = data["placements"]
            avg_placement = sum(placements) / len(placements)
            top4_rate = sum(1 for p in placements if p <= 4) / len(placements)
            win_rate = sum(1 for p in placements if p == 1) / len(placements)
            
            # Get synergistic comps
            synergistic_comps = [
                f"Comp_{hash(comp) % 10000}" 
                for comp, _ in data["comps"].most_common(3)
            ]
            
            stats.append(AugmentStats(
                augment_name=augment,
                patch=patch,
                pick_rate=len(placements) / total_picks if total_picks > 0 else 0,
                avg_placement=avg_placement,
                top4_rate=top4_rate,
                win_rate=win_rate,
                sample_size=len(placements),
                synergistic_comps=synergistic_comps
            ))
        
        return sorted(stats, key=lambda x: x.avg_placement)
