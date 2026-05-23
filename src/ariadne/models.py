from typing import List, Dict, Tuple, Optional, Literal
from pydantic import BaseModel, Field

class DistortionProfile(BaseModel):
    # D1: Environmental substrate
    resource_type: str
    resource_dynamics: str
    thermodynamic_regime: str
    physical_constraints: List[str]

    # D2: Actor configuration
    actor_intentionality: str
    actor_count_regime: str
    actor_autonomy: float
    incentive_legibility: float

    # D3: Domain intersections
    boundary_domains: List[str]
    emergent_problems: List[str]
    intersection_type: str

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
    distortion_profile: Optional[DistortionProfile] = None
    scale_level: str = ""
    f_star_coordinates: Optional[Dict[str, float]] = None

class DomainProfile(BaseModel):
    name: str
    description: str
    q_cycle_mappings: Dict[str, str] = {}
    structural_tags: List[str] = []
    delta: Optional[DomainDelta] = None
    distortion_profile: Optional[DistortionProfile] = None
    scale_level: str = ""
    f_star_coordinates: Optional[Dict[str, float]] = None

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
