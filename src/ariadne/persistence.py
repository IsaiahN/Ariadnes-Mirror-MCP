import json
import os
import datetime
import yaml
from typing import Dict, List, Optional
from .config import settings
from .models import Thread, Theory

class ThreadStateManager:
    def __init__(self, thread_id: str = "default"):
        self.thread_id = thread_id
        self.thread_dir = os.path.join(settings.resolved_storage_dir, "threads", thread_id)
        self.theories_dir = os.path.join(self.thread_dir, "theories")
        os.makedirs(self.theories_dir, exist_ok=True)
        self.state_file = os.path.join(self.thread_dir, "thread.json")
        self.thread = self._load_thread()

    def _load_thread(self) -> Thread:
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return Thread(**json.load(f))
        return Thread(
            id=self.thread_id,
            name=self.thread_id,
            description="Default thread",
            created_at=datetime.datetime.now().isoformat()
        )

    def load_theories(self) -> List[Theory]:
        theories = []
        for fname in os.listdir(self.theories_dir):
            if fname.endswith('.yaml'):
                with open(os.path.join(self.theories_dir, fname), 'r') as f:
                    data = yaml.safe_load(f)
                    theories.append(Theory(**data))
        return theories

    def save_candidate_evaluation(self, name: str, evaluation: dict):
        eval_path = os.path.join(self.thread_dir, "candidates.jsonl")
        entry = {
            "name": name,
            "evaluation": evaluation,
            "timestamp": datetime.datetime.now().isoformat()
        }
        with open(eval_path, 'a') as f:
            f.write(json.dumps(entry) + "\n")

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
