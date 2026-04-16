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
