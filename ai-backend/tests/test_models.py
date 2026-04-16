import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.models import ModelsService
from app.schemas import ModelsResponse, ModelInfo


@pytest.mark.asyncio
async def test_list_models_ollama():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [
            {"name": "mistral:latest", "size": 4000000000},
            {"name": "llama3:latest", "size": 8000000000},
        ]
    }
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp), \
         patch("app.services.models.mlflow") as mock_mlflow:
        mock_mlflow.search_registered_models.return_value = []
        service = ModelsService()
        result = await service.list_models()
        ollama_models = [m for m in result.models if m.source == "ollama"]
        assert len(ollama_models) == 2
        assert ollama_models[0].name == "mistral:latest"


@pytest.mark.asyncio
async def test_list_models_includes_mlflow():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"models": []}

    mock_registered = MagicMock()
    mock_registered.name = "test-bot-ft"

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp), \
         patch("app.services.models.mlflow") as mock_mlflow:
        mock_mlflow.search_registered_models.return_value = [mock_registered]
        service = ModelsService()
        result = await service.list_models()
        mlflow_models = [m for m in result.models if m.source == "mlflow"]
        assert len(mlflow_models) == 1
        assert mlflow_models[0].name == "test-bot-ft"


def test_models_endpoint(client):
    with patch("app.routers.models.ModelsService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.list_models = AsyncMock(
            return_value=ModelsResponse(
                models=[ModelInfo(name="mistral", source="ollama", status="available")]
            )
        )
        resp = client.get("/models")
        assert resp.status_code == 200
