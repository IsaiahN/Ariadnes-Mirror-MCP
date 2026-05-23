import click
import json
import os
import datetime
from .engine import AriadneEngine
from .extractor import QCycleExtractor
from .models import DomainProfile

@click.group()
def main():
    """Ariadne's Mirror: Cross-domain structural mapping tool."""
    pass

@main.command()
@click.option('--domain', required=True, help='Target domain name')
@click.option('--description', required=True, help='Brief description')
def analyze(domain, description):
    """Analyze a domain and generate hypotheses."""
    try:
        from .config import settings
        settings.validate()
    except ValueError as e:
        click.echo(f"Error: {e}")
        return

    extractor = QCycleExtractor()
    click.echo(f"Starting Q-Cycle extraction for: {domain}")

    answers = {}
    click.echo("\nPlease answer the following questions to help characterize your domain:")
    for q_id, q_text in extractor.QUESTIONS.items():
        answer = click.prompt(f"[{q_id}] {q_text}")
        answers[q_id] = answer

    profile = extractor.run_extraction_cycle(domain, description, answers)
    engine = AriadneEngine()

    # Save domain profile
    domain_path = os.path.join(engine.storage_dir, f"domains/{domain.replace(' ', '_').lower()}.json")
    os.makedirs(os.path.dirname(domain_path), exist_ok=True)
    with open(domain_path, 'w') as f:
        f.write(profile.model_dump_json(indent=2))

    click.echo("Generating hypotheses...")
    hypotheses = engine.analyze(profile)

    # Save session
    session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_path = os.path.join(engine.storage_dir, f"sessions/session_{session_id}.json")
    os.makedirs(os.path.dirname(session_path), exist_ok=True)
    with open(session_path, 'w') as f:
        json.dump([h.model_dump() for h in hypotheses], f, indent=2)

    for i, hypo in enumerate(hypotheses):
        click.echo(f"\n--- Hypothesis {i+1}: {hypo.source_theory_id} ---")
        click.echo(f"Strategy: {hypo.strategy}")
        click.echo(f"Testable Prediction: {hypo.testable_prediction}")
        click.echo(f"Final Score: {hypo.final_score}")

@main.group()
def library():
    """Manage the theory library."""
    pass

@library.command(name='list')
def list_library():
    """List all theories in the library."""
    engine = AriadneEngine()
    for theory in engine.theories:
        click.echo(f"- {theory.name} ({theory.id}) [{theory.domain}] - Credibility: {theory.credibility_score:.2f}")

@main.command()
@click.option('--theory', required=True, help='Theory ID')
@click.option('--rating', required=True, type=click.IntRange(1, 5), help='Rating (1-5)')
def feedback(theory, rating):
    """Provide feedback on a theory to update its credibility."""
    engine = AriadneEngine()
    try:
        engine.update_credibility(theory, rating)
        click.echo(f"Feedback recorded for {theory}.")
    except (ValueError, KeyError) as e:
        click.echo(f"Error: {e}")

if __name__ == '__main__':
    main()
