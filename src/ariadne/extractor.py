from typing import Dict, List
from .models import DomainProfile

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
        pass

    def run_extraction_cycle(self, domain_name: str, description: str, answers: Dict[str, str]) -> DomainProfile:
        """
        Populates a DomainProfile based on the Q-Cycle answers.
        In a real app, an LLM would interpret these answers to generate structural tags.
        """
        profile = DomainProfile(
            name=domain_name,
            description=description,
            q_cycle_mappings=answers
        )
        # Mocking structural tag extraction from answers
        profile.structural_tags = ["distributed", "peer-to-peer"]
        return profile
