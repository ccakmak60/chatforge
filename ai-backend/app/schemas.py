from pydantic import BaseModel
from typing import Optional


class IngestRequest(BaseModel):
    bot_id: str
    namespace: Optional[str] = None


class IngestResponse(BaseModel):
    status: str
    chunks_created: int
    bot_id: str


class ChatRequest(BaseModel):
    session_id: str
    bot_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    bot_id: str
    response: str
    sources: list[str]


class FinetuneRequest(BaseModel):
    base_model: str
    dataset_path: str
    bot_id: str
    num_epochs: int = 3
    learning_rate: float = 2e-4
    lora_r: int = 8
    lora_alpha: int = 16


class FinetuneResponse(BaseModel):
    status: str
    run_id: str
    model_name: str


class EvaluateRequest(BaseModel):
    bot_id: str
    test_dataset_path: str


class EvaluateResponse(BaseModel):
    status: str
    metrics: dict
    run_id: str


class ModelInfo(BaseModel):
    name: str
    source: str
    status: str


class ModelsResponse(BaseModel):
    models: list[ModelInfo]


class ErrorResponse(BaseModel):
    code: int
    error: str
    detail: str
    request_id: Optional[str] = None
