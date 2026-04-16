# ChatForge Design Spec

**Date:** 2026-04-16  
**Project:** ChatForge  
**Type:** Portfolio demo (AI Engineer role-aligned)  

## 1) Goal

Build a self-hostable, private, configurable domain chatbot platform that demonstrates end-to-end AI engineering capability: model adaptation, RAG, deployment, monitoring, and operations.

The platform should show practical execution of:
- Private/local model hosting
- Custom-domain retrieval and adaptation
- Production-minded architecture (security, observability, automation)
- Multi-service integration across Python, Node, React, and PHP

## 2) Scope and Delivery Strategy

Given the breadth of requested capabilities, ChatForge is delivered in incremental phases (Option A: core-first).

### Phase 1 (MVP Demo): AI Core
- React chat UI with shadcn/ui components
- Python FastAPI backend for ingest/chat/evaluation/fine-tune jobs
- Ollama runtime for local model serving
- Pinecone vector store for RAG
- LangChain orchestration
- Hugging Face + PEFT for targeted fine-tuning
- MLflow + Weights & Biases instrumentation
- Docker Compose local stack

### Phase 2: Full Stack Layering
- Node.js/Express API gateway (auth, rate limits, routing, streaming passthrough)
- PHP/Laravel admin backend (bot/dataset/user management, audit logs)
- React admin surfaces (still shadcn/ui)
- MySQL persistence for admin domain

### Phase 3: Production & Automation
- n8n workflows for ingestion/fine-tune/evaluation orchestration
- Kubernetes deployment manifests
- vLLM production runtime swap (instead of Ollama)
- Drift/quality automation and alerting

## 3) High-Level Architecture

### Phase 1 architecture
```text
React Chat UI
   -> FastAPI AI Backend
      -> Ollama (dev inference)
      -> Pinecone (vector retrieval)
      -> LangChain (RAG flow)
      -> HF Transformers + PEFT (fine-tune)
      -> MLflow (registry/metrics)
      -> W&B (experiments)
```

### Phase 2 extension
```text
React UI
   -> Node API Gateway
      -> FastAPI AI Backend
      -> Laravel Admin Backend -> MySQL
```

### Phase 3 extension
```text
n8n triggers/schedules
   -> FastAPI jobs (/ingest, /finetune, /evaluate)
Kubernetes hosts all services
vLLM replaces Ollama in production via config
```

## 4) Repository Layout

```text
chatforge/
├─ ai-backend/         # Python FastAPI AI services
├─ web-ui/             # React + shadcn/ui app
├─ api-gateway/        # Node.js/Express gateway
├─ admin-backend/      # PHP/Laravel admin API
├─ automation/         # n8n workflows and config
├─ infra/              # Docker Compose + Kubernetes
└─ docs/               # Architecture and operating docs
```

## 5) Component Design

## 5.1 AI Backend (`ai-backend/`)

Responsibilities:
- Dataset ingestion and chunking
- Embedding generation and Pinecone indexing
- Retrieval-augmented chat
- Fine-tuning orchestration
- Model evaluation and metrics logging

Primary API endpoints:
- `POST /ingest` - ingest files (PDF, DOCX, TXT, JSON), chunk, embed, upsert
- `POST /chat` - RAG chat for `{session_id, bot_id, message}`
- `POST /finetune` - launch LoRA fine-tune job
- `POST /evaluate` - run quality/eval suite
- `GET /models` - list available runtime + registered fine-tuned models

Key internal abstractions:
- `LLMProvider` interface
  - `OllamaProvider` (development)
  - `VLLMProvider` (production)
- Provider selected by `LLM_RUNTIME=ollama|vllm`

This abstraction allows runtime swap without changing chat orchestration logic.

## 5.2 Web UI (`web-ui/`)

Responsibilities:
- End-user chatbot experience
- Domain/bot selection
- Ingest upload (Phase 1)
- Admin forms/tables (Phase 2)

UI stack:
- React + Vite
- Tailwind CSS
- shadcn/ui components (chat layout, forms, dialog, data table)

UX behavior:
- SSE-based streamed responses
- Clear source/context display for RAG responses (when enabled)
- Upload progress and ingestion status visibility

## 5.3 API Gateway (`api-gateway/`)

Responsibilities:
- Unified public API
- JWT auth and route protection
- Request rate limiting
- Reverse proxy/routing to Python and Laravel services
- SSE passthrough for chat streaming

Gateway is public-facing in Phase 2+, while AI backend remains internal-only.

## 5.4 Admin Backend (`admin-backend/`)

Responsibilities:
- Bot configuration CRUD
- Dataset metadata and ingestion status
- User/role management
- Audit/event logging

Domain entities (initial):
- `users`
- `bots`
- `datasets`
- `ingestion_jobs`
- `finetune_jobs`
- `audit_events`

## 5.5 Automation (`automation/`)

n8n workflows:
- Ingestion workflow (webhook-triggered)
- Scheduled evaluation (nightly)
- Fine-tune workflow (manual/admin-triggered)
- Drift checks (weekly)

All workflows include explicit success/failure branches and status callbacks.

## 6) Data Flow Design

### 6.1 Ingestion flow
```text
User upload
-> Gateway auth/validation
-> Laravel records dataset (pending)
-> n8n triggers FastAPI /ingest
-> chunk + embed + Pinecone upsert
-> Laravel marks complete/failed
```

### 6.2 Chat flow
```text
User message
-> Gateway (auth + rate limit)
-> FastAPI /chat
-> Pinecone retrieval (top-k)
-> prompt assembly + runtime inference
-> streamed response back to UI
```

### 6.3 Fine-tune flow
```text
Admin triggers fine-tune
-> Laravel job record
-> n8n triggers FastAPI /finetune
-> HF/PEFT training run
-> W&B logs + MLflow registration
-> Laravel status update
```

## 7) Deployment Design

### 7.1 Local/portfolio deployment (Compose)

Phase 1 minimum:
- `ai-backend`
- `ollama`
- `web-ui`

Phase 2 extended:
- `api-gateway`
- `admin-backend`
- `mysql`

Phase 3 adds:
- `n8n`
- `mlflow`
- production-like compose profile using `vllm`

### 7.2 Kubernetes production target

- One deployment per service
- Ingress path routing (`/`, `/api`, `/admin`, `/n8n`)
- Secrets externalized to Kubernetes Secrets
- ConfigMaps for non-secret config
- HPA for `api-gateway` and `ai-backend`
- Persistent volumes for MySQL and MLflow artifacts

## 8) Observability and Evaluation

### Experiment and model tracking
- W&B: run-level training/eval visualization
- MLflow: model registry, run metadata, deployment candidate tracking

### Model quality tracking
- RAG eval metrics (faithfulness, relevance, correctness)
- Baseline-vs-current comparison for drift detection
- Nightly evaluation jobs with alert thresholds

### Operational metrics
- API latency (p50/p95)
- token usage and cost estimation
- ingestion throughput and failure rate
- chat error rates by provider/runtime

## 9) Error Handling and Reliability

- Consistent API error schema: `{ code, error, detail, request_id }`
- Upstream timeout and retry strategy for model providers
- Circuit-breaker behavior at gateway for backend instability
- n8n error branches always update job state and emit alerts
- Idempotent ingestion job handling by dataset/version key

## 10) Security and Responsible AI

Security baseline:
- No hardcoded secrets; `.env.example` only
- Private/local inference in development
- Runtime provider isolation via internal network
- Per-bot dataset namespace separation in Pinecone
- RBAC for admin endpoints

Responsible AI baseline:
- Bias and harmful-output checks in evaluation suite
- Prompt and policy controls per bot profile
- Audit trail for model updates and fine-tune actions
- Explicit handling for data deletion requests in managed datasets

## 11) Testing Strategy

Unit/integration:
- `ai-backend`: pytest for chunking, retrieval, prompt assembly, provider adapters
- `api-gateway`: Jest + supertest for auth/rate-limit/proxy behavior
- `admin-backend`: PHPUnit feature tests for CRUD/auth/workflow state updates
- `web-ui`: Vitest + React Testing Library for chat, forms, and state handling

End-to-end:
- Playwright scenario for ingest -> retrieve -> chat response
- Smoke checks for fine-tune and model registration path

Acceptance criteria (portfolio milestone):
1. Document ingestion to Pinecone works and is visible in admin status.
2. Chat returns context-grounded responses from ingested data.
3. Fine-tune job can be triggered and tracked in W&B + MLflow.
4. API gateway enforces auth and rate limiting.
5. n8n automation runs at least one scheduled evaluation workflow.
6. Stack runs locally through Docker Compose with clear setup docs.

## 12) Risks and Mitigations

- **Scope risk:** multi-stack complexity can delay a polished demo.
  - Mitigation: strict phased delivery and demo checkpoints per phase.
- **Provider variability:** Ollama/vLLM output and latency may differ.
  - Mitigation: standardized prompt templates + provider adapter tests.
- **Evaluation ambiguity:** quality metrics can be noisy.
  - Mitigation: fixed benchmark set and thresholded comparisons.
- **Ops overhead:** Kubernetes may be heavy for portfolio timeline.
  - Mitigation: maintain prod-like compose profile as fallback demo.

## 13) Out of Scope (Initial Cycle)

- Multi-tenant billing/subscription logic
- Custom model pretraining from scratch
- Complex human-in-the-loop labeling platform
- Enterprise SSO integrations

## 14) Definition of Done (Design Phase)

This design is complete when:
- Architecture and phased delivery are approved
- Component responsibilities and interfaces are explicit
- Data flows, error handling, testing, and security controls are defined
- Scope is constrained for implementation planning

---

Prepared for implementation planning as the next step.
