from fastapi import APIRouter

from app.schemas import EvaluateRequest, EvaluateResponse
from app.services.evaluate import EvaluateService

router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(req: EvaluateRequest):
    service = EvaluateService()
    return await service.evaluate_from_file(
        bot_id=req.bot_id,
        test_dataset_path=req.test_dataset_path,
    )
