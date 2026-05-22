from ariadne.engine import AriadneEngine
import os

theories_path = "data/theories.yaml"
engine = AriadneEngine(theories_path)

# Initial
raft = next(t for t in engine.theories if t.id == "raft_consensus")
print(f"Initial: {raft.credibility_score}")

# Feedback 5
engine.update_credibility("raft_consensus", 5)
print(f"After rating 5: {raft.credibility_score}")

# Feedback 5 again
engine.update_credibility("raft_consensus", 5)
print(f"After another 5: {raft.credibility_score}")

# Feedback 1
engine.update_credibility("raft_consensus", 1)
print(f"After rating 1: {raft.credibility_score}")
