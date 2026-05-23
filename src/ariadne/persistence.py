import json
import os
from typing import Dict
from .config import settings

class TheoryStateManager:
    def __init__(self):
        self.state_file = os.path.join(settings.resolved_storage_dir, "theory_state.json")
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, dict]:
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def get_theory_state(self, theory_id: str) -> dict:
        return self.state.get(theory_id, {"credibility_score": 0.5, "n_uses": 0})

    def update_theory_state(self, theory_id: str, credibility_score: float, n_uses: int):
        self.state[theory_id] = {
            "credibility_score": credibility_score,
            "n_uses": n_uses
        }
        self._save_state()

    def _save_state(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
