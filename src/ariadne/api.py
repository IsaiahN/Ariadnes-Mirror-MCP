import json
import re
from typing import List, Dict, Optional
from .engine import AriadneEngine
from .extractor import QCycleExtractor
from .models import DomainProfile, Hypothesis, FailureMode
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
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            answers = json.loads(json_match.group())
        else:
            raise ValueError("Could not parse Q-Cycle answers from LLM response.")
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
    extractor = QCycleExtractor()
    # For cross-scale we use a brief to get full context
    prompt = f"Extract answers to the 7 Q-Cycle questions based on this brief: {brief}"
    # In a real impl, we would use the same logic as analyze_from_brief
    # For now, let's reuse analyze_from_brief but filter by scale if provided
    hypotheses = analyze_from_brief(domain, brief)

    if target_scale:
        engine = AriadneEngine()
        # Re-filter results by scale
        filtered = []
        for hypo in hypotheses:
            theory = next((t for t in engine.theories if t.id == hypo.source_theory_id), None)
            if theory and theory.scale_level == target_scale:
                filtered.append(hypo)
        return filtered

    return hypotheses

def record_feedback(theory_id: str, rating: int) -> bool:
    engine = AriadneEngine()
    engine.update_credibility(theory_id, rating)
    return True
