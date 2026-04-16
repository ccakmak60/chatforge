import httpx
import mlflow

from app.config import settings
from app.schemas import ModelInfo, ModelsResponse


class ModelsService:
    async def list_models(self) -> ModelsResponse:
        models: list[ModelInfo] = []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{settings.ollama_base_url}/api/tags")
                if resp.status_code == 200:
                    for m in resp.json().get("models", []):
                        models.append(
                            ModelInfo(
                                name=m["name"],
                                source="ollama",
                                status="available",
                            )
                        )
        except httpx.RequestError:
            pass

        try:
            mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
            for rm in mlflow.search_registered_models():
                models.append(
                    ModelInfo(
                        name=rm.name,
                        source="mlflow",
                        status="registered",
                    )
                )
        except Exception:
            pass

        return ModelsResponse(models=models)
