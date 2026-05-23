import yaml
import datetime
import json
import os
import pickle
import re
import numpy as np
from typing import List, Optional, Dict
from importlib import resources
from .models import Theory, DomainProfile, Hypothesis, FailureMode, DistortionProfile, SubtractiveAnalysis, DomainIntersection
from .persistence import TheoryStateManager, ThreadStateManager
from .config import settings
from .ai import AIClient
from .kernel import KernelManager

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    if a.ndim == 1:
        a = a.reshape(1, -1)
    if b.ndim == 1:
        b = b.reshape(1, -1)

    norm_a = np.linalg.norm(a, axis=1, keepdims=True)
    norm_b = np.linalg.norm(b, axis=1, keepdims=True)

    return np.dot(a, b.T) / (norm_a * norm_b.T)

class AriadneEngine:
    def __init__(self, thread_id: str = "default"):
        kernel_dir = os.path.join(os.path.dirname(__file__), 'kernel')
        self.kernel = KernelManager(kernel_dir)
        self.thread_manager = ThreadStateManager(thread_id)
        self.state_manager = TheoryStateManager()
        self._ai_client = None

        # Load all
        self.kernel_theories = self._enrich_theories(self.kernel.theories)
        self.thread_theories = self._enrich_theories(self.thread_manager.load_theories())

        self.storage_dir = settings.resolved_storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def _enrich_theories(self, theories: List[Theory]) -> List[Theory]:
        for theory in theories:
            state = self.state_manager.get_theory_state(theory.id)
            theory.credibility_score = state["credibility_score"]
            theory.n_uses = state["n_uses"]
        return theories

    @property
    def theories(self) -> List[Theory]:
        return self.kernel_theories + self.thread_theories

    def calculate_jaccard_similarity(self, tags1: List[str], tags2: List[str]) -> float:
        set1, set2 = set(tags1), set(tags2)
        if not set1 or not set2:
            return 0.0
        return len(set1.intersection(set2)) / len(set1.union(set2))

    def stage1_filter(self, target_tags: List[str], top_k: int = 20) -> List[Theory]:
        """Coarse structural filter using Jaccard similarity on tags."""
        scored_theories = []
        for theory in self.theories:
            score = self.calculate_jaccard_similarity(target_tags, theory.structural_tags)
            scored_theories.append((score, theory))

        scored_theories.sort(key=lambda x: x[0], reverse=True)
        return [t for s, t in scored_theories[:top_k]]

    def _get_theory_embeddings(self, theories: List[Theory]) -> np.ndarray:
        model_name = settings.openrouter_embedding_model.replace("/", "_")
        cache_path = os.path.join(self.storage_dir, f"embeddings_{model_name}.pkl")
        cache = {}
        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                cache = pickle.load(f)

        theory_texts = {t.id: f"Theory: {t.name}\nDomain: {t.domain}\nDescription: {t.description}\nTags: {', '.join(t.structural_tags)}" for t in theories}

        to_embed = []
        ids_to_embed = []
        for tid, text in theory_texts.items():
            if tid not in cache:
                to_embed.append(text)
                ids_to_embed.append(tid)

        if to_embed:
            new_embeddings = self.ai_client.get_embeddings(to_embed)
            for tid, emb in zip(ids_to_embed, new_embeddings):
                cache[tid] = emb

            with open(cache_path, 'wb') as f:
                pickle.dump(cache, f)

        return np.array([cache[t.id] for t in theories])

    def stage2_embedding_similarity(self, target_profile: DomainProfile, candidates: List[Theory], top_k: int = 10) -> List[Theory]:
        """
        Stage 2: Semantic similarity using real embeddings via OpenRouter with local caching.
        """
        if not candidates:
            return []

        target_text = f"Target Domain: {target_profile.name}\nDescription: {target_profile.description}\nAnswers: {json.dumps(target_profile.q_cycle_mappings)}"

        try:
            theory_embeddings = self._get_theory_embeddings(candidates)
            target_embedding = np.array(self.ai_client.get_embeddings([target_text])[0]).reshape(1, -1)

            similarities = cosine_similarity(target_embedding, theory_embeddings).flatten()

            scored_candidates = sorted(zip(similarities, candidates), key=lambda x: x[0], reverse=True)
            return [t for s, t in scored_candidates[:top_k]]
        except Exception as e:
            print(f"Error during embedding similarity: {e}")
            return candidates[:top_k] # Fallback

    def update_credibility(self, theory_id: str, rating: float):
        """
        Bayesian update for theory credibility.
        Kernel theories are immutable. Thread theories capped at 0.7.
        """
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5.")

        # Check if kernel
        if any(t.id == theory_id for t in self.kernel_theories):
            self._save_usage_log(theory_id, rating)
            return

        theory = next((t for t in self.thread_theories if t.id == theory_id), None)
        if not theory:
            raise KeyError(f"Theory with ID '{theory_id}' not found.")

        normalized_rating = (rating - 1) / 4.0
        n = theory.n_uses
        current_score = theory.credibility_score

        new_score = min(0.7, (current_score * n + normalized_rating) / (n + 1))

        theory.credibility_score = new_score
        theory.n_uses += 1

        self.state_manager.update_theory_state(theory_id, new_score, theory.n_uses)
        self._save_usage_log(theory_id, rating)

    def _save_usage_log(self, theory_id: str, rating: float):
        log_path = os.path.join(self.storage_dir, "usage_log.jsonl")
        log_entry = {
            "theory_id": theory_id,
            "rating": rating,
            "timestamp": datetime.datetime.now().isoformat()
        }
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

    def stage3_llm_comparison(self, target_profile: DomainProfile, theory: Theory) -> Hypothesis:
        """
        Stage 3: LLM structural comparison.
        This constructs the prompt and makes a real call to OpenRouter.
        """
        prompt = f"""
You are an expert in systems theory and structural isomorphism.
Compare the following two systems for deep structural similarities.

TARGET DOMAIN:
Name: {target_profile.name}
Description: {target_profile.description}
Meta-components (Q-Cycle Answers): {json.dumps(target_profile.q_cycle_mappings, indent=2)}

SOURCE THEORY:
Name: {theory.name}
Description: {theory.description}
Topology: {json.dumps(theory.structural_topology.model_dump(), indent=2)}

Evaluate on these dimensions (1-10 each):
1. Role isomorphism: Do the actors play analogous roles?
2. Memory/state isomorphism: Does information accumulate and decay similarly?
3. Valence isomorphism: Are the incentive structures analogous?
4. Transition isomorphism: Do phase transitions occur via analogous mechanisms?
5. Feedback topology: Are the feedback loops structurally similar?

OUTPUT JSON format:
{{
  "isomorphism_map": {{"source_role": "target_role"}},
  "strategy": "Actionable strategy statement",
  "explanation": "Detailed structural reasoning",
  "testable_prediction": "Specific measurable quantity and direction",
  "failure_conditions": ["Condition 1", "Condition 2"],
  "falsification_path": "How to prove this hypothesis wrong",
  "role_score": 8,
  "memory_score": 7,
  "valence_score": 9,
  "transition_score": 6,
  "feedback_score": 8,
  "overall_score": 7.6,
  "novelty_score": 0.8,
  "falsifiability_score": 0.9
}}
"""
        try:
            response = self.ai_client.get_completion(prompt, system_prompt="You are a system scientist.")
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in LLM response")

            data = json.loads(json_match.group())

            structural_similarity = data["overall_score"] / 10.0
            novelty_score = data["novelty_score"]
            falsifiability_score = data["falsifiability_score"]

            # final_score = (structural_similarity * 0.5 + novelty_score * 0.25 + falsifiability_score * 0.25) * theory.credibility_score
            final_score = (structural_similarity * 0.5 + novelty_score * 0.25 + falsifiability_score * 0.25) * theory.credibility_score

            active_dims = [dim for dim, score in [
                ("resource_pressure", data.get("resource_score", 0)),
                ("actor_complexity", data.get("actor_score", 0)),
                ("information_asymmetry", data.get("memory_score", 0)),
                ("coupling_tightness", data.get("feedback_score", 0)),
                ("time_pressure", data.get("transition_score", 0))
            ] if score > 7]

            return Hypothesis(
                source_theory_id=theory.id,
                target_domain_name=target_profile.name,
                isomorphism_map=data["isomorphism_map"],
                strategy=data["strategy"],
                explanation=data["explanation"],
                testable_prediction=data["testable_prediction"],
                failure_conditions=data["failure_conditions"],
                falsification_path=data["falsification_path"],
                active_fstar_dimensions=active_dims,
                structural_similarity=structural_similarity,
                novelty_score=novelty_score,
                falsifiability_score=falsifiability_score,
                final_score=final_score
            )
        except Exception as e:
            print(f"Error during LLM comparison for {theory.name}: {e}")
            # Fallback
            return Hypothesis(
                source_theory_id=theory.id,
                target_domain_name=target_profile.name,
                isomorphism_map={},
                strategy="N/A",
                explanation=f"Error during LLM call: {e}",
                testable_prediction="N/A",
                failure_conditions=[],
                falsification_path="N/A",
                structural_similarity=0.0,
                novelty_score=0.0,
                falsifiability_score=0.0,
                final_score=0.0
            )

    @property
    def ai_client(self):
        if self._ai_client is None:
            self._ai_client = AIClient()
        return self._ai_client

    def stage4_failure_analysis(self, target_profile: DomainProfile, theory: Theory, hypothesis: Hypothesis) -> List[FailureMode]:
        """
        Stage 4: Emergent Failure Analysis.
        Identifies risks that arise specifically from the mismatch between source and target.
        """
        prompt = f"""
You are a systems safety analyst specializing in theory transfer failures.
You have proposed that '{theory.name}' transfers structurally to '{target_profile.name}'.

KNOWN failures of {theory.name} in its ORIGINAL context:
{theory.known_failure_modes}

DOMAIN DELTA (Differences between target and source context):
{target_profile.delta.model_dump_json(indent=2) if target_profile.delta else "Not provided"}

ISOMORPHISM MAP from Stage 3:
{json.dumps(hypothesis.isomorphism_map, indent=2)}

Your task: identify failure modes that are EMERGENT — meaning they:
1. Do not appear in the known failure list above.
2. Arise specifically because this theory is being applied OUTSIDE its original context.
3. Are caused by structural properties the target domain has that the source theory does NOT model.

For each emergent failure, output a JSON object with:
- description: clear explanation of the failure
- structural_cause: which mismatch or delta produces this
- early_warning_signal: observable signal in the target domain
- is_recoverable: boolean
- failure_type: "emergent" (or "transfer" if it's a stretch failure)

Output ONLY a JSON list of objects.
"""
        try:
            response = self.ai_client.get_completion(prompt, system_prompt="You are a safety systems analyst.")
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                modes_data = json.loads(json_match.group())
                return [FailureMode(**m) for m in modes_data]
            return []
        except Exception as e:
            print(f"Error during Stage 4 failure analysis for {theory.name}: {e}")
            return []

    def stage0_distortion_analysis(self, target_profile: DomainProfile) -> DomainProfile:
        """
        Stage 0: Strip domain-specific distortions to find F* coordinates.
        Allows comparison across domains that share deep structure but look different.
        """
        prompt = f"""
You are analyzing a domain to find its position on the underlying domain-agnostic coordination framework F*.

F* is the perfect isomorph of all coordination problems:
any system of bounded agents managing shared resources under uncertainty is a distorted expression of F*.

DOMAIN: {target_profile.name}
DESCRIPTION: {target_profile.description}
Q-CYCLE ANSWERS: {json.dumps(target_profile.q_cycle_mappings, indent=2)}

Three forces distort F* into domain-specific expressions:
D1 (Environmental Substrate): What physical/informational constraints shape this domain? What is fundamentally scarce?
D2 (Actor Configuration): What is the intentionality level of actors? (pure reflex → strategic) How many? How autonomous?
D3 (Domain Intersections): What other domains does this touch? What emergent problems arise?

Identify these distortions and then strip them away to find the pure coordination problem underneath.
Express this as F* coordinates (0.0 to 1.0):
- resource_pressure: 0 (abundant) to 1 (existential scarcity)
- actor_complexity: 0 (pure reflex) to 1 (full strategic intentionality)
- information_asymmetry: 0 (perfect information) to 1 (complete opacity)
- coupling_tightness: 0 (loosely coupled) to 1 (tightly coupled)
- time_pressure: 0 (geological) to 1 (real-time)
- boundary_permeability: 0 (closed system) to 1 (fully open)

OUTPUT JSON format:
{{
  "distortion_profile": {{
    "resource_type": "...",
    "resource_dynamics": "...",
    "thermodynamic_regime": "...",
    "physical_constraints": ["..."],
    "actor_intentionality": "...",
    "actor_count_regime": "...",
    "actor_autonomy": 0.8,
    "incentive_legibility": 0.5,
    "boundary_domains": ["..."],
    "emergent_problems": ["..."],
    "intersection_type": "..."
  }},
  "f_star_coordinates": {{
    "resource_pressure": 0.7,
    "actor_complexity": 0.1,
    "information_asymmetry": 0.8,
    "coupling_tightness": 0.9,
    "time_pressure": 0.8,
    "boundary_permeability": 0.2
  }},
  "scale_level": "organism"
}}
"""
        try:
            response = self.ai_client.get_completion(prompt, system_prompt="You are a systems theoretical scientist.")
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                target_profile.distortion_profile = DistortionProfile(**data["distortion_profile"])
                target_profile.f_star_coordinates = data["f_star_coordinates"]
                target_profile.scale_level = data.get("scale_level", "")
        except Exception as e:
            print(f"Error during Stage 0 distortion analysis: {e}")

        return target_profile

    def _fstar_distance(self, coords1: Dict[str, float], coords2: Dict[str, float]) -> float:
        dims = ['resource_pressure', 'actor_complexity',
                'information_asymmetry', 'coupling_tightness',
                'time_pressure', 'boundary_permeability']
        diffs = [(coords1.get(d, 0.5) - coords2.get(d, 0.5))**2
                 for d in dims]
        return (sum(diffs) / len(dims)) ** 0.5

    def stage1_fstar_filter(self, target_profile: DomainProfile, top_k: int = 20) -> List[Theory]:
        """
        Primary filter using F* coordinates.
        Blueprints are prioritized primary matchers.
        Partials are held as refiners.
        """
        if not target_profile.f_star_coordinates:
            return self.stage1_filter(target_profile.structural_tags, top_k)

        blueprints = []
        frameworks = []
        partials = []

        for theory in self.theories:
            dist = self._fstar_distance(target_profile.f_star_coordinates, theory.f_star_coordinates or {})
            score = 1.0 - dist

            coverage_type = theory.coverage.coverage_type if theory.coverage else "framework"

            if coverage_type == "blueprint":
                blueprints.append((score, theory))
            elif coverage_type == "framework":
                frameworks.append((score, theory))
            else:
                partials.append((score, theory))

        blueprints.sort(key=lambda x: x[0], reverse=True)
        frameworks.sort(key=lambda x: x[0], reverse=True)
        partials.sort(key=lambda x: x[0], reverse=True)

        # Save top partials as current refiners for Stage 4
        self._current_refiners = [t for s, t in partials[:10]]

        # Return prioritized mix
        primary = ([t for s, t in blueprints[:3]] +
                   [t for s, t in frameworks[:top_k-3]])
        return primary[:top_k]

    def stage5_refine_with_partials(self, hypothesis: Hypothesis, target_profile: DomainProfile) -> Hypothesis:
        """
        Stage 5: Sharpen the hypothesis using relevant Partial theories as precision instruments.
        """
        relevant_partials = [
            t for t in getattr(self, '_current_refiners', [])
            if any(dim in (t.f_star_coordinates or {}) for dim in hypothesis.active_fstar_dimensions)
        ]

        if not relevant_partials:
            return hypothesis

        partials_text = "\n".join([
            f"- {t.name}: {t.description} [refines: {t.coverage.fstar_refinements if t.coverage else []}]"
            for t in relevant_partials
        ])

        prompt = f"""
A blueprint/framework hypothesis has been generated for '{target_profile.name}' based on {hypothesis.source_theory_id}.

STRATEGY: {hypothesis.strategy}
PREDICTION: {hypothesis.testable_prediction}

The following partial theories are precision instruments that sharpen specific mechanisms within this hypothesis.
Use them to add constraints, boundary conditions, or known unsolvable subproblems:

{partials_text}

OUTPUT JSON format:
{{
  "sharpened_prediction": "More precise prediction",
  "added_constraints": ["..."],
  "known_unsolvable_subproblems": ["..."]
}}
"""
        try:
            response = self.ai_client.get_completion(prompt, system_prompt="You are a theoretical systems engineer.")
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                hypothesis.testable_prediction = data.get("sharpened_prediction", hypothesis.testable_prediction)
                hypothesis.added_constraints = data.get("added_constraints", [])
                hypothesis.known_unsolvable_subproblems = data.get("known_unsolvable_subproblems", [])
        except Exception as e:
            print(f"Error during Stage 5 refinement: {e}")

        return hypothesis

    def subtractive_isolation(self, theory: Theory, blueprint: Theory) -> SubtractiveAnalysis:
        """
        Subtract blueprint F* structure from a theory to find unnamed refinements.
        """
        prompt = f"""
You are performing subtractive analysis to find unnamed theoretical concepts.

THEORY BEING ANALYZED: {theory.name}
Description: {theory.description}
Mechanisms: {theory.structural_topology.model_dump_json()}
Novel concepts: {theory.coverage.novel_concepts if theory.coverage else []}

BLUEPRINT BEING SUBTRACTED: {blueprint.name}
Core F* principles it covers: {blueprint.coverage.novel_concepts if blueprint.coverage else []}

Step 1: List every mechanism, principle, and concept in {theory.name}.
Step 2: Mark each as:
- COVERED: directly explained by {blueprint.name}
- REFINEMENT: extends or sharpens something in {blueprint.name}
- RESIDUE: not explained by {blueprint.name} at all

Step 3: For each RESIDUE/REFINEMENT component:
- Describe it in domain-agnostic terms
- Is it a candidate for a new Partial theory?
- What would you name it?

OUTPUT JSON list of objects for residue_components.
"""
        try:
            response = self.ai_client.get_completion(prompt, system_prompt="You are a theoretical scientist.")
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                components_data = json.loads(json_match.group())
                # Minimal mapping to ResidueComponent model
                components = []
                for c in components_data:
                    components.append(ResidueComponent(
                        description=c.get("description", ""),
                        appears_in_other_theories=[], # to be populated by cross-referencing
                        domain_of_origin=theory.domain,
                        has_formal_theory=False,
                        closest_formal_theory=blueprint.id,
                        candidate_theory_name=c.get("name"),
                        candidate_theory_description=c.get("description"),
                        potential_applications=[],
                        fstar_coordinates=None
                    ))
                return SubtractiveAnalysis(
                    theory_id=theory.id,
                    blueprint_used=blueprint.id,
                    residue_components=components
                )
        except Exception as e:
            print(f"Error during subtractive isolation: {e}")

        return SubtractiveAnalysis(theory_id=theory.id, blueprint_used=blueprint.id, residue_components=[])

    def analyze_intersection(self, domain_a: DomainProfile, domain_b: DomainProfile, emergent_problem: str) -> DomainIntersection:
        """
        Full intersection analysis pipeline (Orchestration placeholder).
        """
        return DomainIntersection(
            domain_a=domain_a.name,
            domain_b=domain_b.name,
            domain_a_contributions=[],
            domain_b_contributions=[],
            domain_a_solved_problems=[],
            domain_b_solved_problems=[],
            core_tension=emergent_problem,
            tension_fstar_coordinates={},
            subsidiary_tensions=[],
            analog_domains=[],
            interface_a_side={"domain": domain_a.name, "interface_requirements": [], "must_expose": [], "must_accept": [], "must_encapsulate": [], "exchange_protocol": "", "failure_modes": []},
            interface_b_side={"domain": domain_b.name, "interface_requirements": [], "must_expose": [], "must_accept": [], "must_encapsulate": [], "exchange_protocol": "", "failure_modes": []},
            invariant_transferrables=[]
        )

    def analyze(self, target_profile: DomainProfile) -> List[Hypothesis]:
        # Step 0: Distortion Analysis (Find F* coords)
        target_profile = self.stage0_distortion_analysis(target_profile)

        # Step 1: F* Filter (Search by underlying structure, not surface)
        candidates = self.stage1_fstar_filter(target_profile)

        # Step 2: Embedding Similarity
        refined_candidates = self.stage2_embedding_similarity(target_profile, candidates)

        # Step 3: LLM Comparison
        hypotheses = []
        for theory in refined_candidates[:5]:
            hypo = self.stage3_llm_comparison(target_profile, theory)

            # Step 4: Emergent Failure Analysis
            hypo.failure_modes = self.stage4_failure_analysis(target_profile, theory, hypo)

            # Step 5: Partial Refinement
            hypo = self.stage5_refine_with_partials(hypo, target_profile)

            hypotheses.append(hypo)

        return hypotheses
