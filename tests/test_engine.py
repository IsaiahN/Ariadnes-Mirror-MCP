import pytest
import os
from ariadne.engine import AriadneEngine, cosine_similarity
from ariadne.models import DomainProfile
import numpy as np

@pytest.fixture
def engine():
    return AriadneEngine()

def test_jaccard_similarity(engine):
    assert engine.calculate_jaccard_similarity(["a", "b"], ["a", "c"]) == 1/3
    assert engine.calculate_jaccard_similarity(["a", "b"], ["a", "b"]) == 1.0
    assert engine.calculate_jaccard_similarity(["a"], ["b"]) == 0.0
    assert engine.calculate_jaccard_similarity([], ["a"]) == 0.0

def test_cosine_similarity():
    a = [1, 0]
    b = [1, 0]
    assert np.allclose(cosine_similarity(a, b), [[1.0]])

    a = [1, 0]
    b = [0, 1]
    assert np.allclose(cosine_similarity(a, b), [[0.0]])

def test_fstar_distance(engine):
    c1 = {"resource_pressure": 0.5, "actor_complexity": 0.5}
    c2 = {"resource_pressure": 0.6, "actor_complexity": 0.4}
    # (0.1^2 + 0.1^2 + 0+0+0+0) / 6 = 0.02 / 6 = 0.0033...
    # sqrt(0.0033) approx 0.057
    dist = engine._fstar_distance(c1, c2)
    assert 0 < dist < 0.1

    # Same coords
    assert engine._fstar_distance(c1, c1) == 0.0

def test_stage1_fstar_filter(engine):
    # Create profile with F* coords similar to Raft (0.7, 0.1, 0.8, 0.9, 0.8, 0.2)
    profile = DomainProfile(
        name="T", description="D",
        f_star_coordinates={
            "resource_pressure": 0.7,
            "actor_complexity": 0.1,
            "information_asymmetry": 0.8,
            "coupling_tightness": 0.9,
            "time_pressure": 0.8,
            "boundary_permeability": 0.2
        }
    )
    candidates = engine.stage1_fstar_filter(profile, top_k=5)
    assert len(candidates) > 0
    # Raft should be #1
    assert candidates[0].id == "raft_consensus"

def test_theory_loading(engine):
    raft = next(t for t in engine.theories if t.id == "raft_consensus")
    assert raft.f_star_coordinates is not None
    assert raft.f_star_coordinates["resource_pressure"] == 0.7
