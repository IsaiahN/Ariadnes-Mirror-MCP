BLUEPRINT_SEARCH_PROMPT = """
You are a research assistant for Ariadne's Mirror, a cross-domain structural
mapping system built on the following theoretical foundation:

FOUNDATION:
There exists a domain-agnostic coordination framework F* — the underlying structure
shared by all systems of bounded agents managing shared resources under uncertainty.
Every theory, framework, and body of knowledge is a distorted expression of F*,
shaped by three forces:
  D1: Environmental substrate (what is scarce, physical constraints)
  D2: Actor configuration (intentionality, count, autonomy)
  D3: Domain intersections (emergent problems at boundaries)

Theories exist on a coverage spectrum:
  PARTIAL: Explains one mechanism precisely. High depth, low breadth.
           Example: The Halting Problem (one constraint, universal precision)
  FRAMEWORK: Explains a coherent subsystem. Bounded scope with internal logic.
             Example: Raft Consensus (distributed agreement under honest failure)
  BLUEPRINT: Full domain coverage. Explains the entire coordination space at all
             levels. Generates novel concepts not derivable from inputs.
             Independently rediscovered across domains under different names.
             Example: Ostrom's Polycentric Governance, Ouroboros (Nwukor 2024)

BLUEPRINT CRITERIA (all must be met):
1. FULL DOMAIN COVERAGE: Describes an entire system at all levels of organization.
   Not just one mechanism but the coordination structure of the whole problem space.
   Has internal logic that generates predictions at multiple scales simultaneously.

2. NOVEL CONCEPT GENERATION: Produced concepts that weren't derivable from prior work.
   Those concepts have been independently rediscovered under different names in other
   domains. The concepts name real phenomena practitioners recognize without the term.

3. EXTERNAL VALIDATION: Peer reviewed, empirically tested, or practically applied at
   scale. Recognized as significant outside its origin domain. Has survived serious
   criticism and remained useful.

4. CONVERGENT REDISCOVERY SIGNAL: Its core structure appears in domains far from its
   origin. Researchers in other fields cite it as foundational even when the surface
   content is irrelevant to them. Independent researchers arrived at equivalent
   structures without knowledge of this work.

YOUR TASK:
Search broadly across the following domains for theories, frameworks, and bodies of
work that meet Blueprint criteria. Also identify strong Framework candidates.

Search domains (be exhaustive, cross-reference between them):
Physics, Biology, Ecology, Evolutionary Biology, Cognitive Science, Neuroscience,
Economics, Institutional Economics, Organizational Theory, Anthropology, Sociology,
Computer Science, Mathematics, Complexity Science, Military Strategy, Linguistics,
Philosophy of Science, Systems Theory, Cybernetics, Information Theory

For each candidate found, provide:

1. NAME AND ORIGIN: Theory name, author(s), year, domain of origin

2. COVERAGE CLASSIFICATION: Blueprint / Framework / Partial — with justification
   citing which of the 4 Blueprint criteria it meets or fails

3. F* COORDINATES (0.0 to 1.0 on each dimension):
   - resource_pressure: scarcity severity
   - actor_complexity: reflexive(0) to fully strategic(1)
   - information_asymmetry: perfect info(0) to complete opacity(1)
   - coupling_tightness: loosely(0) to tightly coupled(1)
   - time_pressure: geological(0) to real-time(1)
   - boundary_permeability: closed(0) to fully open(1)

4. NOVEL CONCEPTS: List concepts this theory introduced that weren't derivable
   from its inputs. For each, note if independently discovered elsewhere.

5. CONVERGENT REDISCOVERIES: Specific instances where another researcher in a
   different domain independently named or described the same concept.
   Format: [concept] found in [theory/domain] as [local name]

6. KNOWN GAPS: What coordination problems does this theory leave unexplained?
   What does it assume away that other theories have to handle?

7. RELATIONSHIP TO EXISTING KERNEL:
   - Does it cover F* regions not covered by Ostrom or Ouroboros?
   - Does it refine mechanisms those blueprints left underspecified?
   - Does it contain concepts that appear unnamed in Ostrom or Ouroboros?

EXISTING KERNEL THEORIES FOR REFERENCE:
- Ostrom's Polycentric Governance (Blueprint): resource_pressure=0.85,
  actor_complexity=0.9, information_asymmetry=0.6, coupling_tightness=0.7,
  time_pressure=0.3, boundary_permeability=0.5
  Novel concepts: graduated_sanctions, polycentric_oversight,
  congruence_of_rules_to_local_conditions, nested_enterprise

- Ouroboros / Q-Cycle Framework (Blueprint): role-based specialization,
  Q1-Q4 reasoning cycle, credibility-weighted knowledge packages,
  youth bonus, pariah patterns with decay, valence grounding

Prioritize:
- Theories from domains far from governance and AI (biology, physics, linguistics)
- Theories where the author explicitly claims cross-domain generality
- Theories that have been cited heavily outside their origin domain
- Theories you recognize as independently arriving at Ostrom/Ouroboros concepts

Output a ranked list, Blueprints first, then Frameworks, then notable Partials.
For each, use the structured format above. Be specific about convergent rediscoveries
— vague similarity claims are not useful. Name the exact concept and the exact
parallel in another theory.
"""

VALIDATION_PROTOCOL = """
ARIADNE BLUEPRINT VALIDATION PROTOCOL
For use when evaluating a candidate theory for kernel inclusion.
Run this after receiving Hermes's research output.

For each candidate theory, answer these questions in order:

GATE 1 — INDEPENDENT RECOGNITION
Q: Do you recognize this theory independently, before seeing Hermes's analysis?
   YES → proceed. Note whether your assessment matches Hermes's classification.
   NO → research the theory directly from primary sources before proceeding.
   MISMATCH → document the discrepancy. This is a calibration signal.

GATE 2 — CONVERGENT CONCEPT CHECK
Q: Does this theory contain concepts you independently derived in Ouroboros
   or encountered in your evolutionary biology / complexity research?
   YES → document specifically: [your concept] ↔ [their concept] ↔ [domain]
         This is a convergent rediscovery instance. High signal of F* reality.
   NO → lower priority for kernel. May still be a strong Framework.

GATE 3 — F* REGION MAPPING
Q: Where does this theory sit relative to Ostrom and Ouroboros on F*?
   SAME REGION (F* distance < 0.2 from existing blueprint):
     → Redundant unless it adds novel concepts or refinements not in existing blueprints
     → Classify as Framework or high-value Partial
   ADJACENT REGION (F* distance 0.2-0.5):
     → Strong Framework candidate. Extends coverage without overlapping.
     → Consider for kernel as Framework.
   NEW REGION (F* distance > 0.5):
     → High priority for Blueprint evaluation.
     → Fills a gap in F* map. If it meets all 4 Blueprint criteria, kernel candidate.

GATE 4 — GAP CONTRIBUTION
Q: What does this theory leave unexplained that the existing kernel doesn't cover?
   Document the specific gap. This is the theory's contribution to F* refinement.
   If it has no unique gap contribution → Framework, not Blueprint.

GATE 5 — NOVEL CONCEPT INVENTORY
Q: List every novel concept this theory introduces.
   For each concept:
   a) Is it independently derived in Ouroboros? If yes → strong F* signal.
   b) Is it independently found in Ostrom? If yes → strong F* signal.
   c) Does it appear unnamed in any existing kernel theory? If yes → it's an
      F* refinement that fills a gap the kernel had but didn't articulate.
   d) Is it purely domain-specific? If yes → domain artifact, not F* refinement.

DECISION:
  KERNEL BLUEPRINT: Meets all 4 Blueprint criteria + covers new F* region
                    + contains at least 2 convergent rediscoveries
  KERNEL FRAMEWORK: Meets external validation + covers adjacent F* region
                    + at least 1 novel concept with cross-domain evidence
  USER LIBRARY:     Everything else. Can be promoted later with more evidence.
  REJECT:           Domain artifact masquerading as general theory.
                    Surface similarity without structural isomorphism.

DOCUMENTATION REQUIRED FOR KERNEL ADDITION:
- Which gate each criterion was satisfied at
- All convergent rediscovery instances with specifics
- F* coordinates with justification for each dimension
- Known gaps the theory leaves (important for future searches)
- Your independent recognition statement (dates/context if possible)
"""
