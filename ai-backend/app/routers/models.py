from fastapi import APIRouter

from app.schemas import ModelsResponse
from app.services.models import ModelsService

router = APIRouter()


@router.get("/models", response_model=ModelsResponse)
async def list_models():
    service = ModelsService()
    return await service.list_models()
