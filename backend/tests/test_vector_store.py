import pytest
from unittest.mock import Mock, AsyncMock
from app.services.vector_store import VectorStoreService
from app.models.schemas import CompStats, AugmentStats


@pytest.fixture
def vector_store():
    """Create a vector store instance for testing."""
    return VectorStoreService()


def test_add_comp_stats(vector_store):
    """Test adding composition statistics."""
    comp_stats = [
        CompStats(
            comp_name="Test_Comp",
            patch="12.1",
            champions=["Ashe", "Sejuani"],
            avg_placement=3.5,
            play_rate=0.15,
            top4_rate=0.65,
            win_rate=0.20,
            sample_size=100,
            key_augments=["Jeweled Lotus"],
            key_items={"Ashe": ["Guinsoo", "Giant Slayer"]}
        )
    ]
    
    # Should not raise an exception
    vector_store.add_comp_stats(comp_stats)


def test_add_augment_stats(vector_store):
    """Test adding augment statistics."""
    augment_stats = [
        AugmentStats(
            augment_name="Jeweled Lotus",
            patch="12.1",
            pick_rate=0.25,
            avg_placement=3.8,
            top4_rate=0.60,
            win_rate=0.18,
            sample_size=500,
            synergistic_comps=["Test_Comp"]
        )
    ]
    
    # Should not raise an exception
    vector_store.add_augment_stats(augment_stats)


def test_add_playbook(vector_store):
    """Test adding a playbook."""
    title = "Test Strategy"
    content = "This is a test strategic playbook for unit testing."
    tags = ["test", "strategy"]
    
    # Should not raise an exception
    vector_store.add_playbook(title, content, tags)
