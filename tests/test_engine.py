import pytest
import os
from ariadne.engine import AriadneEngine
from ariadne.models import DomainProfile

@pytest.fixture
def engine():
    return AriadneEngine()

def test_jaccard_similarity(engine):
    assert engine.calculate_jaccard_similarity(["a", "b"], ["a", "c"]) == 1/3
    assert engine.calculate_jaccard_similarity(["a", "b"], ["a", "b"]) == 1.0
    assert engine.calculate_jaccard_similarity(["a"], ["b"]) == 0.0
    assert engine.calculate_jaccard_similarity([], ["a"]) == 0.0

def test_cosine_similarity():
    from ariadne.engine import cosine_similarity
    import numpy as np
    a = [1, 0]
    b = [1, 0]
    assert np.allclose(cosine_similarity(a, b), [[1.0]])

    a = [1, 0]
    b = [0, 1]
    assert np.allclose(cosine_similarity(a, b), [[0.0]])

def test_stage1_filter(engine):
    target_tags = ["hierarchical", "peer-to-peer"]
    candidates = engine.stage1_filter(target_tags, top_k=5)
    assert len(candidates) > 0
    assert any(t.id == "raft_consensus" for t in candidates)

def test_theory_loading(engine):
    assert len(engine.theories) > 10
    raft = next(t for t in engine.theories if t.id == "raft_consensus")
    assert raft.name == "Raft Consensus Algorithm"
    assert "Leader" in raft.structural_topology.roles
