from fastapi import APIRouter

from app.schemas import FinetuneRequest, FinetuneResponse
from app.services.finetune import FinetuneService

router = APIRouter()


@router.post("/finetune", response_model=FinetuneResponse)
async def finetune(req: FinetuneRequest):
    service = FinetuneService()
    return await service.launch(
        base_model=req.base_model,
        dataset_path=req.dataset_path,
        bot_id=req.bot_id,
        num_epochs=req.num_epochs,
        learning_rate=req.learning_rate,
        lora_r=req.lora_r,
        lora_alpha=req.lora_alpha,
    )
