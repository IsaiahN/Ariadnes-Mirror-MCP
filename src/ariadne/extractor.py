import json
import re
from typing import Dict, List
from .models import DomainProfile
from .ai import AIClient

class QCycleExtractor:
    QUESTIONS = {
        "Q1": "What in your domain is CHANGING rapidly vs. what is FIXED? (State variables and invariants)",
        "Q2": "What PUNISHES actors in your domain? What REWARDS them? (Valence/currency)",
        "Q3": "What happens when you push on the MOST SALIENT variable? (Transition triggers)",
        "Q4": "How do agents find out what others are doing? (Information/Communication)",
        "Q5": "What subset of variables directly affect the outcome? (Core variables)",
        "Q6": "What constraints cannot be discovered from experiments alone? (Background knowledge)",
        "Q7": "How is the target domain different from the source theory's original context? (Failure modes)"
    }

    def __init__(self):
        self.ai_client = AIClient()

    def run_extraction_cycle(self, domain_name: str, description: str, answers: Dict[str, str]) -> DomainProfile:
        """
        Populates a DomainProfile based on the Q-Cycle answers.
        Uses an LLM to interpret these answers and generate structural tags.
        """
        profile = DomainProfile(
            name=domain_name,
            description=description,
            q_cycle_mappings=answers
        )

        prompt = f"""
Based on the following Q-Cycle answers for the domain '{domain_name}', extract a list of 5-8 relevant structural tags.
Description: {description}
Answers: {json.dumps(answers, indent=2)}

Vocabulary to choose from:
hierarchical, peer-to-peer, hub-spoke, cyclic, evolutionary, adversarial, cooperative, market, stigmergic, predictive, regulatory, layered, modular, network

Output ONLY a JSON list of strings.
"""
        try:
            response = self.ai_client.get_completion(prompt, system_prompt="You are a system analyst.")
            # Basic JSON extraction
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                profile.structural_tags = json.loads(json_match.group())
            else:
                profile.structural_tags = ["distributed"] # Fallback
        except Exception as e:
            print(f"Error during tag extraction: {e}")
            profile.structural_tags = ["distributed"] # Fallback

        return profile
