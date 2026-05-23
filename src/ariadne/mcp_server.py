from mcp.server.fastmcp import FastMCP
from typing import Optional
from .api import (
    analyze_domain, list_theories, record_feedback,
    analyze_from_brief, analyze_failures, find_cross_scale_analog,
    run_subtractive_isolation, map_fstar_coverage
)
from .research_tasks import BLUEPRINT_SEARCH_PROMPT, VALIDATION_PROTOCOL

mcp = FastMCP("ariadnes-mirror")

@mcp.tool()
def ariadne_analyze(
    domain: str,
    description: str,
    q1: str, q2: str, q3: str,
    q4: str, q5: str, q6: str, q7: str
) -> list[dict]:
    """Find structural isomorphisms between a domain and known theories using Q-Cycle answers."""
    answers = {
        "Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4,
        "Q5": q5, "Q6": q6, "Q7": q7
    }
    hypotheses = analyze_domain(domain, description, answers)
    return [h.model_dump() for h in hypotheses]

@mcp.tool()
def ariadne_analyze_brief(
    domain: str,
    brief: str
) -> list[dict]:
    """Find structural isomorphisms by automatically extracting Q-Cycle answers from a research brief."""
    hypotheses = analyze_from_brief(domain, brief)
    return [h.model_dump() for h in hypotheses]

@mcp.tool()
def ariadne_list_theories() -> list[dict]:
    """List all theories in the Ariadne library with credibility scores."""
    return [{"id": t.id, "name": t.name, "domain": t.domain,
             "credibility": t.credibility_score} for t in list_theories()]

@mcp.tool()
def ariadne_analyze_failures(
    domain: str,
    theory_id: str,
    q7_answer: str
) -> list[dict]:
    """Given a proposed theory transfer, generate emergent failure modes that arise from structural mismatches."""
    failures = analyze_failures(domain, theory_id, q7_answer)
    return [f.model_dump() for f in failures]

@mcp.tool()
def ariadne_find_cross_scale_analog(
    domain: str,
    brief: str,
    target_scale: Optional[str] = None
) -> list[dict]:
    """Find solutions by searching for how the same F*-equivalent problem was solved at a different scale."""
    hypotheses = find_cross_scale_analog(domain, brief, target_scale)
    return [h.model_dump() for h in hypotheses]

@mcp.tool()
def ariadne_subtractive_isolation(
    theory_id: str,
    blueprint_id: str = "ostrom_polycentric_governance"
) -> dict:
    """Subtract blueprint F* structure from a theory to find unnamed nuances and refinements."""
    result = run_subtractive_isolation(theory_id, blueprint_id)
    return result.model_dump()

@mcp.tool()
def ariadne_map_fstar_coverage() -> dict:
    """Return a map of F* space showing theory coverage and identifying gaps."""
    return map_fstar_coverage()

@mcp.tool()
def ariadne_get_blueprint_search_prompt() -> str:
    """Returns the structured research prompt for searching for Blueprint-level theories."""
    return BLUEPRINT_SEARCH_PROMPT

@mcp.tool()
def ariadne_get_validation_protocol() -> str:
    """Returns the validation protocol for evaluating Blueprint candidates."""
    return VALIDATION_PROTOCOL

@mcp.tool()
def ariadne_list_kernel_theories() -> list[dict]:
    """List all theories in the protected kernel seed set."""
    from .engine import AriadneEngine
    engine = AriadneEngine()
    return [
        {
            "id": t.id,
            "name": t.name,
            "domain": t.domain,
            "coverage_type": t.coverage.coverage_type if t.coverage else "unknown",
            "f_star_coordinates": t.f_star_coordinates,
            "novel_concepts": t.coverage.novel_concepts if t.coverage else [],
            "kernel_status": "protected"
        }
        for t in engine.kernel_theories
    ]

@mcp.tool()
def ariadne_feedback(theory_id: str, rating: int) -> str:
    """Rate a theory's usefulness (1-5) to update its credibility."""
    try:
        record_feedback(theory_id, rating)
        return f"Updated credibility for {theory_id}"
    except (ValueError, KeyError) as e:
        return f"Error: {e}"

if __name__ == "__main__":
    mcp.run()
