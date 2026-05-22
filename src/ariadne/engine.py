import yaml
import json
import os
import numpy as np
from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Theory, DomainProfile, Hypothesis
# For this bootstrap, I will provide the architectural structure

class AriadneEngine:
    def __init__(self, theories_path: str):
        self.theories = self._load_theories(theories_path)
        self.storage_dir = os.path.expanduser("~/.ariadne")
        os.makedirs(self.storage_dir, exist_ok=True)

    def _load_theories(self, path: str) -> List[Theory]:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            return [Theory(**t) for t in data['theories']]

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

    def stage2_embedding_similarity(self, target_profile: DomainProfile, candidates: List[Theory], top_k: int = 10) -> List[Theory]:
        """
        Stage 2: Semantic similarity using TF-IDF as a proxy for embeddings.
        """
        if not candidates:
            return []

        texts = [f"{t.name} {t.domain} {t.description} {' '.join(t.structural_tags)}" for t in candidates]
        target_text = f"{target_profile.name} {target_profile.description} {' '.join(target_profile.q_cycle_mappings.values())}"

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts + [target_text])

        # Last element is the target
        target_vector = tfidf_matrix[-1:]
        theory_vectors = tfidf_matrix[:-1]

        similarities = cosine_similarity(target_vector, theory_vectors).flatten()

        scored_candidates = sorted(zip(similarities, candidates), key=lambda x: x[0], reverse=True)
        return [t for s, t in scored_candidates[:top_k]]

    def update_credibility(self, theory_id: str, rating: float):
        """
        Bayesian update for theory credibility.
        rating is 1-5, normalized to 0-1.
        """
        theory = next((t for t in self.theories if t.id == theory_id), None)
        if not theory:
            return

        normalized_rating = (rating - 1) / 4.0
        n = theory.n_uses
        current_score = theory.credibility_score

        # Simple Bayesian update: (prior * n + evidence) / (n + 1)
        new_score = (current_score * n + normalized_rating) / (n + 1)

        theory.credibility_score = new_score
        theory.n_uses += 1

        # In a real app, we would save this back to theories.yaml or a separate state file
        self._save_usage_log(theory_id, rating)

    def _save_usage_log(self, theory_id: str, rating: float):
        log_path = os.path.join(self.storage_dir, "usage_log.jsonl")
        log_entry = {"theory_id": theory_id, "rating": rating, "timestamp": "..."}
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

    def stage3_llm_comparison(self, target_profile: DomainProfile, theory: Theory) -> Hypothesis:
        """
        Stage 3: LLM structural comparison.
        This constructs the prompt that would be sent to the LLM.
        """
        prompt = f"""
You are comparing two systems for structural isomorphism.

TARGET DOMAIN:
Name: {target_profile.name}
Description: {target_profile.description}
Meta-components: {target_profile.q_cycle_mappings}

SOURCE THEORY:
Name: {theory.name}
Description: {theory.description}
Topology: {theory.structural_topology.model_dump()}

Evaluate on these dimensions (1-10 each):
1. Role isomorphism
2. Memory/state isomorphism
3. Valence isomorphism
4. Transition isomorphism
5. Feedback topology

Generate a transfer hypothesis with testable predictions and failure conditions.
"""
        # In a real app, we would call OpenAI here.
        # For this version, we will generate a structured response based on the theory data.

        return Hypothesis(
            source_theory_id=theory.id,
            target_domain_name=target_profile.name,
            isomorphism_map={"role1": "target_role1"},
            strategy=f"Adopt {theory.name}'s approach...",
            explanation=f"Because {target_profile.name} shares structural fingerprints with {theory.name}...",
            testable_prediction="If X is increased, Y will decrease by Z amount.",
            failure_conditions=["If scale exceeds capacity", "If communication is interrupted"],
            falsification_path="Measure Y after increasing X; if Y does not decrease, hypothesis is false.",
            structural_similarity=0.85,
            novelty_score=0.9,
            falsifiability_score=0.8,
            final_score=0.85,
            confidence_interval=(0.7, 0.9)
        )

    def analyze(self, target_profile: DomainProfile) -> List[Hypothesis]:
        # Step 1: Coarse Filter
        candidates = self.stage1_filter(target_profile.structural_tags)

        # Step 2: Embedding Similarity
        refined_candidates = self.stage2_embedding_similarity(target_profile, candidates)

        # Step 3: LLM Comparison
        hypotheses = []
        for theory in refined_candidates[:5]:
            hypo = self.stage3_llm_comparison(target_profile, theory)
            hypotheses.append(hypo)

        return hypotheses
