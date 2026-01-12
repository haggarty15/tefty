import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import logging

from app.core.config import settings
from app.models.schemas import CompStats, AugmentStats

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing vector database for RAG."""
    
    def __init__(self):
        self.persist_directory = Path(settings.chroma_persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Create collections
        self.comp_collection = self.client.get_or_create_collection(
            name="compositions",
            metadata={"description": "Team composition statistics"}
        )
        
        self.augment_collection = self.client.get_or_create_collection(
            name="augments",
            metadata={"description": "Augment statistics"}
        )
        
        self.playbook_collection = self.client.get_or_create_collection(
            name="playbooks",
            metadata={"description": "Strategic playbooks"}
        )
    
    def add_comp_stats(self, comp_stats: List[CompStats]):
        """Add composition statistics to vector store."""
        documents = []
        metadatas = []
        ids = []
        
        for i, comp in enumerate(comp_stats):
            # Create a text representation for embedding
            doc_text = (
                f"Team composition: {', '.join(comp.champions)}. "
                f"Patch {comp.patch}. "
                f"Average placement: {comp.avg_placement:.2f}. "
                f"Top 4 rate: {comp.top4_rate:.1%}. "
                f"Win rate: {comp.win_rate:.1%}. "
                f"Key augments: {', '.join(comp.key_augments)}. "
                f"Sample size: {comp.sample_size} games."
            )
            
            documents.append(doc_text)
            metadatas.append({
                "comp_name": comp.comp_name,
                "patch": comp.patch,
                "avg_placement": comp.avg_placement,
                "top4_rate": comp.top4_rate,
                "win_rate": comp.win_rate,
                "champions": json.dumps(comp.champions),
                "key_augments": json.dumps(comp.key_augments)
            })
            ids.append(f"comp_{comp.patch}_{i}")
        
        if documents:
            self.comp_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} composition stats to vector store")
    
    def add_augment_stats(self, augment_stats: List[AugmentStats]):
        """Add augment statistics to vector store."""
        documents = []
        metadatas = []
        ids = []
        
        for i, augment in enumerate(augment_stats):
            doc_text = (
                f"Augment: {augment.augment_name}. "
                f"Patch {augment.patch}. "
                f"Pick rate: {augment.pick_rate:.1%}. "
                f"Average placement: {augment.avg_placement:.2f}. "
                f"Top 4 rate: {augment.top4_rate:.1%}. "
                f"Win rate: {augment.win_rate:.1%}. "
                f"Works well with: {', '.join(augment.synergistic_comps)}. "
                f"Sample size: {augment.sample_size} games."
            )
            
            documents.append(doc_text)
            metadatas.append({
                "augment_name": augment.augment_name,
                "patch": augment.patch,
                "pick_rate": augment.pick_rate,
                "avg_placement": augment.avg_placement,
                "top4_rate": augment.top4_rate,
                "win_rate": augment.win_rate
            })
            ids.append(f"augment_{augment.patch}_{i}")
        
        if documents:
            self.augment_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} augment stats to vector store")
    
    def add_playbook(self, title: str, content: str, tags: List[str] = None):
        """Add a strategic playbook to vector store."""
        tags = tags or []
        
        self.playbook_collection.add(
            documents=[content],
            metadatas=[{
                "title": title,
                "tags": json.dumps(tags)
            }],
            ids=[f"playbook_{title.lower().replace(' ', '_')}"]
        )
        logger.info(f"Added playbook: {title}")
    
    def query_compositions(
        self, 
        query: str, 
        n_results: int = 5,
        patch_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query for relevant compositions."""
        where_filter = {"patch": patch_filter} if patch_filter else None
        
        results = self.comp_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        return self._format_results(results)
    
    def query_augments(
        self, 
        query: str, 
        n_results: int = 5,
        patch_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query for relevant augments."""
        where_filter = {"patch": patch_filter} if patch_filter else None
        
        results = self.augment_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        return self._format_results(results)
    
    def query_playbooks(
        self, 
        query: str, 
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Query for relevant playbooks."""
        results = self.playbook_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return self._format_results(results)
    
    def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format ChromaDB results into a list of dictionaries."""
        formatted = []
        
        if not results or not results.get("documents"):
            return formatted
        
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results.get("distances", [[]])[0]
        
        for i, doc in enumerate(documents):
            formatted.append({
                "document": doc,
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "distance": distances[i] if i < len(distances) else None
            })
        
        return formatted
