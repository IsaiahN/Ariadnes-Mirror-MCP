import json
import re
from typing import List, Dict, Optional, Any
from .engine import AriadneEngine
from .extractor import QCycleExtractor
from .models import DomainProfile, Hypothesis, FailureMode, SubtractiveAnalysis, DomainIntersection
from .ai import AIClient

def analyze_failures(
    domain_name: str,
    theory_id: str,
    q7_answer: str
) -> List[FailureMode]:
    """
    Generate emergent failure modes for a proposed transfer.
    """
    engine = AriadneEngine()
    theory = next((t for t in engine.theories if t.id == theory_id), None)
    if not theory:
        raise KeyError(f"Theory with ID '{theory_id}' not found.")

    # Create a minimal profile and hypothesis for context
    extractor = QCycleExtractor()
    profile = extractor.run_extraction_cycle(domain_name, "", {"Q7": q7_answer})

    # We need a Stage 3 hypothesis for the isomorphism map context
    temp_hypo = engine.stage3_llm_comparison(profile, theory)

    return engine.stage4_failure_analysis(profile, theory, temp_hypo)

def analyze_domain(
    domain: str,
    description: str,
    answers: Dict[str, str]
) -> List[Hypothesis]:
    """
    Programmatic API to analyze a domain.
    """
    extractor = QCycleExtractor()
    profile = extractor.run_extraction_cycle(domain, description, answers)
    engine = AriadneEngine()
    return engine.analyze(profile)

def analyze_from_brief(
    domain: str,
    brief: str
) -> List[Hypothesis]:
    """
    Convenience method for agents. Generates Q-Cycle answers from a research brief
    before running the analysis.
    """
    extractor = QCycleExtractor()

    prompt = f"""
Given the following research brief for the domain '{domain}', provide detailed answers to the 7 Q-Cycle questions.

RESEARCH BRIEF:
{brief}

QUESTIONS:
{json.dumps(extractor.QUESTIONS, indent=2)}

Output ONLY a JSON object with keys Q1-Q7.
"""
    try:
        ai_client = AIClient()
        response = ai_client.get_completion(prompt, system_prompt="You are a system analyst.")
        answers = json.loads(response)
    except Exception as e:
        print(f"Error during brief-to-Q-cycle: {e}")
        # Fallback to empty answers
        answers = {f"Q{i}": "N/A" for i in range(1, 8)}

    return analyze_domain(domain, brief, answers)

def list_theories() -> List:
    return AriadneEngine().theories

def find_cross_scale_analog(
    domain: str,
    brief: str,
    target_scale: Optional[str] = None
) -> List[Hypothesis]:
    """
    Find solutions by searching for how the same F*-equivalent problem
    was solved at a different scale or in a different domain.
    """
    # Use F* proximity on scale-correlating dimensions if target_scale is provided
    hypotheses = analyze_from_brief(domain, brief)

    if target_scale:
        # Scale tends to correlate with time_pressure and coupling_tightness
        # This is a heuristic: smaller scales have higher time pressure and tighter coupling
        scale_map = {
            "subatomic": (0.9, 0.9),
            "cellular": (0.8, 0.8),
            "organism": (0.6, 0.6),
            "institutional": (0.4, 0.4),
            "civilizational": (0.2, 0.2)
        }

        target_tp, target_ct = scale_map.get(target_scale, (0.5, 0.5))
        engine = AriadneEngine()

        filtered = []
        for hypo in hypotheses:
            theory = next((t for t in engine.theories if t.id == hypo.source_theory_id), None)
            if not theory: continue

            # If theory has scale_level, use it
            if theory.scale_level == target_scale:
                filtered.append(hypo)
                continue

            # Otherwise use F* proximity on scale dimensions
            if theory.f_star_coordinates:
                tp = theory.f_star_coordinates.get("time_pressure", 0.5)
                ct = theory.f_star_coordinates.get("coupling_tightness", 0.5)
                if abs(tp - target_tp) < 0.3 and abs(ct - target_ct) < 0.3:
                    filtered.append(hypo)

        return filtered

    return hypotheses

def run_subtractive_isolation(theory_id: str, blueprint_id: str = "ostrom_polycentric_governance") -> SubtractiveAnalysis:
    engine = AriadneEngine()
    theory = next((t for t in engine.theories if t.id == theory_id), None)
    blueprint = next((t for t in engine.theories if t.id == blueprint_id), None)
    if not theory:
        raise KeyError(f"Theory '{theory_id}' not found.")
    if not blueprint:
        raise KeyError(f"Blueprint '{blueprint_id}' not found.")
    return engine.subtractive_isolation(theory, blueprint)

def map_fstar_coverage() -> Dict[str, Any]:
    engine = AriadneEngine()

    # Compute actual coverage from theories
    all_coords = [
        t.f_star_coordinates for t in engine.theories
        if t.f_star_coordinates
    ]

    dims = ['resource_pressure', 'actor_complexity', 'information_asymmetry',
            'coupling_tightness', 'time_pressure', 'boundary_permeability']

    coverage_by_dim = {}
    for dim in dims:
        values = [c[dim] for c in all_coords if dim in c]
        if values:
            sorted_vals = sorted(values)
            gaps = []
            for i in range(len(sorted_vals) - 1):
                if sorted_vals[i+1] - sorted_vals[i] > 0.3:
                    gaps.append({"from": sorted_vals[i], "to": sorted_vals[i+1], "size": sorted_vals[i+1] - sorted_vals[i]})

            coverage_by_dim[dim] = {
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "gaps": gaps
            }

    return {
        "coverage_by_dimension": coverage_by_dim,
        "blueprint_count": len([t for t in engine.theories if t.coverage and t.coverage.coverage_type == "blueprint"]),
        "total_theories": len(engine.theories)
    }

def record_feedback(theory_id: str, rating: int) -> bool:
    engine = AriadneEngine()
    engine.update_credibility(theory_id, rating)
    return True
