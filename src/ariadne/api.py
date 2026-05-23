import json
import re
from typing import List, Dict
from .engine import AriadneEngine
from .extractor import QCycleExtractor
from .models import DomainProfile, Hypothesis

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
        from .ai import AIClient
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

def record_feedback(theory_id: str, rating: int) -> bool:
    engine = AriadneEngine()
    engine.update_credibility(theory_id, rating)
    return True
