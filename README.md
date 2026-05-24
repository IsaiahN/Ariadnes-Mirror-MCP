# Ariadne's Mirror MCP

*Ariadne leads you out of your field's labyrinth by finding threads in others.*

## What It Does

**Most hard problems remain hard because their solutions may already exist in another field, under a different name, invisible to keyword search.**

Problems share deep structures: trade-offs, bottlenecks, incentive traps, search landscapes. Different fields have found heuristics for them, but jargon hides the commonality. Ariadne's Mirror acts as a looking glass that maps your problem's core structure to other domains.

It doesn't give you the answer, but it does provide an analogical bridge that you can traverse and validate.

Where a researcher brings only one career of cross-domain reading, this brings a
mapped library of theories across physics, biology, economics, computer
science, and philosophy, searched by structural similarity rather than keywords.

## Use Cases

| Use Case | Category | Description |
|---|---|---|
| **Hypothesis generation** | Analysis | Given a problem domain, find which theories from unrelated fields are structurally closest and generate transfer hypotheses with testable predictions and falsification paths. |
| **Emergent failure analysis** | Analysis | Identify failure modes that arise specifically from applying a theory outside its original context. These are distinct from the theory's known failure modes and are often the ones that matter most in practice. |
| **Domain intersection analysis** | Research | When two domains collide and produce emergent problems that exist in neither domain alone, find a third domain where the same structural tension was already resolved, then derive interface specifications for each side separately. The combination problem often becomes two tractable boundary problems. |
| **Scale traversal** | Research | Find how the same structural problem was solved at a different scale. A logistics problem at the institutional scale may have a well-tested solution at the cellular or ecological scale once distortions are stripped away. |
| **Subtractive isolation** | Research | Subtract a Blueprint-level theory from any other theory to find the residue: concepts that exist in the coordination space but have no formal theory yet. These unnamed concepts are candidates for new Partial theories and often contain the most transferable insights. |
| **Gap mapping** | Research | Identify regions of F* space where no theory exists. These are not failures of the search. They are the map telling you where recurring coordination problems have never been formally theorized. |
| **Theory classification** | Curation | Given a new theory or framework, classify it as Blueprint, Framework, or Partial, place it in F* space, and identify its convergent rediscoveries in the existing library. |
| **Convergent rediscovery detection** | Curation | Check whether a concept appears independently across multiple theories in different domains. High convergence is evidence the concept is a real feature of the underlying coordination structure rather than a domain artifact. |
| **Expert matching** | Collaboration | A sufficiently rich F* map identifies not just analogous theories but analogous thinkers: researchers whose career expertise sits at a structurally similar position to your problem, making cross-domain collaboration targeted rather than accidental. |

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

| Tool | Description |
|---|---|
| `ariadne_analyze_brief` | Full analysis from a research brief |
| `ariadne_analyze_failures` | Emergent failure mode analysis |
| `ariadne_find_cross_scale_analog` | Find solutions at different scales |
| `ariadne_subtractive_isolation` | Find unnamed theoretical residues |
| `ariadne_map_fstar_coverage` | F* coverage gaps in the library |
| `ariadne_get_blueprint_search_prompt` | Structured prompt for finding new kernel candidates |
| `ariadne_list_kernel_theories` | Inspect the protected seed set |

## Tests

```bash
pip install -e ".[test]"
pytest tests/
```

## Architecture

### The Kernel

The protected seed set of theories spanning physics, biology, economics,
computer science, sociology, and philosophy. 

Each theory has:

- F* coordinates across 6 dimensions (resource_pressure, actor_complexity,
  information_asymmetry, coupling_tightness, time_pressure,
  boundary_permeability)
- Coverage classification (Blueprint / Framework / Partial)
- Convergent discovery records linking structurally equivalent concepts
  across domains
- Distortion profile describing how domain-specific factors shape the theory

The kernel is read-only at runtime and hash-verified on load. It is the
system's closest approximation of F*, the domain-agnostic coordination
structure underlying all bounded-resource coordination problems.

Current Blueprints: Ostrom's Polycentric Governance, Ouroboros/Q-Cycle
(Nwukor 2024), Panarchy, Ashby's Law of Requisite Variety, Prigogine's
Dissipative Structures, Autopoiesis, Bateson's Ecology of Mind.

### The Pipeline

| Stage | Name | Description |
|---|---|---|
| 0 | Distortion Analysis | Find F* coordinates for the target domain |
| 1 | F* Filter | Match by structural distance, not surface similarity |
| 2 | Embedding Similarity | Semantic refinement of candidates |
| 3 | LLM Comparison | Structural isomorphism scoring and hypothesis generation |
| 4 | Failure Analysis | Emergent failure modes from transfer mismatches |
| 5 | Partial Refinement | Sharpen predictions with precision partial theories |

### Thread System

User-added theories and session data are stored in isolated threads, separate
from the kernel. Thread theories have a credibility ceiling of 0.7. Kernel
theories start at 0.8 and are not modified by usage feedback.

## Theoretical Basis

### The F* Hypothesis

The F* hypothesis is that coordination problems across all domains share deep
structural regularities that persist after domain-specific context is stripped
away. The primary evidence is convergent rediscovery: independent researchers
in unrelated fields independently arriving at structurally equivalent
frameworks without knowledge of each other's work.

This is an empirical hypothesis, not a proven theorem. The outputs uncover
potential shapes of a problem and structurally analogous solutions from other
domains. Validation remains the user's work.

### How F* Mappings Work

Each theory in the kernel or added to thread libraries is categorized as one
of these three:

- **Blueprints** are full-coverage frameworks that describe an entire
  coordination space at all levels, independently derived and empirically
  validated across domains, and the strongest signal that a theory is
  measuring something real about F* rather than its origin domain.
- **Frameworks** explain a coherent subsystem with defined scope and internal
  logic, useful for concretizing hypotheses within a bounded problem space.
- **Partials** are high-precision instruments that describe one mechanism
  exactly, used to sharpen predictions and identify known unsolvable
  subproblems within a hypothesis.

### On the Kernel

The kernel's quality directly determines the quality of every output the tool
produces. Modifying it without careful consideration has cascading effects on
all downstream results and is not recommended.

For enrichment, using AutoResearch to chart additional regions of F* for
example, new theories should be stored in thread libraries rather than the
kernel itself. This lets you compare core outputs against enriched outputs and
revert cleanly if enrichment degrades results.

## Related Work

Nwukor, I. (2024). Role-Based Multi-Agent Reasoning Framework.
Ostrom, E. (1990). Governing the Commons.
Ashby, W.R. (1956). An Introduction to Cybernetics.
Prigogine, I. (1977). Self-Organization in Non-Equilibrium Systems.

## License

MIT
