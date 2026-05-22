import click
import json
import os
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
    extractor = QCycleExtractor()
    click.echo(f"Starting Q-Cycle extraction for: {domain}")

    answers = {}
    click.echo("\nPlease answer the following questions to help characterize your domain:")
    for q_id, q_text in extractor.QUESTIONS.items():
        answer = click.prompt(f"[{q_id}] {q_text}")
        answers[q_id] = answer

    profile = extractor.run_extraction_cycle(domain, description, answers)

    # Locate theories.yaml
    theories_path = os.path.join(os.path.dirname(__file__), '../../data/theories.yaml')
    engine = AriadneEngine(theories_path)

    click.echo("Generating hypotheses...")
    hypotheses = engine.analyze(profile)

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
    theories_path = os.path.join(os.path.dirname(__file__), '../../data/theories.yaml')
    engine = AriadneEngine(theories_path)
    for theory in engine.theories:
        click.echo(f"- {theory.name} ({theory.id}) [{theory.domain}] - Credibility: {theory.credibility_score:.2f}")

@main.command()
@click.option('--theory', required=True, help='Theory ID')
@click.option('--rating', required=True, type=int, help='Rating (1-5)')
def feedback(theory, rating):
    """Provide feedback on a theory to update its credibility."""
    theories_path = os.path.join(os.path.dirname(__file__), '../../data/theories.yaml')
    engine = AriadneEngine(theories_path)
    engine.update_credibility(theory, rating)
    click.echo(f"Feedback recorded for {theory}.")

if __name__ == '__main__':
    main()
