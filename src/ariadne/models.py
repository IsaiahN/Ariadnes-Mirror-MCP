from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field

class ScaleLevel(BaseModel):
    name: str  # "subatomic", "cellular", "organism", "social", "institutional", "civilizational"
    typical_actor_intentionality: float
    typical_time_horizon: str
    typical_resource_type: str
    typical_coupling: float
    invariant_questions: List[str]
    invariant_tensions: List[str]

class TheoryCoverage(BaseModel):
    coverage_type: Literal["partial", "framework", "blueprint"]
    fstar_dimensions_covered: List[str]
    breadth_score: float
    depth_score: float
    novel_concepts: List[str]
    convergent_discoveries: List[Dict[str, str]]
    fstar_refinements: List[str]

class ResidueComponent(BaseModel):
    description: str
    appears_in_other_theories: List[str]
    domain_of_origin: str
    has_formal_theory: bool
    closest_formal_theory: Optional[str]
    candidate_theory_name: Optional[str]
    candidate_theory_description: Optional[str]
    potential_applications: List[str]
    fstar_coordinates: Optional[Dict[str, float]]

class SubtractiveAnalysis(BaseModel):
    theory_id: str
    blueprint_used: str
    residue_components: List[ResidueComponent]

class InterfaceSpec(BaseModel):
    domain: str
    interface_requirements: List[str]
    must_expose: List[str]
    must_accept: List[str]
    must_encapsulate: List[str]
    exchange_protocol: str
    failure_modes: List[str]

class AnalogResolution(BaseModel):
    domain: str
    scale: str
    solution: str
    proven: bool
    mechanism: str
    transposition_delta: str

class DomainIntersection(BaseModel):
    domain_a: str
    domain_b: str
    domain_a_contributions: List[str]
    domain_b_contributions: List[str]
    domain_a_solved_problems: List[str]
    domain_b_solved_problems: List[str]
    core_tension: str
    tension_fstar_coordinates: Dict[str, float]
    subsidiary_tensions: List[str]
    analog_domains: List[AnalogResolution]
    interface_a_side: InterfaceSpec
    interface_b_side: InterfaceSpec
    invariant_transferrables: List[str]

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
    coverage: Optional[TheoryCoverage] = None

class DomainProfile(BaseModel):
    name: str
    description: str
    q_cycle_mappings: Dict[str, str] = {}
    structural_tags: List[str] = []
    delta: Optional[DomainDelta] = None
    distortion_profile: Optional[DistortionProfile] = None
    scale_level: str = ""
    f_star_coordinates: Optional[Dict[str, float]] = None

class KernelTheory(BaseModel):
    theory: Theory
    kernel_version: str
    content_hash: str
    inclusion_rationale: str
    validation_evidence: List[str]
    independent_derivation_record: Optional[str] = None

class KernelManifest(BaseModel):
    version: str
    theories: List[KernelTheory]
    manifest_hash: str
    primary_blueprints: List[str]
    known_fstar_gaps: List[str]
    curator_notes: str

class Thread(BaseModel):
    id: str
    name: str
    description: str
    domain_focus: Optional[str] = None
    created_at: str
    theories: List[Theory] = []
    credibility_state: Dict[str, float] = {}
    session_paths: List[str] = []
    residues: List[ResidueComponent] = []
    max_credibility: float = 0.7

class UserLibrary(BaseModel):
    threads: Dict[str, Thread]
    active_thread_id: str
    global_theories: List[Theory] = []
    global_credibility: Dict[str, float] = {}

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
    active_fstar_dimensions: List[str] = []
    added_constraints: List[str] = []
    known_unsolvable_subproblems: List[str] = []
    structural_similarity: float
    novelty_score: float
    falsifiability_score: float
    final_score: float
