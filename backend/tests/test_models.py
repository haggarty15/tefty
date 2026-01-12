import pytest
from app.models.schemas import GameSnapshot, Champion, TFTSet


def test_game_snapshot_creation():
    """Test creating a game snapshot."""
    snapshot = GameSnapshot(
        set_version=TFTSet.SET_12,
        stage="4-2",
        level=7,
        gold=30,
        health=60,
        board=[
            Champion(name="Ashe", stars=2, items=["Guinsoo", "Giant Slayer"])
        ],
        bench=[],
        active_traits=["Evoker"],
        available_augments=["Jeweled Lotus"],
        shop_champions=["Ahri", "Syndra"]
    )
    
    assert snapshot.level == 7
    assert len(snapshot.board) == 1
    assert snapshot.board[0].name == "Ashe"
    assert snapshot.board[0].stars == 2


def test_champion_creation():
    """Test creating a champion."""
    champ = Champion(
        name="Ashe",
        stars=2,
        items=["Guinsoo", "Giant Slayer"]
    )
    
    assert champ.name == "Ashe"
    assert champ.stars == 2
    assert len(champ.items) == 2


def test_snapshot_validation():
    """Test snapshot field validation."""
    with pytest.raises(ValueError):
        # Level must be between 1 and 10
        GameSnapshot(
            set_version=TFTSet.SET_12,
            stage="4-2",
            level=11,  # Invalid
            gold=30,
            health=60
        )


def test_champion_star_validation():
    """Test champion star validation."""
    with pytest.raises(ValueError):
        # Stars must be between 1 and 3
        Champion(name="Ashe", stars=4, items=[])
