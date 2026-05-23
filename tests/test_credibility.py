import pytest
import os
import json
from ariadne.engine import AriadneEngine

@pytest.fixture
def engine(tmp_path):
    os.environ["ARIADNE_STORAGE_DIR"] = str(tmp_path)
    from ariadne.config import settings
    settings.storage_dir = str(tmp_path)
    os.makedirs(settings.resolved_storage_dir, exist_ok=True)
    return AriadneEngine()

def test_credibility_logic(engine):
    theory_id = "raft_consensus"
    raft = next(t for t in engine.theories if t.id == theory_id)
    # raft starts at 0.5 because it's a new instance with fresh tmp_path
    initial_score = raft.credibility_score
    initial_uses = raft.n_uses

    assert initial_score == 0.5
    assert initial_uses == 0

    # Rating 5 -> (0.5*0 + 1.0) / (0+1) = 1.0
    engine.update_credibility(theory_id, 5)
    assert raft.n_uses == 1
    assert raft.credibility_score == 1.0

    # Rating 1 -> (1.0*1 + 0.0) / (1+1) = 0.5
    engine.update_credibility(theory_id, 1)
    assert raft.n_uses == 2
    assert raft.credibility_score == 0.5

    # Check persistence
    state_file = os.path.join(engine.storage_dir, "theory_state.json")
    with open(state_file, 'r') as f:
        state = json.load(f)
        assert state[theory_id]["credibility_score"] == 0.5

def test_invalid_rating(engine):
    with pytest.raises(ValueError):
        engine.update_credibility("raft_consensus", 6)

def test_missing_theory(engine):
    with pytest.raises(KeyError):
        engine.update_credibility("non_existent", 3)
