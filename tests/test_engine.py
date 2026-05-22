import pytest
from ariadne.engine import AriadneEngine
from ariadne.models import DomainProfile

def test_jaccard_similarity():
    engine = AriadneEngine("data/theories.yaml")
    assert engine.calculate_jaccard_similarity(["a", "b"], ["a", "c"]) == 1/3
    assert engine.calculate_jaccard_similarity(["a", "b"], ["a", "b"]) == 1.0
    assert engine.calculate_jaccard_similarity(["a"], ["b"]) == 0.0
    assert engine.calculate_jaccard_similarity([], ["a"]) == 0.0

def test_stage1_filter():
    engine = AriadneEngine("data/theories.yaml")
    # All theories have some tags, let's pick some that match Raft
    target_tags = ["hierarchical", "peer-to-peer"]
    candidates = engine.stage1_filter(target_tags, top_k=5)
    assert len(candidates) > 0
    # Raft should be among the top candidates
    assert any(t.id == "raft_consensus" for t in candidates)

def test_analyze():
    engine = AriadneEngine("data/theories.yaml")
    profile = DomainProfile(
        name="Content Moderation",
        description="Scaling trust and safety",
        structural_tags=["distributed", "regulatory", "adversarial"]
    )
    hypotheses = engine.analyze(profile)
    assert len(hypotheses) > 0
    assert hypotheses[0].target_domain_name == "Content Moderation"
    assert hypotheses[0].testable_prediction is not None
