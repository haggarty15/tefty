#!/usr/bin/env python3
"""
Utility script to initialize the TFT Strategic Advisor with playbooks.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store import VectorStoreService


async def load_playbooks():
    """Load all playbooks from the playbooks directory."""
    vector_store = VectorStoreService()
    playbooks_dir = Path(__file__).parent.parent / "data" / "playbooks"
    
    if not playbooks_dir.exists():
        print(f"Playbooks directory not found: {playbooks_dir}")
        return
    
    for playbook_file in playbooks_dir.glob("*.md"):
        print(f"Loading playbook: {playbook_file.name}")
        
        with open(playbook_file, 'r') as f:
            content = f.read()
        
        title = playbook_file.stem.replace('_', ' ').title()
        vector_store.add_playbook(title, content, tags=[playbook_file.stem])
        
        print(f"  ✓ Loaded: {title}")
    
    print("\nPlaybooks loaded successfully!")


if __name__ == "__main__":
    asyncio.run(load_playbooks())
