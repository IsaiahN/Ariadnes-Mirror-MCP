import pytest
import json
from unittest.mock import MagicMock, patch
from ariadne.engine import AriadneEngine
from ariadne.models import DomainProfile, DomainDelta, Hypothesis

@pytest.fixture
def engine():
    with patch("ariadne.engine.AIClient") as mock_ai:
        eng = AriadneEngine()
        yield eng

def test_stage4_failure_analysis(engine):
    profile = DomainProfile(
        name="Test Domain",
        description="Desc",
        delta=DomainDelta(
            missing_mechanisms=["m1"],
            extra_mechanisms=["e1"],
            scale_differences="scale",
            agent_differences="agents"
        )
    )
    theory = engine.theories[0]
    hypo = Hypothesis(
        source_theory_id=theory.id,
        target_domain_name=profile.name,
        isomorphism_map={"a": "b"},
        strategy="s",
        explanation="e",
        testable_prediction="p",
        failure_conditions=[],
        falsification_path="f",
        structural_similarity=0.8,
        novelty_score=0.8,
        falsifiability_score=0.8,
        final_score=0.4
    )

    mock_response = json.dumps([{
        "description": "emergent failure",
        "structural_cause": "cause",
        "early_warning_signal": "signal",
        "is_recoverable": True,
        "failure_type": "emergent"
    }])

    with patch.object(engine.ai_client, 'get_completion', return_value=mock_response):
        failures = engine.stage4_failure_analysis(profile, theory, hypo)

    assert len(failures) == 1
    assert failures[0].description == "emergent failure"
    assert failures[0].failure_type == "emergent"

def test_analyze_integration(engine):
    profile = DomainProfile(name="T", description="D")

    with patch.object(engine, 'stage1_filter', return_value=[engine.theories[0]]),          patch.object(engine, 'stage2_embedding_similarity', return_value=[engine.theories[0]]),          patch.object(engine, 'stage3_llm_comparison') as mock_s3,          patch.object(engine, 'stage4_failure_analysis') as mock_s4:

         mock_s3.return_value = Hypothesis(
            source_theory_id="id", target_domain_name="T", isomorphism_map={},
            strategy="s", explanation="e", testable_prediction="p",
            failure_conditions=[], falsification_path="f",
            structural_similarity=0.8, novelty_score=0.8,
            falsifiability_score=0.8, final_score=0.4
         )
         mock_s4.return_value = []

         hypos = engine.analyze(profile)
         assert len(hypos) == 1
         mock_s4.assert_called_once()
