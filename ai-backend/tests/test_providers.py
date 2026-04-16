import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.providers.base import LLMProvider
from app.providers.ollama import OllamaProvider
from app.providers.vllm import VLLMProvider
from app.providers import get_provider


def test_llm_provider_is_abstract():
    with pytest.raises(TypeError):
        LLMProvider()


def test_get_provider_ollama():
    with patch("app.providers.settings") as mock_settings:
        mock_settings.llm_runtime = "ollama"
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_settings.ollama_model = "mistral"
        provider = get_provider()
        assert isinstance(provider, OllamaProvider)


def test_get_provider_vllm():
    with patch("app.providers.settings") as mock_settings:
        mock_settings.llm_runtime = "vllm"
        mock_settings.vllm_base_url = "http://localhost:8000"
        mock_settings.vllm_model = "mistral-7b"
        provider = get_provider()
        assert isinstance(provider, VLLMProvider)


def test_get_provider_invalid():
    with patch("app.providers.settings") as mock_settings:
        mock_settings.llm_runtime = "invalid"
        with pytest.raises(ValueError, match="Unknown LLM runtime"):
            get_provider()


@pytest.mark.asyncio
async def test_ollama_generate():
    provider = OllamaProvider(base_url="http://test:11434", model="mistral")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "Hello world"}
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        result = await provider.generate("Say hello")
        assert result == "Hello world"


@pytest.mark.asyncio
async def test_vllm_generate():
    provider = VLLMProvider(base_url="http://test:8000", model="mistral-7b")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello world"}}]
    }
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        result = await provider.generate("Say hello")
        assert result == "Hello world"
