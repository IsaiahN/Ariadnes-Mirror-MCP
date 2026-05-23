import pytest
from ariadne.engine import AriadneEngine
import os
import json

@pytest.fixture
def engine(tmp_path):
    # Setup temporary storage
    os.environ["ARIADNE_STORAGE_DIR"] = str(tmp_path)
    from ariadne.config import settings
    # Force reload of settings if needed, but here we just ensure the dir exists
    os.makedirs(settings.resolved_storage_dir, exist_ok=True)
    return AriadneEngine()

def test_credibility_logic(engine):
    theory_id = "raft_consensus"
    raft = next(t for t in engine.theories if t.id == theory_id)
    initial_score = raft.credibility_score
    initial_uses = raft.n_uses

    # Rating 5
    engine.update_credibility(theory_id, 5)
    assert raft.n_uses == initial_uses + 1
    assert raft.credibility_score > initial_score

    # Check persistence
    state_file = os.path.join(engine.storage_dir, "theory_state.json")
    with open(state_file, 'r') as f:
        state = json.load(f)
        assert state[theory_id]["credibility_score"] == raft.credibility_score

def test_invalid_rating(engine):
    with pytest.raises(ValueError):
        engine.update_credibility("raft_consensus", 6)

def test_missing_theory(engine):
    with pytest.raises(KeyError):
        engine.update_credibility("non_existent", 3)
