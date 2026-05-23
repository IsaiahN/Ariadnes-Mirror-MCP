
# Ariadne's Mirror MCP

A cross-domain structural mapping tool that helps find deep structural 
similarities between a problem domain and a curated library of theories, 
generating transferable hypotheses and identifying analogous solutions from 
unrelated fields.

## What It Does

Given a problem domain described through a structured Q-Cycle interview, 
Ariadne's Mirror:

1. Strips domain-specific distortions to find the problem's position in a 
   domain-agnostic coordinate space (F*)
2. Searches a curated theory library for structurally similar theories 
   regardless of surface domain
3. Generates transfer hypotheses with testable predictions
4. Identifies emergent failure modes specific to the transfer
5. Refines hypotheses using partial theories as precision instruments

Two domains that share structural fingerprints may yield transferable insights. The outputs provide direction and shape structural connections that point toward where answers might exist and what form they might take, giving you something concrete to follow up with and validate.

## Architecture

### The Kernel

The protected seed set of ~48 theories spanning physics, biology, economics, 
computer science, sociology, and philosophy. Each theory has:

- F* coordinates across 6 dimensions (resource_pressure, actor_complexity, 
  information_asymmetry, coupling_tightness, time_pressure, 
  boundary_permeability)
- Coverage classification (Blueprint / Framework / Partial)
- Convergent discovery records linking structurally equivalent concepts 
  across domains
- Distortion profile describing how domain-specific factors shape the theory

The kernel is read-only at runtime and hash-verified on load. It is the 
system's closest approximation of F* — the domain-agnostic coordination 
structure underlying all bounded-resource coordination problems.

Blueprints in the kernel: Ostrom's Polycentric Governance, Ouroboros/Q-Cycle 
(Nwukor 2024), Panarchy, Ashby's Law of Requisite Variety, Prigogine's 
Dissipative Structures, Autopoiesis, Bateson's Ecology of Mind.

### The Pipeline

```
Stage 0: Distortion Analysis    — Find F* coordinates for the target domain
Stage 1: F* Filter              — Match by structural distance, not surface similarity
Stage 2: Embedding Similarity   — Semantic refinement of candidates
Stage 3: LLM Comparison         — Structural isomorphism scoring and hypothesis generation
Stage 4: Failure Analysis       — Emergent failure modes from transfer mismatches
Stage 5: Partial Refinement     — Sharpen predictions with precision partial theories
```

### Thread System

User-added theories and session data are stored in isolated threads, 
separate from the kernel. Thread theories have a credibility ceiling of 0.7 
(kernel theories start at 0.8 and are not modified by usage feedback).

## Installation

```bash
pip install -e .
```

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

For OpenRouter:
```
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_EMBEDDING_MODEL=openai/text-embedding-3-large
```

For local Ollama (fully offline):
```
OPENROUTER_BASE_URL=http://localhost:11434/v1
OPENROUTER_API_KEY=ollama
OPENROUTER_MODEL=nous-hermes-2-pro
OPENROUTER_EMBEDDING_MODEL=nomic-embed-text
```

## Usage

### CLI

```bash
# Interactive Q-Cycle analysis
ariadne analyze --domain "content moderation" \
  --description "Managing scale and toxicity in social platforms"

# List kernel theories
ariadne library list

# Provide feedback on a theory
ariadne feedback --theory raft_consensus --rating 4
```

### MCP Server (for Hermes / agent frameworks)

```bash
ariadne-mcp
```

Register in your agent config:
```yaml
mcp_servers:
  - name: ariadnes-mirror
    command: ariadne-mcp
    transport: stdio
```

Available tools:
- `ariadne_analyze_brief` — full analysis from a research brief
- `ariadne_analyze_failures` — emergent failure mode analysis
- `ariadne_find_cross_scale_analog` — find solutions at different scales
- `ariadne_subtractive_isolation` — find unnamed theoretical residues
- `ariadne_map_fstar_coverage` — F* coverage gaps in the library
- `ariadne_get_blueprint_search_prompt` — structured prompt for finding 
  new kernel candidates
- `ariadne_list_kernel_theories` — inspect the protected seed set

## Tests

```bash
pip install -e ".[test]"
pytest tests/
```

## Theoretical Basis

### The F* Hypothesis

Most hard problems stay hard because the people working on them don't know 
that someone else already solved a structurally identical problem in a 
completely different field under a different name, with different 
vocabulary, invisible to any keyword search.

The F* hypothesis is that coordination problems across all domains, how 
bounded agents manage shared resources under uncertainty, share deep 
structural regularities that persist after you strip away domain-specific 
context. 

The tool is the hypothesis put to the test. 
The tool's outputs' uncover potential shapes of a problem and structurally analogous solutions 
from other domains to present potential solutions but the validation work will still be required. 

### On the Kernel

The kernel is the system's approximation of F*. Its quality directly 
determines the quality of every output the tool produces. Modifying it 
without careful consideration has cascading effects on all downstream 
results (it is not recommended).

For enrichment and extension for example, using AutoResearch to chart 
additional regions of F*, new theories should be stored externally in 
thread libraries, not in the kernel itself. 

This separation lets you compare core outputs against enriched outputs and revert cleanly if 
enrichment degrades results.

## License

MIT
```
