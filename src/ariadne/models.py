from typing import List, Dict, Tuple, Optional, Literal
from pydantic import BaseModel, Field

class DomainDelta(BaseModel):
    missing_mechanisms: List[str]
    extra_mechanisms: List[str]
    scale_differences: str
    agent_differences: str

class FailureMode(BaseModel):
    description: str
    structural_cause: str
    early_warning_signal: str
    is_recoverable: bool
    failure_type: Literal["known", "transfer", "emergent"]

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
    q_cycle_mappings: Dict[str, str] = {}
    structural_tags: List[str] = []
    delta: Optional[DomainDelta] = None

class Hypothesis(BaseModel):
    source_theory_id: str
    target_domain_name: str
    isomorphism_map: Dict[str, str]
    strategy: str
    explanation: str
    testable_prediction: str
    failure_conditions: List[str]
    failure_modes: List[FailureMode] = []
    falsification_path: str
    structural_similarity: float
    novelty_score: float
    falsifiability_score: float
    final_score: float
