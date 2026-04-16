from typing import AsyncIterator
import httpx
import json

from app.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, prompt: str, **kwargs) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, **kwargs},
            )
            resp.raise_for_status()
            return resp.json()["response"]

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": True, **kwargs},
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
