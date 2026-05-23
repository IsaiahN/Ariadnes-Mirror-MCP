import pytest
import os
import json
from unittest.mock import MagicMock, patch
from ariadne.engine import AriadneEngine, cosine_similarity
from ariadne.models import DomainProfile, Hypothesis
import numpy as np

@pytest.fixture(autouse=True)
def setup_env():
    os.environ["OPENROUTER_API_KEY"] = "sk-test"

@pytest.fixture
def engine():
    return AriadneEngine()

def test_jaccard_similarity(engine):
    assert engine.calculate_jaccard_similarity(["a", "b"], ["a", "c"]) == 1/3

def test_cosine_similarity():
    a = [1, 0]
    b = [1, 0]
    assert np.allclose(cosine_similarity(a, b), [[1.0]])

def test_fstar_distance(engine):
    c1 = {"resource_pressure": 0.5, "actor_complexity": 0.5}
    c2 = {"resource_pressure": 0.6, "actor_complexity": 0.4}
    dist = engine._fstar_distance(c1, c2)
    assert 0 < dist < 0.1

def test_stage1_fstar_filter_with_coverage(engine):
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
    candidates = engine.stage1_fstar_filter(profile, top_k=10)
    assert len(candidates) > 0
    # Blueprints should be near the top
    assert any(c.coverage.coverage_type == "blueprint" for c in candidates if c.coverage)
    # Partials should be saved in _current_refiners
    assert hasattr(engine, '_current_refiners')
    assert len(engine._current_refiners) > 0

def test_stage5_refinement(engine):
    profile = DomainProfile(name="T", description="D")
    hypo = Hypothesis(
        source_theory_id="id", target_domain_name="T", isomorphism_map={},
        strategy="s", explanation="e", testable_prediction="original p",
        failure_conditions=[], falsification_path="f",
        structural_similarity=0.8, novelty_score=0.8,
        falsifiability_score=0.8, final_score=0.4,
        active_fstar_dimensions=["information_asymmetry"]
    )

    # Setup a refiner in engine
    partial = next(t for t in engine.theories if t.id == "halting_problem")
    engine._current_refiners = [partial]

    mock_response = json.dumps({
        "sharpened_prediction": "sharpened p",
        "added_constraints": ["c1"],
        "known_unsolvable_subproblems": ["u1"]
    })

    # We patch AIClient class to avoid instantiation error if it hasn't happened yet
    with patch("ariadne.engine.AIClient") as mock_ai_class:
        mock_ai = mock_ai_class.return_value
        mock_ai.get_completion.return_value = mock_response
        # Access engine.ai_client property will now use the mock
        refined = engine.stage5_refine_with_partials(hypo, profile)

    assert refined.testable_prediction == "sharpened p"
    assert "c1" in refined.added_constraints
