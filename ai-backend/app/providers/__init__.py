from app.config import settings
from app.providers.base import LLMProvider
from app.providers.ollama import OllamaProvider
from app.providers.vllm import VLLMProvider


def get_provider() -> LLMProvider:
    if settings.llm_runtime == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        )
    elif settings.llm_runtime == "vllm":
        return VLLMProvider(
            base_url=settings.vllm_base_url,
            model=settings.vllm_model,
        )
    else:
        raise ValueError(f"Unknown LLM runtime: {settings.llm_runtime}")
