import os
import pytest
import json
from unittest.mock import MagicMock, patch
from ariadne.cli import analyze
from click.testing import CliRunner

@pytest.fixture(autouse=True)
def setup_env():
    os.environ["OPENROUTER_API_KEY"] = "sk-test"

@patch("ariadne.ai.OpenAI")
def test_analyze_flow(mock_openai_class, tmp_path):
    os.environ["ARIADNE_STORAGE_DIR"] = str(tmp_path)
    # Mock OpenAI client
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    # Mock chat completion for tag extraction
    mock_tag_response = MagicMock()
    mock_tag_response.choices = [MagicMock(message=MagicMock(content='["distributed", "network"]'))]

    # Mock embedding
    mock_emb_res = MagicMock()
    mock_emb_res.data = [MagicMock(embedding=[0.1]*1536) for _ in range(25)]
    mock_client.embeddings.create.return_value = mock_emb_res

    # Mock Stage 3 LLM response
    mock_stage3_res = MagicMock()
    mock_stage3_res.choices = [MagicMock(message=MagicMock(content=json.dumps({
        "isomorphism_map": {"a": "b"},
        "strategy": "test strategy",
        "explanation": "test explanation",
        "testable_prediction": "test prediction",
        "failure_conditions": ["c1"],
        "falsification_path": "fp",
        "role_score": 8,
        "memory_score": 8,
        "valence_score": 8,
        "transition_score": 8,
        "feedback_score": 8,
        "overall_score": 8.0,
        "novelty_score": 0.8,
        "falsifiability_score": 0.8
    })))]

    # QCycleExtractor makes 1 call for tags, then Engine makes 5 calls for hypotheses
    mock_client.chat.completions.create.side_effect = [mock_tag_response] + [mock_stage3_res]*10

    runner = CliRunner()
    result = runner.invoke(analyze, [
        "--domain", "Test Domain",
        "--description", "Test Description"
    ], input="a1\na2\na3\na4\na5\na6\na7\n")

    print(result.output)
    if result.exit_code != 0:
        print(result.exception)

    assert result.exit_code == 0
    assert "Generating hypotheses..." in result.output

    # Check persistence
    storage_dir = os.path.expanduser("~/.ariadne")
    assert os.path.exists(os.path.join(storage_dir, "domains/test_domain.json"))
    assert len(os.listdir(os.path.join(storage_dir, "sessions"))) > 0
