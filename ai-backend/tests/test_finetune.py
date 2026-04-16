import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.finetune import FinetuneService


@pytest.mark.asyncio
async def test_finetune_service_launches_job():
    mock_wandb = MagicMock()
    mock_wandb.init.return_value = MagicMock(id="wandb-run-123")
    mock_mlflow = MagicMock()
    mock_mlflow.start_run.return_value.__enter__ = MagicMock(
        return_value=MagicMock(info=MagicMock(run_id="mlflow-run-456"))
    )
    mock_mlflow.start_run.return_value.__exit__ = MagicMock(return_value=False)

    with patch("app.services.finetune.wandb", mock_wandb), \
         patch("app.services.finetune.mlflow", mock_mlflow), \
         patch("app.services.finetune.run_lora_finetune", new_callable=AsyncMock) as mock_train:
        mock_train.return_value = "/tmp/output_model"
        service = FinetuneService()
        result = await service.launch(
            base_model="mistralai/Mistral-7B-Instruct-v0.2",
            dataset_path="/tmp/data.json",
            bot_id="test-bot",
            num_epochs=1,
            learning_rate=2e-4,
            lora_r=8,
            lora_alpha=16,
        )
        assert result.status == "complete"
        assert "mlflow" in result.run_id or "wandb" in result.run_id or len(result.run_id) > 0


def test_finetune_endpoint(client):
    with patch("app.routers.finetune.FinetuneService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.launch = AsyncMock(
            return_value=MagicMock(status="complete", run_id="run-1", model_name="test-bot-ft")
        )
        resp = client.post("/finetune", json={
            "base_model": "mistral",
            "dataset_path": "/data/train.json",
            "bot_id": "test-bot",
            "num_epochs": 1,
            "learning_rate": 2e-4,
            "lora_r": 8,
            "lora_alpha": 16,
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "complete"
