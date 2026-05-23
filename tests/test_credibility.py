import pytest
import os
import json
from ariadne.engine import AriadneEngine
import ariadne.config

@pytest.fixture
def engine(tmp_path, monkeypatch):
    storage_dir = str(tmp_path)
    monkeypatch.setattr(ariadne.config.settings, "storage_dir", storage_dir)

    # Mocking a thread theory
    thread_dir = os.path.join(storage_dir, "threads", "default", "theories")
    os.makedirs(thread_dir, exist_ok=True)
    with open(os.path.join(thread_dir, "user_theory.yaml"), "w") as f:
        f.write("id: user_theory\nname: User Theory\ndomain: Test\ndescription: D\nstructural_tags: []\nstructural_topology: {roles: [], directionality: '', feedback_loops: '', scale: '', time_horizon: ''}\nfalsifiability_note: ''\nkey_refs: []\nknown_failure_modes: []")

    return AriadneEngine()

def test_credibility_logic(engine):
    theory_id = "user_theory"
    theory = next(t for t in engine.thread_theories if t.id == theory_id)
    initial_score = theory.credibility_score
    initial_uses = theory.n_uses

    assert initial_score == 0.5
    assert initial_uses == 0

    # Rating 5 -> (0.5*0 + 1.0) / (0+1) = 1.0, capped at 0.7
    engine.update_credibility(theory_id, 5)
    assert theory.n_uses == 1
    assert theory.credibility_score == 0.7

    # Rating 1 -> (0.7*1 + 0.0) / (1+1) = 0.35
    engine.update_credibility(theory_id, 1)
    assert theory.n_uses == 2
    assert theory.credibility_score == 0.35

def test_invalid_rating(engine):
    with pytest.raises(ValueError):
        engine.update_credibility("user_theory", 6)

def test_missing_theory(engine):
    with pytest.raises(KeyError):
        engine.update_credibility("non_existent", 3)
