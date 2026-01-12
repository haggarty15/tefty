#!/usr/bin/env python3
"""
Sample data generator for testing the TFT Strategic Advisor.
Creates mock statistics and playbooks for testing without real API data.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store import VectorStoreService
from app.models.schemas import CompStats, AugmentStats


def create_sample_data():
    """Create sample composition and augment statistics."""
    vector_store = VectorStoreService()
    
    print("Creating sample composition statistics...")
    
    sample_comps = [
        CompStats(
            comp_name="Reroll_Ashe",
            patch="12.1",
            champions=["Ashe", "Sejuani", "Lissandra", "Syndra", "Neeko"],
            avg_placement=3.2,
            play_rate=0.15,
            top4_rate=0.68,
            win_rate=0.22,
            sample_size=250,
            key_augments=["Cybernetic Implants", "Jeweled Lotus"],
            key_items={
                "Ashe": ["Guinsoo's Rageblade", "Giant Slayer", "Last Whisper"],
                "Sejuani": ["Warmog's Armor", "Bramble Vest"]
            }
        ),
        CompStats(
            comp_name="Fast8_Ahri",
            patch="12.1",
            champions=["Ahri", "Syndra", "Lissandra", "Neeko", "Twisted Fate", "Janna"],
            avg_placement=3.5,
            play_rate=0.12,
            top4_rate=0.62,
            win_rate=0.18,
            sample_size=180,
            key_augments=["Preparation", "Level Up!", "Rich Get Richer"],
            key_items={
                "Ahri": ["Jeweled Gauntlet", "Spear of Shojin", "Blue Buff"],
                "Syndra": ["Morellonomicon", "Archangel's Staff"]
            }
        ),
        CompStats(
            comp_name="Flex_Bruiser",
            patch="12.1",
            champions=["Sett", "Vi", "Sejuani", "Illaoi", "Rek'Sai"],
            avg_placement=4.1,
            play_rate=0.18,
            top4_rate=0.55,
            win_rate=0.14,
            sample_size=320,
            key_augments=["Bruiser Heart", "Component Grab Bag"],
            key_items={
                "Sett": ["Bloodthirster", "Titan's Resolve", "Quicksilver"],
                "Sejuani": ["Warmog's Armor", "Sunfire Cape"]
            }
        ),
    ]
    
    vector_store.add_comp_stats(sample_comps)
    print(f"  ✓ Added {len(sample_comps)} composition statistics")
    
    print("\nCreating sample augment statistics...")
    
    sample_augments = [
        AugmentStats(
            augment_name="Jeweled Lotus",
            patch="12.1",
            pick_rate=0.28,
            avg_placement=3.4,
            top4_rate=0.64,
            win_rate=0.20,
            sample_size=450,
            synergistic_comps=["Reroll_Ashe", "Fast8_Ahri"]
        ),
        AugmentStats(
            augment_name="Cybernetic Implants",
            patch="12.1",
            pick_rate=0.22,
            avg_placement=3.2,
            top4_rate=0.68,
            win_rate=0.22,
            sample_size=380,
            synergistic_comps=["Reroll_Ashe"]
        ),
        AugmentStats(
            augment_name="Preparation",
            patch="12.1",
            pick_rate=0.25,
            avg_placement=3.6,
            top4_rate=0.61,
            win_rate=0.17,
            sample_size=420,
            synergistic_comps=["Fast8_Ahri"]
        ),
        AugmentStats(
            augment_name="Level Up!",
            patch="12.1",
            pick_rate=0.18,
            avg_placement=3.7,
            top4_rate=0.60,
            win_rate=0.16,
            sample_size=310,
            synergistic_comps=["Fast8_Ahri", "Flex_Bruiser"]
        ),
    ]
    
    vector_store.add_augment_stats(sample_augments)
    print(f"  ✓ Added {len(sample_augments)} augment statistics")
    
    print("\n✅ Sample data created successfully!")
    print("\nYou can now use the application with this sample data.")
    print("To add real data, use the Riot API ingestion endpoints.")


if __name__ == "__main__":
    create_sample_data()
