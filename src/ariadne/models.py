from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel, Field

class StructuralTopology(BaseModel):
    roles: List[str]
    directionality: str
    feedback_loops: str
    scale: str
    time_horizon: str

class Theory(BaseModel):
    id: str
    name: str
    domain: str
    description: str
    structural_tags: List[str]
    structural_topology: StructuralTopology
    falsifiability_note: str
    key_refs: List[str]
    known_failure_modes: List[str]
    credibility_score: float = 0.5
    n_uses: int = 0

class DomainProfile(BaseModel):
    name: str
    description: str
    meta_components: Dict[str, str] = {}
    q_cycle_mappings: Dict[str, str] = {}
    structural_tags: List[str] = []

class Hypothesis(BaseModel):
    source_theory_id: str
    target_domain_name: str
    isomorphism_map: Dict[str, str]
    strategy: str
    explanation: str
    testable_prediction: str
    failure_conditions: List[str]
    falsification_path: str
    structural_similarity: float
    novelty_score: float
    falsifiability_score: float
    final_score: float
    confidence_interval: Tuple[float, float]
