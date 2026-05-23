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

def test_kernel_immutability(engine):
    raft = next(t for t in engine.kernel_theories if t.id == "raft_consensus")
    initial_score = raft.credibility_score
    engine.update_credibility("raft_consensus", 5)
    assert raft.credibility_score == initial_score

def test_thread_credibility_ceiling(engine):
    engine.update_credibility("user_theory", 5)
    user = next(t for t in engine.thread_theories if t.id == "user_theory")
    assert user.credibility_score == 0.7

def test_map_fstar_coverage(engine):
    from ariadne.api import map_fstar_coverage
    coverage = map_fstar_coverage()
    assert "coverage_by_dimension" in coverage
    # Based on theories.yaml enrichment
    assert coverage["blueprint_count"] >= 1
