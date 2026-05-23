import json
import re
from typing import Dict, List
from .models import DomainProfile, DomainDelta
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
        Uses an LLM to interpret these answers and generate structural tags and a domain delta.
        """
        profile = DomainProfile(
            name=domain_name,
            description=description,
            q_cycle_mappings=answers
        )

        # 1. Tag Extraction
        tag_prompt = f"""
Based on the following Q-Cycle answers for the domain '{domain_name}', extract a list of 5-8 relevant structural tags.
Description: {description}
Answers: {json.dumps(answers, indent=2)}

Vocabulary to choose from:
hierarchical, peer-to-peer, hub-spoke, cyclic, evolutionary, adversarial, cooperative, market, stigmergic, predictive, regulatory, layered, modular, network

Output ONLY a JSON list of strings.
"""
        try:
            response = self.ai_client.get_completion(tag_prompt, system_prompt="You are a system analyst.")
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                profile.structural_tags = json.loads(json_match.group())
            else:
                profile.structural_tags = ["distributed"]
        except Exception as e:
            print(f"Error during tag extraction: {e}")
            profile.structural_tags = ["distributed"]

        # 2. Delta Extraction (from Q7)
        q7_answer = answers.get("Q7", "")
        if q7_answer:
            delta_prompt = f"""
Analyze the following answer to Q7: "How is the target domain ('{domain_name}') different from the source theory's original context?"
Answer: {q7_answer}

Extract a structured 'Domain Delta' identifying:
- missing_mechanisms: things usually assumed in theoretical models that don't exist here
- extra_mechanisms: unique features of this domain not covered by general theories
- scale_differences: how size/volume affects the system
- agent_differences: intentionality, autonomy, or incentive differences

Output ONLY a JSON object with these 4 keys.
"""
            try:
                response = self.ai_client.get_completion(delta_prompt, system_prompt="You are a system analyst.")
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    profile.delta = DomainDelta(**json.loads(json_match.group()))
            except Exception as e:
                print(f"Error during delta extraction: {e}")

        return profile
