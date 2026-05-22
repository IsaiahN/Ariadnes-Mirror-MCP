# Ariadne's Mirror

Ariadne's Mirror (formerly Universal Heuristic Oracle or UHO) is a tool for cross-domain structural mapping and hypothesis generation. It helps find structural isomorphisms between a target domain and a library of theories, providing transferable insights and testable predictions.

## Core Claim
Two domains that share structural fingerprints will yield transferable insights.

## Features
- **3-Stage Similarity Pipeline**: Tag-based filtering, Embedding similarity, and LLM-based structural comparison.
- **Theory Library**: A rich collection of theories from Physics, Economics, Biology, Network Science, and more.
- **Q-Cycle**: A structured 7-question cycle for domain extraction and evaluation.
- **Hypothesis Generation**: Produces testable predictions, failure conditions, and falsification paths.
- **Credibility Dynamics**: Theories gain or lose credibility based on their empirical track record.

## Installation
```bash
pip install -e .
```

## Usage
```bash
ariadne analyze --domain "content moderation" --description "Managing scale and toxicity in social platforms"
```
