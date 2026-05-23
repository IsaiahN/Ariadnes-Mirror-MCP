import yaml
import datetime
import json
import os
import pickle
import re
import numpy as np
from typing import List, Optional
from importlib import resources
from .models import Theory, DomainProfile, Hypothesis, FailureMode
from .persistence import TheoryStateManager
from .config import settings
from .ai import AIClient

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
    def __init__(self, theories_path: Optional[str] = None):
        if theories_path is None:
            with resources.path("ariadne.data", "theories.yaml") as p:
                theories_path = str(p)

        self.state_manager = TheoryStateManager()
        self._ai_client = None
        self.theories = self._load_theories(theories_path)
        self.storage_dir = settings.resolved_storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def _load_theories(self, path: str) -> List[Theory]:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            theories = []
            for t_data in data['theories']:
                theory = Theory(**t_data)
                # Load persisted state
                state = self.state_manager.get_theory_state(theory.id)
                theory.credibility_score = state["credibility_score"]
                theory.n_uses = state["n_uses"]
                theories.append(theory)
            return theories

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
        rating is 1-5, normalized to 0-1.
        """
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5.")

        theory = next((t for t in self.theories if t.id == theory_id), None)
        if not theory:
            raise KeyError(f"Theory with ID '{theory_id}' not found.")

        normalized_rating = (rating - 1) / 4.0
        n = theory.n_uses
        current_score = theory.credibility_score

        # Simple Bayesian update: (prior * n + evidence) / (n + 1)
        new_score = (current_score * n + normalized_rating) / (n + 1)

        theory.credibility_score = new_score
        theory.n_uses += 1

        # Persist state
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

            return Hypothesis(
                source_theory_id=theory.id,
                target_domain_name=target_profile.name,
                isomorphism_map=data["isomorphism_map"],
                strategy=data["strategy"],
                explanation=data["explanation"],
                testable_prediction=data["testable_prediction"],
                failure_conditions=data["failure_conditions"],
                falsification_path=data["falsification_path"],
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

    def analyze(self, target_profile: DomainProfile) -> List[Hypothesis]:
        # Step 1: Coarse Filter
        candidates = self.stage1_filter(target_profile.structural_tags)

        # Step 2: Embedding Similarity
        refined_candidates = self.stage2_embedding_similarity(target_profile, candidates)

        # Step 3: LLM Comparison
        hypotheses = []
        for theory in refined_candidates[:5]:
            hypo = self.stage3_llm_comparison(target_profile, theory)

            # Step 4: Emergent Failure Analysis
            hypo.failure_modes = self.stage4_failure_analysis(target_profile, theory, hypo)

            hypotheses.append(hypo)

        return hypotheses
