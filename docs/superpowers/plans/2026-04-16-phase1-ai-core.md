# ChatForge Phase 1: AI Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 1 MVP — a working AI backend with RAG, fine-tuning, evaluation, and a React chat UI, all running locally via Docker Compose with Ollama.

**Architecture:** Python FastAPI backend exposes `/ingest`, `/chat`, `/finetune`, `/evaluate`, `/models` endpoints. An `LLMProvider` abstraction swaps between Ollama (dev) and vLLM (prod) via env var. React frontend streams chat responses via SSE. Docker Compose orchestrates all three services.

**Tech Stack:** Python 3.11, FastAPI, LangChain, Pinecone, HuggingFace Transformers + PEFT, MLflow, W&B, sentence-transformers, React 18, Vite, Tailwind CSS, shadcn/ui, Docker Compose, Ollama.

---

## File Structure

```text
ai-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, CORS, error middleware
│   ├── config.py                # Pydantic BaseSettings
│   ├── schemas.py               # All request/response models
│   ├── providers/
│   │   ├── __init__.py          # get_provider() factory
│   │   ├── base.py              # LLMProvider ABC
│   │   ├── ollama.py            # OllamaProvider
│   │   └── vllm.py              # VLLMProvider
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ingest.py            # Chunking, embedding, Pinecone upsert
│   │   ├── chat.py              # RAG retrieval + prompt + streaming
│   │   ├── finetune.py          # LoRA fine-tune orchestration
│   │   ├── evaluate.py          # RAGAS-style eval + MLflow logging
│   │   └── models.py            # Model listing from Ollama + MLflow
│   └── routers/
│       ├── __init__.py
│       ├── ingest.py
│       ├── chat.py
│       ├── finetune.py
│       ├── evaluate.py
│       └── models.py
├── tests/
│   ├── conftest.py              # Shared fixtures, mocks
│   ├── test_config.py
│   ├── test_providers.py
│   ├── test_ingest.py
│   ├── test_chat.py
│   ├── test_finetune.py
│   ├── test_evaluate.py
│   └── test_models.py
├── requirements.txt
├── pytest.ini
├── Dockerfile
└── .env.example

web-ui/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── lib/
│   │   └── api.ts               # API client + SSE helper
│   ├── hooks/
│   │   ├── use-chat.ts          # Chat state + streaming hook
│   │   └── use-upload.ts        # File upload hook
│   └── components/
│       ├── chat/
│       │   ├── chat-panel.tsx   # Main chat layout
│       │   ├── message-list.tsx # Scrollable message thread
│       │   ├── message-input.tsx# Text input + send
│       │   └── bot-selector.tsx # Bot/model dropdown
│       └── upload/
│           └── upload-widget.tsx # Drag-and-drop file upload
├── __tests__/
│   ├── use-chat.test.ts
│   └── chat-panel.test.tsx
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── tsconfig.node.json
├── components.json
└── Dockerfile

infra/
├── docker-compose.yml
└── .env.example
```

---

## Task 1: AI Backend — Project Scaffolding + Config

**Files:**
- Create: `ai-backend/requirements.txt`
- Create: `ai-backend/pytest.ini`
- Create: `ai-backend/.env.example`
- Create: `ai-backend/app/__init__.py`
- Create: `ai-backend/app/config.py`
- Create: `ai-backend/app/main.py`
- Create: `ai-backend/app/schemas.py`
- Test: `ai-backend/tests/conftest.py`
- Test: `ai-backend/tests/test_config.py`

- [ ] **Step 1: Create `requirements.txt`**

```text
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic-settings==2.3.4
python-multipart==0.0.9
langchain==0.2.6
langchain-community==0.2.6
langchain-core==0.2.10
pinecone-client==4.0.0
sentence-transformers==3.0.1
transformers==4.42.3
peft==0.11.1
datasets==2.20.0
accelerate==0.31.0
torch==2.3.1
mlflow==2.14.1
wandb==0.17.4
httpx==0.27.0
python-docx==1.1.2
pypdf==4.2.0
tiktoken==0.7.0
pytest==8.2.2
pytest-asyncio==0.23.7
pytest-cov==5.0.0
```

- [ ] **Step 2: Create `pytest.ini`**

```ini
[pytest]
testpaths = tests
asyncio_mode = auto
```

- [ ] **Step 3: Create `.env.example`**

```env
LLM_RUNTIME=ollama
OLLAMA_BASE_URL=http://ollama:11434
VLLM_BASE_URL=http://vllm:8000
VLLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
OLLAMA_MODEL=mistral
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX=chatforge
PINECONE_NAMESPACE=default
EMBEDDING_MODEL=all-MiniLM-L6-v2
MLFLOW_TRACKING_URI=http://localhost:5000
WANDB_API_KEY=your-wandb-api-key
WANDB_PROJECT=chatforge
```

- [ ] **Step 4: Create `app/__init__.py`**

```python
```

(Empty init file.)

- [ ] **Step 5: Create `app/config.py`**

```python
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    llm_runtime: Literal["ollama", "vllm"] = "ollama"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "mistral"
    vllm_base_url: str = "http://vllm:8000"
    vllm_model: str = "mistralai/Mistral-7B-Instruct-v0.2"
    pinecone_api_key: str = ""
    pinecone_index: str = "chatforge"
    pinecone_namespace: str = "default"
    embedding_model: str = "all-MiniLM-L6-v2"
    mlflow_tracking_uri: str = "http://localhost:5000"
    wandb_api_key: str = ""
    wandb_project: str = "chatforge"
    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_top_k: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 6: Create `app/schemas.py`**

```python
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
    source: str  # "ollama" | "mlflow"
    status: str


class ModelsResponse(BaseModel):
    models: list[ModelInfo]


class ErrorResponse(BaseModel):
    code: int
    error: str
    detail: str
    request_id: Optional[str] = None
```

- [ ] **Step 7: Create `app/main.py`**

```python
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import ErrorResponse

app = FastAPI(title="ChatForge AI Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            code=500,
            error="internal_error",
            detail=str(exc),
            request_id=request_id,
        ).model_dump(),
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 8: Write tests — `tests/conftest.py` and `tests/test_config.py`**

`tests/conftest.py`:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
```

`tests/test_config.py`:
```python
from app.config import Settings


def test_default_settings():
    s = Settings(pinecone_api_key="test", wandb_api_key="test")
    assert s.llm_runtime == "ollama"
    assert s.chunk_size == 500
    assert s.retrieval_top_k == 5


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_request_id_header(client):
    resp = client.get("/health")
    assert "X-Request-ID" in resp.headers
```

- [ ] **Step 9: Install dependencies and run tests**

Run (from `ai-backend/`):
```bash
pip install -r requirements.txt
pytest tests/test_config.py -v
```
Expected: 3 tests PASS.

- [ ] **Step 10: Commit**

```bash
git add ai-backend/
git commit -m "feat(ai-backend): project scaffolding, config, health endpoint"
```

---

## Task 2: AI Backend — LLM Provider Abstraction

**Files:**
- Create: `ai-backend/app/providers/__init__.py`
- Create: `ai-backend/app/providers/base.py`
- Create: `ai-backend/app/providers/ollama.py`
- Create: `ai-backend/app/providers/vllm.py`
- Test: `ai-backend/tests/test_providers.py`

- [ ] **Step 1: Write failing tests — `tests/test_providers.py`**

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_providers.py -v`
Expected: FAIL (imports not found).

- [ ] **Step 3: Implement `app/providers/base.py`**

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        ...

    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        ...
```

- [ ] **Step 4: Implement `app/providers/ollama.py`**

```python
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
```

- [ ] **Step 5: Implement `app/providers/vllm.py`**

```python
from typing import AsyncIterator
import httpx
import json

from app.providers.base import LLMProvider


class VLLMProvider(LLMProvider):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, prompt: str, **kwargs) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    **kwargs,
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True,
                    **kwargs,
                },
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        data = json.loads(line[6:])
                        delta = data["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]
```

- [ ] **Step 6: Implement `app/providers/__init__.py`**

```python
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
```

- [ ] **Step 7: Run tests**

Run: `pytest tests/test_providers.py -v`
Expected: 6 tests PASS.

- [ ] **Step 8: Commit**

```bash
git add ai-backend/app/providers/ ai-backend/tests/test_providers.py
git commit -m "feat(ai-backend): LLM provider abstraction (Ollama + vLLM)"
```

---

## Task 3: AI Backend — Document Ingestion

**Files:**
- Create: `ai-backend/app/services/__init__.py`
- Create: `ai-backend/app/services/ingest.py`
- Create: `ai-backend/app/routers/__init__.py`
- Create: `ai-backend/app/routers/ingest.py`
- Modify: `ai-backend/app/main.py` (register router)
- Test: `ai-backend/tests/test_ingest.py`

- [ ] **Step 1: Write failing tests — `tests/test_ingest.py`**

```python
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.ingest import chunk_text, load_document, IngestService


def test_chunk_text_basic():
    text = "word " * 200  # 1000 chars
    chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) <= 550  # chunk_size + some tolerance


def test_chunk_text_small_input():
    text = "Hello world"
    chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == "Hello world"


def test_load_document_txt(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("Hello from a text file.")
    text = load_document(str(f))
    assert "Hello from a text file" in text


def test_load_document_unsupported(tmp_path):
    f = tmp_path / "test.xyz"
    f.write_text("data")
    with pytest.raises(ValueError, match="Unsupported file type"):
        load_document(str(f))


@pytest.mark.asyncio
async def test_ingest_service_processes_file(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_text("This is test content for ingestion. " * 20)

    mock_index = MagicMock()
    mock_index.upsert = MagicMock()

    mock_embed_model = MagicMock()
    mock_embed_model.encode.return_value = [[0.1] * 384]

    with patch("app.services.ingest.get_pinecone_index", return_value=mock_index), \
         patch("app.services.ingest.get_embedding_model", return_value=mock_embed_model):
        service = IngestService()
        result = await service.ingest_file(str(f), bot_id="test-bot", namespace="test")
        assert result.status == "complete"
        assert result.chunks_created > 0
        assert result.bot_id == "test-bot"


def test_ingest_endpoint_accepts_file(client):
    import io
    with patch("app.routers.ingest.IngestService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.ingest_file = AsyncMock(
            return_value=MagicMock(status="complete", chunks_created=5, bot_id="test")
        )
        resp = client.post(
            "/ingest",
            data={"bot_id": "test"},
            files={"file": ("test.txt", io.BytesIO(b"hello world"), "text/plain")},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "complete"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_ingest.py -v`
Expected: FAIL (imports not found).

- [ ] **Step 3: Implement `app/services/__init__.py`**

```python
```

(Empty init.)

- [ ] **Step 4: Implement `app/services/ingest.py`**

```python
import os
from pathlib import Path

from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.schemas import IngestResponse


def get_pinecone_index():
    pc = Pinecone(api_key=settings.pinecone_api_key)
    return pc.Index(settings.pinecone_index)


def get_embedding_model():
    return SentenceTransformer(settings.embedding_model)


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks


def load_document(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif ext == ".docx":
        from docx import Document
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    elif ext == ".json":
        import json
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


class IngestService:
    def __init__(self):
        self.index = get_pinecone_index()
        self.embed_model = get_embedding_model()

    async def ingest_file(
        self, file_path: str, bot_id: str, namespace: str | None = None
    ) -> IngestResponse:
        ns = namespace or settings.pinecone_namespace
        text = load_document(file_path)
        chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
        embeddings = self.embed_model.encode(chunks).tolist()

        vectors = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            vec_id = f"{bot_id}_{Path(file_path).stem}_{i}"
            vectors.append({
                "id": vec_id,
                "values": emb,
                "metadata": {"text": chunk, "bot_id": bot_id, "source": Path(file_path).name},
            })

        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            self.index.upsert(vectors=vectors[i : i + batch_size], namespace=ns)

        return IngestResponse(status="complete", chunks_created=len(chunks), bot_id=bot_id)
```

- [ ] **Step 5: Implement `app/routers/__init__.py`**

```python
```

(Empty init.)

- [ ] **Step 6: Implement `app/routers/ingest.py`**

```python
import os
import tempfile
import shutil

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.schemas import IngestResponse
from app.services.ingest import IngestService

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    bot_id: str = Form(...),
    namespace: str | None = Form(None),
):
    tmp_dir = tempfile.mkdtemp()
    try:
        file_path = os.path.join(tmp_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        service = IngestService()
        result = await service.ingest_file(file_path, bot_id=bot_id, namespace=namespace)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
```

- [ ] **Step 7: Register router in `app/main.py`**

Add after the `health` endpoint:

```python
from app.routers.ingest import router as ingest_router

app.include_router(ingest_router)
```

- [ ] **Step 8: Run tests**

Run: `pytest tests/test_ingest.py -v`
Expected: 5 tests PASS.

- [ ] **Step 9: Commit**

```bash
git add ai-backend/app/services/ ai-backend/app/routers/ ai-backend/tests/test_ingest.py
git commit -m "feat(ai-backend): document ingestion with chunking and Pinecone upsert"
```

---

## Task 4: AI Backend — RAG Chat with SSE Streaming

**Files:**
- Create: `ai-backend/app/services/chat.py`
- Create: `ai-backend/app/routers/chat.py`
- Modify: `ai-backend/app/main.py` (register router)
- Test: `ai-backend/tests/test_chat.py`

- [ ] **Step 1: Write failing tests — `tests/test_chat.py`**

```python
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.chat import ChatService


@pytest.mark.asyncio
async def test_chat_service_returns_response():
    mock_index = MagicMock()
    mock_index.query.return_value = MagicMock(
        matches=[
            MagicMock(metadata={"text": "Paris is the capital of France.", "source": "doc.txt"}, score=0.95),
        ]
    )
    mock_embed = MagicMock()
    mock_embed.encode.return_value = [[0.1] * 384]

    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "Paris is the capital of France."

    with patch("app.services.chat.get_pinecone_index", return_value=mock_index), \
         patch("app.services.chat.get_embedding_model", return_value=mock_embed), \
         patch("app.services.chat.get_provider", return_value=mock_provider):
        service = ChatService()
        result = await service.get_response(
            message="What is the capital of France?",
            bot_id="test-bot",
            session_id="sess-1",
        )
        assert result.response == "Paris is the capital of France."
        assert len(result.sources) == 1
        assert result.session_id == "sess-1"


def test_chat_endpoint_returns_json(client):
    with patch("app.routers.chat.ChatService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.get_response = AsyncMock(
            return_value=MagicMock(
                session_id="s1", bot_id="b1",
                response="Hello", sources=["doc.txt"],
            )
        )
        resp = client.post("/chat", json={
            "session_id": "s1", "bot_id": "b1", "message": "Hi"
        })
        assert resp.status_code == 200
        assert resp.json()["response"] == "Hello"


def test_chat_stream_endpoint(client):
    async def mock_stream(*args, **kwargs):
        for word in ["Hello", " ", "world"]:
            yield word

    with patch("app.routers.chat.ChatService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.stream_response = mock_stream
        resp = client.post(
            "/chat/stream",
            json={"session_id": "s1", "bot_id": "b1", "message": "Hi"},
        )
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_chat.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `app/services/chat.py`**

```python
from typing import AsyncIterator

from app.config import settings
from app.schemas import ChatResponse
from app.providers import get_provider
from app.services.ingest import get_pinecone_index, get_embedding_model


SYSTEM_PROMPT = """You are a helpful assistant. Answer the user's question based on the provided context.
If the context doesn't contain relevant information, say so honestly.

Context:
{context}

Question: {question}

Answer:"""


class ChatService:
    def __init__(self):
        self.index = get_pinecone_index()
        self.embed_model = get_embedding_model()
        self.provider = get_provider()

    def _retrieve_context(self, message: str, bot_id: str, namespace: str | None = None) -> tuple[str, list[str]]:
        ns = namespace or settings.pinecone_namespace
        query_embedding = self.embed_model.encode([message])[0].tolist()
        results = self.index.query(
            vector=query_embedding,
            top_k=settings.retrieval_top_k,
            include_metadata=True,
            namespace=ns,
            filter={"bot_id": {"$eq": bot_id}},
        )
        context_parts = []
        sources = []
        for match in results.matches:
            context_parts.append(match.metadata["text"])
            source = match.metadata.get("source", "unknown")
            if source not in sources:
                sources.append(source)
        context = "\n\n".join(context_parts)
        return context, sources

    async def get_response(
        self, message: str, bot_id: str, session_id: str, namespace: str | None = None
    ) -> ChatResponse:
        context, sources = self._retrieve_context(message, bot_id, namespace)
        prompt = SYSTEM_PROMPT.format(context=context, question=message)
        response = await self.provider.generate(prompt)
        return ChatResponse(
            session_id=session_id,
            bot_id=bot_id,
            response=response,
            sources=sources,
        )

    async def stream_response(
        self, message: str, bot_id: str, session_id: str, namespace: str | None = None
    ) -> AsyncIterator[str]:
        context, sources = self._retrieve_context(message, bot_id, namespace)
        prompt = SYSTEM_PROMPT.format(context=context, question=message)
        async for token in self.provider.stream(prompt):
            yield token
```

- [ ] **Step 4: Implement `app/routers/chat.py`**

```python
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas import ChatRequest, ChatResponse
from app.services.chat import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    service = ChatService()
    return await service.get_response(
        message=req.message,
        bot_id=req.bot_id,
        session_id=req.session_id,
    )


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    service = ChatService()

    async def event_generator():
        async for token in service.stream_response(
            message=req.message,
            bot_id=req.bot_id,
            session_id=req.session_id,
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

- [ ] **Step 5: Register router in `app/main.py`**

Add:
```python
from app.routers.chat import router as chat_router

app.include_router(chat_router)
```

- [ ] **Step 6: Run tests**

Run: `pytest tests/test_chat.py -v`
Expected: 3 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add ai-backend/app/services/chat.py ai-backend/app/routers/chat.py ai-backend/tests/test_chat.py
git commit -m "feat(ai-backend): RAG chat with SSE streaming"
```

---

## Task 5: AI Backend — Fine-Tuning Service

**Files:**
- Create: `ai-backend/app/services/finetune.py`
- Create: `ai-backend/app/routers/finetune.py`
- Modify: `ai-backend/app/main.py` (register router)
- Test: `ai-backend/tests/test_finetune.py`

- [ ] **Step 1: Write failing tests — `tests/test_finetune.py`**

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_finetune.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `app/services/finetune.py`**

```python
import asyncio
import os

import mlflow
import wandb
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset

from app.config import settings
from app.schemas import FinetuneResponse


async def run_lora_finetune(
    base_model: str,
    dataset_path: str,
    output_dir: str,
    num_epochs: int,
    learning_rate: float,
    lora_r: int,
    lora_alpha: int,
) -> str:
    def _train():
        tokenizer = AutoTokenizer.from_pretrained(base_model)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            base_model, device_map="auto", torch_dtype="auto"
        )

        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=lora_r,
            lora_alpha=lora_alpha,
            lora_dropout=0.05,
            target_modules=["q_proj", "v_proj"],
        )
        model = get_peft_model(model, lora_config)

        dataset = load_dataset("json", data_files=dataset_path, split="train")

        def tokenize(example):
            return tokenizer(
                example["text"], truncation=True, padding="max_length", max_length=512
            )

        dataset = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)
        dataset = dataset.add_column("labels", dataset["input_ids"])

        from transformers import Trainer

        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            learning_rate=learning_rate,
            per_device_train_batch_size=4,
            save_strategy="epoch",
            logging_steps=10,
            report_to=["wandb"],
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            tokenizer=tokenizer,
        )
        trainer.train()
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        return output_dir

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _train)


class FinetuneService:
    async def launch(
        self,
        base_model: str,
        dataset_path: str,
        bot_id: str,
        num_epochs: int = 3,
        learning_rate: float = 2e-4,
        lora_r: int = 8,
        lora_alpha: int = 16,
    ) -> FinetuneResponse:
        model_name = f"{bot_id}-ft"
        output_dir = f"/tmp/chatforge_finetune/{model_name}"
        os.makedirs(output_dir, exist_ok=True)

        wandb.init(
            project=settings.wandb_project,
            name=f"finetune-{model_name}",
            config={
                "base_model": base_model,
                "num_epochs": num_epochs,
                "learning_rate": learning_rate,
                "lora_r": lora_r,
                "lora_alpha": lora_alpha,
            },
        )

        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        with mlflow.start_run(run_name=f"finetune-{model_name}") as run:
            mlflow.log_params({
                "base_model": base_model,
                "num_epochs": num_epochs,
                "learning_rate": learning_rate,
                "lora_r": lora_r,
                "lora_alpha": lora_alpha,
                "bot_id": bot_id,
            })

            output_path = await run_lora_finetune(
                base_model=base_model,
                dataset_path=dataset_path,
                output_dir=output_dir,
                num_epochs=num_epochs,
                learning_rate=learning_rate,
                lora_r=lora_r,
                lora_alpha=lora_alpha,
            )

            mlflow.log_artifacts(output_path, artifact_path="model")
            mlflow.log_param("output_dir", output_path)

            run_id = run.info.run_id

        wandb.finish()

        return FinetuneResponse(
            status="complete",
            run_id=run_id,
            model_name=model_name,
        )
```

- [ ] **Step 4: Implement `app/routers/finetune.py`**

```python
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
```

- [ ] **Step 5: Register router in `app/main.py`**

Add:
```python
from app.routers.finetune import router as finetune_router

app.include_router(finetune_router)
```

- [ ] **Step 6: Run tests**

Run: `pytest tests/test_finetune.py -v`
Expected: 2 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add ai-backend/app/services/finetune.py ai-backend/app/routers/finetune.py ai-backend/tests/test_finetune.py
git commit -m "feat(ai-backend): LoRA fine-tuning with W&B + MLflow tracking"
```

---

## Task 6: AI Backend — Evaluation Service

**Files:**
- Create: `ai-backend/app/services/evaluate.py`
- Create: `ai-backend/app/routers/evaluate.py`
- Modify: `ai-backend/app/main.py` (register router)
- Test: `ai-backend/tests/test_evaluate.py`

- [ ] **Step 1: Write failing tests — `tests/test_evaluate.py`**

```python
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.evaluate import EvaluateService, compute_faithfulness


def test_compute_faithfulness():
    score = compute_faithfulness(
        answer="Paris is the capital of France.",
        context="Paris is the capital of France. It is located in Europe.",
    )
    assert 0.0 <= score <= 1.0


@pytest.mark.asyncio
async def test_evaluate_service():
    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "Paris"

    mock_index = MagicMock()
    mock_index.query.return_value = MagicMock(
        matches=[MagicMock(metadata={"text": "Paris is the capital of France.", "source": "doc.txt"}, score=0.9)]
    )
    mock_embed = MagicMock()
    mock_embed.encode.return_value = [[0.1] * 384]

    with patch("app.services.evaluate.get_provider", return_value=mock_provider), \
         patch("app.services.evaluate.get_pinecone_index", return_value=mock_index), \
         patch("app.services.evaluate.get_embedding_model", return_value=mock_embed), \
         patch("app.services.evaluate.mlflow") as mock_mlflow:
        mock_mlflow.start_run.return_value.__enter__ = MagicMock(
            return_value=MagicMock(info=MagicMock(run_id="eval-run-1"))
        )
        mock_mlflow.start_run.return_value.__exit__ = MagicMock(return_value=False)

        service = EvaluateService()
        result = await service.evaluate(
            bot_id="test-bot",
            test_data=[
                {"question": "What is the capital of France?", "expected": "Paris"},
            ],
        )
        assert result.status == "complete"
        assert "faithfulness" in result.metrics
        assert "relevance" in result.metrics


def test_evaluate_endpoint(client):
    with patch("app.routers.evaluate.EvaluateService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.evaluate_from_file = AsyncMock(
            return_value=MagicMock(
                status="complete",
                metrics={"faithfulness": 0.85, "relevance": 0.9},
                run_id="eval-1",
            )
        )
        resp = client.post("/evaluate", json={
            "bot_id": "test-bot",
            "test_dataset_path": "/data/test.json",
        })
        assert resp.status_code == 200
        assert "faithfulness" in resp.json()["metrics"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_evaluate.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `app/services/evaluate.py`**

```python
import json

import mlflow

from app.config import settings
from app.schemas import EvaluateResponse
from app.providers import get_provider
from app.services.ingest import get_pinecone_index, get_embedding_model


def compute_faithfulness(answer: str, context: str) -> float:
    answer_words = set(answer.lower().split())
    context_words = set(context.lower().split())
    if not answer_words:
        return 0.0
    overlap = answer_words & context_words
    return len(overlap) / len(answer_words)


def compute_relevance(answer: str, expected: str) -> float:
    answer_words = set(answer.lower().split())
    expected_words = set(expected.lower().split())
    if not expected_words:
        return 0.0
    overlap = answer_words & expected_words
    return len(overlap) / len(expected_words)


class EvaluateService:
    def __init__(self):
        self.index = get_pinecone_index()
        self.embed_model = get_embedding_model()
        self.provider = get_provider()

    async def evaluate(
        self, bot_id: str, test_data: list[dict]
    ) -> EvaluateResponse:
        faithfulness_scores = []
        relevance_scores = []

        for item in test_data:
            question = item["question"]
            expected = item["expected"]

            query_emb = self.embed_model.encode([question])[0].tolist()
            results = self.index.query(
                vector=query_emb,
                top_k=settings.retrieval_top_k,
                include_metadata=True,
                namespace=settings.pinecone_namespace,
                filter={"bot_id": {"$eq": bot_id}},
            )
            context = "\n".join(m.metadata["text"] for m in results.matches)

            answer = await self.provider.generate(
                f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
            )

            faithfulness_scores.append(compute_faithfulness(answer, context))
            relevance_scores.append(compute_relevance(answer, expected))

        metrics = {
            "faithfulness": sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0.0,
            "relevance": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0,
            "num_samples": len(test_data),
        }

        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        with mlflow.start_run(run_name=f"eval-{bot_id}") as run:
            mlflow.log_metrics(metrics)
            mlflow.log_param("bot_id", bot_id)
            run_id = run.info.run_id

        return EvaluateResponse(status="complete", metrics=metrics, run_id=run_id)

    async def evaluate_from_file(
        self, bot_id: str, test_dataset_path: str
    ) -> EvaluateResponse:
        with open(test_dataset_path, "r") as f:
            test_data = json.load(f)
        return await self.evaluate(bot_id=bot_id, test_data=test_data)
```

- [ ] **Step 4: Implement `app/routers/evaluate.py`**

```python
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
```

- [ ] **Step 5: Register router in `app/main.py`**

Add:
```python
from app.routers.evaluate import router as evaluate_router

app.include_router(evaluate_router)
```

- [ ] **Step 6: Run tests**

Run: `pytest tests/test_evaluate.py -v`
Expected: 3 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add ai-backend/app/services/evaluate.py ai-backend/app/routers/evaluate.py ai-backend/tests/test_evaluate.py
git commit -m "feat(ai-backend): evaluation service with faithfulness and relevance metrics"
```

---

## Task 7: AI Backend — Models Listing

**Files:**
- Create: `ai-backend/app/services/models.py`
- Create: `ai-backend/app/routers/models.py`
- Modify: `ai-backend/app/main.py` (register router)
- Test: `ai-backend/tests/test_models.py`

- [ ] **Step 1: Write failing tests — `tests/test_models.py`**

```python
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.models import ModelsService


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
            return_value=MagicMock(
                models=[MagicMock(name="mistral", source="ollama", status="available")]
            )
        )
        resp = client.get("/models")
        assert resp.status_code == 200
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_models.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `app/services/models.py`**

```python
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
                        models.append(ModelInfo(
                            name=m["name"],
                            source="ollama",
                            status="available",
                        ))
        except httpx.RequestError:
            pass

        try:
            mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
            for rm in mlflow.search_registered_models():
                models.append(ModelInfo(
                    name=rm.name,
                    source="mlflow",
                    status="registered",
                ))
        except Exception:
            pass

        return ModelsResponse(models=models)
```

- [ ] **Step 4: Implement `app/routers/models.py`**

```python
from fastapi import APIRouter

from app.schemas import ModelsResponse
from app.services.models import ModelsService

router = APIRouter()


@router.get("/models", response_model=ModelsResponse)
async def list_models():
    service = ModelsService()
    return await service.list_models()
```

- [ ] **Step 5: Register router in `app/main.py`**

Add:
```python
from app.routers.models import router as models_router

app.include_router(models_router)
```

- [ ] **Step 6: Run tests**

Run: `pytest tests/test_models.py -v`
Expected: 3 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add ai-backend/app/services/models.py ai-backend/app/routers/models.py ai-backend/tests/test_models.py
git commit -m "feat(ai-backend): model listing from Ollama + MLflow registry"
```

---

## Task 8: AI Backend — Dockerfile

**Files:**
- Create: `ai-backend/Dockerfile`

- [ ] **Step 1: Create `ai-backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Commit**

```bash
git add ai-backend/Dockerfile
git commit -m "feat(ai-backend): add Dockerfile"
```

---

## Task 9: Web UI — Project Scaffolding

**Files:**
- Create: `web-ui/package.json`
- Create: `web-ui/index.html`
- Create: `web-ui/vite.config.ts`
- Create: `web-ui/tailwind.config.js`
- Create: `web-ui/postcss.config.js`
- Create: `web-ui/tsconfig.json`
- Create: `web-ui/tsconfig.node.json`
- Create: `web-ui/components.json`
- Create: `web-ui/src/main.tsx`
- Create: `web-ui/src/App.tsx`
- Create: `web-ui/src/index.css`
- Create: `web-ui/src/lib/utils.ts`

- [ ] **Step 1: Create `web-ui/package.json`**

```json
{
  "name": "chatforge-web-ui",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.3.0",
    "lucide-react": "^0.395.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.4",
    "typescript": "^5.4.5",
    "vite": "^5.3.1",
    "vitest": "^1.6.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.4.6",
    "jsdom": "^24.1.0"
  }
}
```

- [ ] **Step 2: Create `web-ui/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ChatForge</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 3: Create `web-ui/vite.config.ts`**

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
```

- [ ] **Step 4: Create `web-ui/tailwind.config.js`**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
};
```

- [ ] **Step 5: Create `web-ui/postcss.config.js`**

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

- [ ] **Step 6: Create `web-ui/tsconfig.json` and `web-ui/tsconfig.node.json`**

`tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

`tsconfig.node.json`:
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 7: Create `web-ui/components.json`**

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/index.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

- [ ] **Step 8: Create `web-ui/src/index.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --radius: 0.5rem;
}
```

- [ ] **Step 9: Create `web-ui/src/lib/utils.ts`**

```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

- [ ] **Step 10: Create `web-ui/src/main.tsx`**

```typescript
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 11: Create `web-ui/src/App.tsx`**

```typescript
import { ChatPanel } from "@/components/chat/chat-panel";

export default function App() {
  return (
    <div className="flex h-screen bg-neutral-50">
      <main className="flex flex-1 flex-col">
        <header className="flex h-14 items-center border-b bg-white px-6">
          <h1 className="text-lg font-semibold">ChatForge</h1>
        </header>
        <ChatPanel />
      </main>
    </div>
  );
}
```

- [ ] **Step 12: Install deps and verify build**

Run (from `web-ui/`):
```bash
npm install
npx shadcn-ui@latest add button input scroll-area card avatar
npm run build
```
Expected: build succeeds with no errors.

- [ ] **Step 13: Commit**

```bash
git add web-ui/
git commit -m "feat(web-ui): project scaffolding with Vite, Tailwind, shadcn/ui"
```

---

## Task 10: Web UI — API Client + Hooks

**Files:**
- Create: `web-ui/src/lib/api.ts`
- Create: `web-ui/src/hooks/use-chat.ts`
- Create: `web-ui/src/hooks/use-upload.ts`
- Test: `web-ui/__tests__/use-chat.test.ts`

- [ ] **Step 1: Create `web-ui/src/lib/api.ts`**

```typescript
const API_BASE = "/api";

export async function postChat(body: {
  session_id: string;
  bot_id: string;
  message: string;
}) {
  const resp = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) throw new Error(`Chat failed: ${resp.status}`);
  return resp.json();
}

export async function streamChat(
  body: { session_id: string; bot_id: string; message: string },
  onToken: (token: string) => void,
  onDone: () => void
) {
  const resp = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) throw new Error(`Stream failed: ${resp.status}`);
  const reader = resp.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const payload = line.slice(6);
        if (payload === "[DONE]") {
          onDone();
          return;
        }
        const data = JSON.parse(payload);
        if (data.token) onToken(data.token);
      }
    }
  }
  onDone();
}

export async function uploadFile(file: File, botId: string) {
  const form = new FormData();
  form.append("file", file);
  form.append("bot_id", botId);
  const resp = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    body: form,
  });
  if (!resp.ok) throw new Error(`Upload failed: ${resp.status}`);
  return resp.json();
}

export async function fetchModels() {
  const resp = await fetch(`${API_BASE}/models`);
  if (!resp.ok) throw new Error(`Models failed: ${resp.status}`);
  return resp.json();
}
```

- [ ] **Step 2: Create `web-ui/src/hooks/use-chat.ts`**

```typescript
import { useState, useCallback, useRef } from "react";
import { streamChat } from "@/lib/api";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export function useChat(botId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const sessionId = useRef(crypto.randomUUID());

  const sendMessage = useCallback(
    async (content: string) => {
      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content,
      };
      const assistantId = crypto.randomUUID();

      setMessages((prev) => [
        ...prev,
        userMsg,
        { id: assistantId, role: "assistant", content: "" },
      ]);
      setIsStreaming(true);

      try {
        await streamChat(
          {
            session_id: sessionId.current,
            bot_id: botId,
            message: content,
          },
          (token) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: m.content + token }
                  : m
              )
            );
          },
          () => setIsStreaming(false)
        );
      } catch {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: "Error: Failed to get response." }
              : m
          )
        );
        setIsStreaming(false);
      }
    },
    [botId]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    sessionId.current = crypto.randomUUID();
  }, []);

  return { messages, isStreaming, sendMessage, clearMessages };
}
```

- [ ] **Step 3: Create `web-ui/src/hooks/use-upload.ts`**

```typescript
import { useState, useCallback } from "react";
import { uploadFile } from "@/lib/api";

export interface UploadState {
  isUploading: boolean;
  progress: string;
  error: string | null;
  lastResult: { chunks_created: number } | null;
}

export function useUpload(botId: string) {
  const [state, setState] = useState<UploadState>({
    isUploading: false,
    progress: "",
    error: null,
    lastResult: null,
  });

  const upload = useCallback(
    async (file: File) => {
      setState({ isUploading: true, progress: "Uploading...", error: null, lastResult: null });
      try {
        const result = await uploadFile(file, botId);
        setState({
          isUploading: false,
          progress: "",
          error: null,
          lastResult: { chunks_created: result.chunks_created },
        });
        return result;
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Upload failed";
        setState({ isUploading: false, progress: "", error: message, lastResult: null });
        throw err;
      }
    },
    [botId]
  );

  return { ...state, upload };
}
```

- [ ] **Step 4: Write test — `__tests__/use-chat.test.ts`**

```typescript
import { describe, it, expect, vi } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useChat } from "../src/hooks/use-chat";

vi.mock("../src/lib/api", () => ({
  streamChat: vi.fn(async (_body, onToken, onDone) => {
    onToken("Hello");
    onToken(" world");
    onDone();
  }),
}));

describe("useChat", () => {
  it("adds user and assistant messages on send", async () => {
    const { result } = renderHook(() => useChat("test-bot"));

    await act(async () => {
      await result.current.sendMessage("Hi");
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0].role).toBe("user");
    expect(result.current.messages[0].content).toBe("Hi");
    expect(result.current.messages[1].role).toBe("assistant");
    expect(result.current.messages[1].content).toBe("Hello world");
  });

  it("clears messages", async () => {
    const { result } = renderHook(() => useChat("test-bot"));

    await act(async () => {
      await result.current.sendMessage("Hi");
    });
    expect(result.current.messages).toHaveLength(2);

    act(() => {
      result.current.clearMessages();
    });
    expect(result.current.messages).toHaveLength(0);
  });
});
```

- [ ] **Step 5: Run tests**

Run (from `web-ui/`):
```bash
npx vitest run __tests__/use-chat.test.ts
```
Expected: 2 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add web-ui/src/lib/ web-ui/src/hooks/ web-ui/__tests__/
git commit -m "feat(web-ui): API client, useChat and useUpload hooks"
```

---

## Task 11: Web UI — Chat Interface Components

**Files:**
- Create: `web-ui/src/components/chat/chat-panel.tsx`
- Create: `web-ui/src/components/chat/message-list.tsx`
- Create: `web-ui/src/components/chat/message-input.tsx`
- Create: `web-ui/src/components/chat/bot-selector.tsx`

- [ ] **Step 1: Create `web-ui/src/components/chat/message-list.tsx`**

```typescript
import { Message } from "@/hooks/use-chat";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import { useEffect, useRef } from "react";

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center text-neutral-400">
        <p>Send a message to start chatting.</p>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1 p-4">
      <div className="mx-auto flex max-w-3xl flex-col gap-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={cn(
              "flex gap-3",
              msg.role === "user" ? "justify-end" : "justify-start"
            )}
          >
            {msg.role === "assistant" && (
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-blue-600 text-white text-xs">
                  AI
                </AvatarFallback>
              </Avatar>
            )}
            <div
              className={cn(
                "max-w-[80%] rounded-lg px-4 py-2 text-sm",
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-white border text-neutral-900"
              )}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
```

- [ ] **Step 2: Create `web-ui/src/components/chat/message-input.tsx`**

```typescript
import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send } from "lucide-react";

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 border-t bg-white p-4">
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Type a message..."
        disabled={disabled}
        className="flex-1"
      />
      <Button type="submit" disabled={disabled || !value.trim()} size="icon">
        <Send className="h-4 w-4" />
      </Button>
    </form>
  );
}
```

- [ ] **Step 3: Create `web-ui/src/components/chat/bot-selector.tsx`**

```typescript
import { useEffect, useState } from "react";
import { fetchModels } from "@/lib/api";

interface BotSelectorProps {
  value: string;
  onChange: (botId: string) => void;
}

interface ModelInfo {
  name: string;
  source: string;
  status: string;
}

export function BotSelector({ value, onChange }: BotSelectorProps) {
  const [models, setModels] = useState<ModelInfo[]>([]);

  useEffect(() => {
    fetchModels()
      .then((data) => setModels(data.models || []))
      .catch(() => setModels([]));
  }, []);

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm"
    >
      <option value="default">default</option>
      {models.map((m) => (
        <option key={m.name} value={m.name}>
          {m.name} ({m.source})
        </option>
      ))}
    </select>
  );
}
```

- [ ] **Step 4: Create `web-ui/src/components/chat/chat-panel.tsx`**

```typescript
import { useState } from "react";
import { useChat } from "@/hooks/use-chat";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";
import { BotSelector } from "./bot-selector";

export function ChatPanel() {
  const [botId, setBotId] = useState("default");
  const { messages, isStreaming, sendMessage, clearMessages } = useChat(botId);

  return (
    <div className="flex flex-1 flex-col">
      <div className="flex items-center gap-3 border-b bg-white px-4 py-2">
        <span className="text-sm text-neutral-500">Bot:</span>
        <BotSelector value={botId} onChange={setBotId} />
        <button
          onClick={clearMessages}
          className="ml-auto text-xs text-neutral-400 hover:text-neutral-600"
        >
          Clear chat
        </button>
      </div>
      <MessageList messages={messages} />
      <MessageInput onSend={sendMessage} disabled={isStreaming} />
    </div>
  );
}
```

- [ ] **Step 5: Verify build**

Run (from `web-ui/`):
```bash
npm run build
```
Expected: build succeeds.

- [ ] **Step 6: Commit**

```bash
git add web-ui/src/components/
git commit -m "feat(web-ui): chat panel, message list, input, bot selector"
```

---

## Task 12: Web UI — Upload Widget

**Files:**
- Create: `web-ui/src/components/upload/upload-widget.tsx`
- Modify: `web-ui/src/App.tsx` (add upload to sidebar)

- [ ] **Step 1: Create `web-ui/src/components/upload/upload-widget.tsx`**

```typescript
import { useCallback, useRef } from "react";
import { useUpload } from "@/hooks/use-upload";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload } from "lucide-react";

interface UploadWidgetProps {
  botId: string;
}

export function UploadWidget({ botId }: UploadWidgetProps) {
  const { isUploading, progress, error, lastResult, upload } = useUpload(botId);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) upload(file);
    },
    [upload]
  );

  const handleFileSelect = useCallback(() => {
    const file = inputRef.current?.files?.[0];
    if (file) upload(file);
  }, [upload]);

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm">Upload Documents</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="flex flex-col items-center gap-2 rounded-lg border-2 border-dashed border-neutral-200 p-6 text-center hover:border-neutral-400"
        >
          <Upload className="h-8 w-8 text-neutral-400" />
          <p className="text-xs text-neutral-500">
            Drag a file here or click to browse
          </p>
          <input
            ref={inputRef}
            type="file"
            accept=".txt,.pdf,.docx,.json"
            onChange={handleFileSelect}
            className="hidden"
          />
          <Button
            variant="outline"
            size="sm"
            onClick={() => inputRef.current?.click()}
            disabled={isUploading}
          >
            {isUploading ? progress : "Choose File"}
          </Button>
        </div>
        {error && <p className="mt-2 text-xs text-red-500">{error}</p>}
        {lastResult && (
          <p className="mt-2 text-xs text-green-600">
            Ingested {lastResult.chunks_created} chunks
          </p>
        )}
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: Update `web-ui/src/App.tsx` to include upload sidebar**

```typescript
import { useState } from "react";
import { ChatPanel } from "@/components/chat/chat-panel";
import { UploadWidget } from "@/components/upload/upload-widget";

export default function App() {
  const [botId] = useState("default");

  return (
    <div className="flex h-screen bg-neutral-50">
      <aside className="flex w-72 flex-col gap-4 border-r bg-white p-4">
        <h2 className="text-sm font-semibold text-neutral-700">Tools</h2>
        <UploadWidget botId={botId} />
      </aside>
      <main className="flex flex-1 flex-col">
        <header className="flex h-14 items-center border-b bg-white px-6">
          <h1 className="text-lg font-semibold">ChatForge</h1>
        </header>
        <ChatPanel />
      </main>
    </div>
  );
}
```

- [ ] **Step 3: Verify build**

Run: `npm run build`
Expected: build succeeds.

- [ ] **Step 4: Commit**

```bash
git add web-ui/src/components/upload/ web-ui/src/App.tsx
git commit -m "feat(web-ui): upload widget with drag-and-drop"
```

---

## Task 13: Web UI — Dockerfile

**Files:**
- Create: `web-ui/Dockerfile`
- Create: `web-ui/nginx.conf`

- [ ] **Step 1: Create `web-ui/nginx.conf`**

```nginx
server {
    listen 3000;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://ai-backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
    }
}
```

- [ ] **Step 2: Create `web-ui/Dockerfile`**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **Step 3: Commit**

```bash
git add web-ui/Dockerfile web-ui/nginx.conf
git commit -m "feat(web-ui): add Dockerfile and nginx config"
```

---

## Task 14: Docker Compose — Full Phase 1 Stack

**Files:**
- Create: `infra/docker-compose.yml`
- Create: `infra/.env.example`
- Create: `README.md`

- [ ] **Step 1: Create `infra/docker-compose.yml`**

```yaml
version: "3.8"

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

  ai-backend:
    build: ../ai-backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - ollama
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434

  web-ui:
    build: ../web-ui
    ports:
      - "3000:3000"
    depends_on:
      - ai-backend

volumes:
  ollama_data:
```

- [ ] **Step 2: Create `infra/.env.example`**

```env
LLM_RUNTIME=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=mistral
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX=chatforge
PINECONE_NAMESPACE=default
EMBEDDING_MODEL=all-MiniLM-L6-v2
MLFLOW_TRACKING_URI=http://host.docker.internal:5000
WANDB_API_KEY=your-wandb-api-key
WANDB_PROJECT=chatforge
```

- [ ] **Step 3: Create `README.md` at repo root**

```markdown
# ChatForge

A self-hostable, private, configurable domain chatbot platform.

## Quick Start (Phase 1)

### Prerequisites
- Docker and Docker Compose
- A Pinecone API key (free tier works)
- (Optional) W&B API key for fine-tune tracking
- (Optional) MLflow running on port 5000

### Setup

1. Copy the env file and add your keys:
   ```bash
   cp infra/.env.example infra/.env
   # Edit infra/.env with your PINECONE_API_KEY
   ```

2. Pull the Ollama model:
   ```bash
   docker compose -f infra/docker-compose.yml up ollama -d
   docker exec -it $(docker ps -qf "ancestor=ollama/ollama") ollama pull mistral
   ```

3. Start all services:
   ```bash
   docker compose -f infra/docker-compose.yml up --build
   ```

4. Open http://localhost:3000

### Usage

1. Upload a document via the sidebar upload widget
2. Wait for ingestion to complete
3. Ask questions about your document in the chat

### API Endpoints

| Method | Path           | Description                    |
|--------|----------------|--------------------------------|
| POST   | /ingest        | Upload and ingest a document   |
| POST   | /chat          | RAG chat (JSON response)       |
| POST   | /chat/stream   | RAG chat (SSE streaming)       |
| POST   | /finetune      | Launch a LoRA fine-tune job    |
| POST   | /evaluate      | Run eval suite on a test set   |
| GET    | /models        | List available models          |
| GET    | /health        | Health check                   |

### Architecture

See `docs/superpowers/specs/2026-04-16-chatforge-design.md` for full design.

## Tech Stack

- **AI Backend:** Python, FastAPI, LangChain, Pinecone, HuggingFace, PEFT, MLflow, W&B
- **Web UI:** React, Vite, Tailwind CSS, shadcn/ui
- **Runtime:** Ollama (dev), vLLM (prod)
- **Infra:** Docker Compose
```

- [ ] **Step 4: Build and verify the full stack**

Run (from repo root):
```bash
docker compose -f infra/docker-compose.yml build
```
Expected: all 3 images build successfully.

- [ ] **Step 5: Commit**

```bash
git add infra/ README.md
git commit -m "feat: Docker Compose stack and README for Phase 1"
```

---

## Spec Coverage Check

| Spec Requirement | Covered By |
|---|---|
| FastAPI backend | Task 1 |
| LLMProvider (Ollama + vLLM) | Task 2 |
| POST /ingest (PDF, DOCX, TXT, JSON) | Task 3 |
| POST /chat with RAG + SSE streaming | Task 4 |
| POST /finetune with LoRA + W&B + MLflow | Task 5 |
| POST /evaluate with metrics + MLflow | Task 6 |
| GET /models from Ollama + MLflow | Task 7 |
| Consistent error schema + request IDs | Task 1 |
| React + Vite + shadcn/ui chat UI | Tasks 9, 11 |
| SSE streaming in UI | Task 10 (useChat hook) |
| Upload widget | Task 12 |
| Bot selector | Task 11 |
| Docker Compose (3 services) | Task 14 |
| .env.example, no hardcoded secrets | Tasks 1, 14 |
| Pinecone namespace per bot | Tasks 3, 4 |
| pytest test suite | Tasks 1-7 |
| Vitest test for hooks | Task 10 |
