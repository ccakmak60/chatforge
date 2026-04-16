import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.evaluate import EvaluateService, compute_faithfulness


def test_compute_faithfulness():
    score = compute_faithfulness(
        answer="Paris is the capital of France.",
        context="Paris is the capital of France. It is located in Europe.",
    )
    assert 0.0 <= score <= 1.0


@pytest.mark.asyncio
async def test_evaluate_service():
    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "Paris"

    mock_index = MagicMock()
    mock_index.query.return_value = MagicMock(
        matches=[MagicMock(metadata={"text": "Paris is the capital of France.", "source": "doc.txt"}, score=0.9)]
    )
    mock_embed = MagicMock()
    mock_embed.encode.return_value = [[0.1] * 384]

    with patch("app.services.evaluate.get_provider", return_value=mock_provider), \
         patch("app.services.evaluate.get_pinecone_index", return_value=mock_index), \
         patch("app.services.evaluate.get_embedding_model", return_value=mock_embed), \
         patch("app.services.evaluate.mlflow") as mock_mlflow:
        mock_mlflow.start_run.return_value.__enter__ = MagicMock(
            return_value=MagicMock(info=MagicMock(run_id="eval-run-1"))
        )
        mock_mlflow.start_run.return_value.__exit__ = MagicMock(return_value=False)

        service = EvaluateService()
        result = await service.evaluate(
            bot_id="test-bot",
            test_data=[
                {"question": "What is the capital of France?", "expected": "Paris"},
            ],
        )
        assert result.status == "complete"
        assert "faithfulness" in result.metrics
        assert "relevance" in result.metrics


def test_evaluate_endpoint(client):
    with patch("app.routers.evaluate.EvaluateService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.evaluate_from_file = AsyncMock(
            return_value=MagicMock(
                status="complete",
                metrics={"faithfulness": 0.85, "relevance": 0.9},
                run_id="eval-1",
            )
        )
        resp = client.post("/evaluate", json={
            "bot_id": "test-bot",
            "test_dataset_path": "/data/test.json",
        })
        assert resp.status_code == 200
        assert "faithfulness" in resp.json()["metrics"]
