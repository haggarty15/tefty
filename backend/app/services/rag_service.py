import openai
from typing import List, Dict, Any
import logging
import json

from app.core.config import settings
from app.models.schemas import GameSnapshot, StrategicAdvice, StrategicOption
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class RAGService:
    """Service for Retrieval-Augmented Generation of strategic advice."""
    
    def __init__(self, vector_store: VectorStoreService = None):
        self.vector_store = vector_store or VectorStoreService()
        openai.api_key = settings.openai_api_key
        self.model = settings.openai_model
    
    def _create_query_from_snapshot(self, snapshot: GameSnapshot) -> str:
        """Create a search query from game snapshot."""
        query_parts = []
        
        # Add champions on board
        if snapshot.board:
            champs = [c.name for c in snapshot.board]
            query_parts.append(f"Champions: {', '.join(champs)}")
        
        # Add active traits
        if snapshot.active_traits:
            query_parts.append(f"Traits: {', '.join(snapshot.active_traits)}")
        
        # Add stage and level context
        query_parts.append(f"Stage {snapshot.stage}, Level {snapshot.level}")
        
        # Add available augments
        if snapshot.available_augments:
            query_parts.append(f"Available augments: {', '.join(snapshot.available_augments)}")
        
        return " ".join(query_parts)
    
    async def generate_advice(self, snapshot: GameSnapshot) -> StrategicAdvice:
        """Generate strategic advice using RAG."""
        
        # Create query from snapshot
        query = self._create_query_from_snapshot(snapshot)
        
        # Retrieve relevant information
        comp_results = self.vector_store.query_compositions(
            query=query,
            n_results=5,
            patch_filter=snapshot.set_version.value if hasattr(snapshot.set_version, 'value') else None
        )
        
        augment_results = self.vector_store.query_augments(
            query=query,
            n_results=5,
            patch_filter=snapshot.set_version.value if hasattr(snapshot.set_version, 'value') else None
        )
        
        playbook_results = self.vector_store.query_playbooks(
            query=query,
            n_results=3
        )
        
        # Build context for LLM
        context = self._build_context(
            snapshot, 
            comp_results, 
            augment_results, 
            playbook_results
        )
        
        # Generate advice using LLM
        options = await self._generate_options(snapshot, context)
        general_advice = await self._generate_general_advice(snapshot, context)
        
        # Collect retrieved context for transparency
        retrieved_context = [
            f"Composition: {r['document'][:100]}..." for r in comp_results[:3]
        ] + [
            f"Augment: {r['document'][:100]}..." for r in augment_results[:3]
        ]
        
        return StrategicAdvice(
            snapshot=snapshot,
            options=options,
            general_advice=general_advice,
            retrieved_context=retrieved_context
        )
    
    def _build_context(
        self,
        snapshot: GameSnapshot,
        comp_results: List[Dict[str, Any]],
        augment_results: List[Dict[str, Any]],
        playbook_results: List[Dict[str, Any]]
    ) -> str:
        """Build context string for LLM prompt."""
        context_parts = []
        
        # Current game state
        context_parts.append("## Current Game State")
        context_parts.append(f"Set: {snapshot.set_version}")
        context_parts.append(f"Stage: {snapshot.stage}")
        context_parts.append(f"Level: {snapshot.level}")
        context_parts.append(f"Gold: {snapshot.gold}")
        context_parts.append(f"Health: {snapshot.health}")
        
        if snapshot.board:
            board_champs = [f"{c.name} ({c.stars}★)" for c in snapshot.board]
            context_parts.append(f"Board: {', '.join(board_champs)}")
        
        if snapshot.active_traits:
            context_parts.append(f"Active Traits: {', '.join(snapshot.active_traits)}")
        
        # Retrieved composition stats
        if comp_results:
            context_parts.append("\n## Relevant Team Compositions")
            for result in comp_results[:3]:
                context_parts.append(f"- {result['document']}")
        
        # Retrieved augment stats
        if augment_results:
            context_parts.append("\n## Relevant Augments")
            for result in augment_results[:3]:
                context_parts.append(f"- {result['document']}")
        
        # Strategic playbooks
        if playbook_results:
            context_parts.append("\n## Strategic Playbooks")
            for result in playbook_results:
                context_parts.append(f"- {result['document'][:200]}")
        
        return "\n".join(context_parts)
    
    async def _generate_options(
        self, 
        snapshot: GameSnapshot, 
        context: str
    ) -> List[StrategicOption]:
        """Generate strategic options using LLM."""
        
        prompt = f"""You are a TFT strategic advisor. Based on the current game state and retrieved statistics, provide 3-5 ranked strategic options for the player.

{context}

User Context: {snapshot.context or 'None provided'}

For each option, provide:
1. A clear title
2. A brief description of what to do
3. Reasoning based on the statistics and game state
4. Key stats supporting this option
5. Confidence level (0.0 to 1.0)

Return your response as a JSON array of options, ordered by recommendation strength.

Example format:
[
  {{
    "rank": 1,
    "title": "Pivot to Reroll Comp",
    "description": "Sell high-cost units and roll down for 3-star carries",
    "reasoning": "At stage 4-2 with 50 gold, statistics show this comp has 65% top 4 rate when executed at this timing",
    "key_stats": {{"avg_placement": 3.2, "top4_rate": 0.65}},
    "confidence": 0.85
  }}
]
"""
        
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional TFT coach providing strategic advice based on data."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            options_data = json.loads(content)
            
            # Handle both array and object with "options" key
            if isinstance(options_data, dict) and "options" in options_data:
                options_data = options_data["options"]
            
            options = []
            for i, opt_data in enumerate(options_data[:5]):
                options.append(StrategicOption(
                    rank=opt_data.get("rank", i + 1),
                    title=opt_data.get("title", "Strategic Option"),
                    description=opt_data.get("description", ""),
                    reasoning=opt_data.get("reasoning", ""),
                    key_stats=opt_data.get("key_stats", {}),
                    confidence=opt_data.get("confidence", 0.5)
                ))
            
            return options
            
        except Exception as e:
            logger.error(f"Error generating options: {e}")
            # Return fallback option
            return [
                StrategicOption(
                    rank=1,
                    title="Continue Current Strategy",
                    description="Maintain your current approach based on available information.",
                    reasoning="Unable to generate specific recommendations at this time.",
                    key_stats={},
                    confidence=0.3
                )
            ]
    
    async def _generate_general_advice(
        self, 
        snapshot: GameSnapshot, 
        context: str
    ) -> str:
        """Generate general strategic advice."""
        
        prompt = f"""Based on the current game state and statistics, provide brief general advice (2-3 sentences) for this TFT player.

{context}

Focus on immediate priorities and key considerations for their current situation."""
        
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a concise TFT coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating general advice: {e}")
            return "Focus on economy and positioning. Make decisions based on your health and lobby strength."
