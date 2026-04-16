# API Gateway Design Spec (Phase 2 Scaffold)

**Date:** 2026-04-16  
**Project:** ChatForge  
**Component:** `api-gateway` (Node.js/Express)

## 1) Goal

Scaffold a production-shaped API gateway for ChatForge Phase 2 that:
- Exposes a public `GET /health`
- Protects all non-health routes with JWT auth
- Validates JWTs using `RS256` + remote `JWKS`
- Applies per-IP rate limiting
- Proxies REST and SSE traffic to `ai-backend`
- Returns consistent gateway error envelopes

This scaffold prioritizes clean boundaries and testability while keeping implementation minimal.

## 2) Scope

### In scope
- Express app scaffold with typed config
- Security middleware (`helmet`, `cors`, JWT verification)
- Rate limiting middleware (global per-IP, optional tighter chat path limit)
- Request ID propagation
- Proxy routes for AI backend endpoints
- SSE passthrough for `/chat/stream`
- Unit/integration tests for health, auth, rate limiting, proxy, and stream behavior

### Out of scope
- User management and RBAC policy matrix
- Laravel/admin route integration
- Gateway-side business orchestration
- Distributed rate limit stores (Redis)

## 3) Architecture

Proposed file layout:

```text
api-gateway/
├─ src/
│  ├─ server.ts
│  ├─ app.ts
│  ├─ config/
│  │  └─ env.ts
│  ├─ middleware/
│  │  ├─ auth.ts
│  │  ├─ rate-limit.ts
│  │  ├─ request-id.ts
│  │  └─ error-handler.ts
│  ├─ routes/
│  │  ├─ health.ts
│  │  └─ proxy.ts
│  ├─ lib/
│  │  └─ proxy-client.ts
│  └─ types/
│     └─ auth.ts
├─ tests/
│  ├─ health.test.ts
│  ├─ auth.test.ts
│  ├─ rate-limit.test.ts
│  ├─ proxy.test.ts
│  └─ stream.test.ts
├─ package.json
├─ tsconfig.json
├─ vite.config.ts
└─ .env.example
```

Responsibilities:
- `app.ts`: app composition for testability
- `server.ts`: runtime bootstrap only
- `config/env.ts`: parse and validate environment
- `middleware/*`: cross-cutting concerns
- `routes/proxy.ts`: route binding to forwarder helpers
- `lib/proxy-client.ts`: upstream forwarding logic

## 4) Route Contract

### Public route
- `GET /health`
  - No auth required
  - Returns status metadata

### Authenticated proxy routes
- `POST /ingest` -> `ai-backend /ingest`
- `POST /chat` -> `ai-backend /chat`
- `POST /chat/stream` -> `ai-backend /chat/stream` (SSE)
- `POST /finetune` -> `ai-backend /finetune`
- `POST /evaluate` -> `ai-backend /evaluate`
- `GET /models` -> `ai-backend /models`

Proxy behavior:
- Preserve request method/body/query where applicable
- Forward `authorization` and `x-request-id`
- Attach identity context headers from token claims when present:
  - `x-user-sub`
  - `x-user-email`
- Normalize non-success upstream responses into gateway schema

## 5) Auth and Security Design

Auth policy:
- All routes except `GET /health` require Bearer JWT
- Validate with `jose.jwtVerify` + `createRemoteJWKSet`
- Enforce:
  - algorithm: `RS256`
  - configured issuer
  - configured audience

Security baseline:
- `helmet` enabled
- CORS allowlist via `CORS_ORIGIN`
- Input size limits at JSON parser level

## 6) Rate Limiting Design

Strategy:
- Global per-IP limiter applied to authenticated API routes
- Optional stricter limiter for chat endpoints

Config:
- `RATE_LIMIT_WINDOW_MS`
- `RATE_LIMIT_MAX`
- `CHAT_RATE_LIMIT_MAX`

Failure behavior:
- Return `429` with standard error envelope

## 7) Error Handling Contract

All gateway errors return:

```json
{
  "code": "string",
  "error": "string",
  "detail": "string",
  "request_id": "string"
}
```

Gateway error codes:
- `unauthorized`
- `rate_limited`
- `upstream_timeout`
- `upstream_error`
- `internal_error`

Notes:
- Preserve `request_id` across middleware and proxy boundaries
- Avoid leaking sensitive upstream internals in `detail`

## 8) Environment Configuration

`.env.example` keys:
- `PORT=8080`
- `AI_BACKEND_BASE_URL=http://ai-backend:8000`
- `CORS_ORIGIN=http://localhost:3000`
- `JWKS_URI=`
- `JWT_ISSUER=`
- `JWT_AUDIENCE=`
- `RATE_LIMIT_WINDOW_MS=60000`
- `RATE_LIMIT_MAX=60`
- `CHAT_RATE_LIMIT_MAX=30`
- `UPSTREAM_TIMEOUT_MS=60000`

## 9) Testing Strategy

Tooling:
- `vitest` + `supertest`
- Upstream mocking via HTTP mock utilities (fast, no Docker dependency)

Tests:
- `health.test.ts`
  - `GET /health` returns 200 without token
- `auth.test.ts`
  - protected route without token returns 401
  - invalid token returns 401
  - valid token path succeeds (JWKS mocked)
- `rate-limit.test.ts`
  - repeated requests exceed threshold and return 429
- `proxy.test.ts`
  - forwards method/body/headers
  - upstream non-2xx mapped to gateway error schema
- `stream.test.ts`
  - SSE chunks from upstream are passed through

## 10) Milestone Acceptance (Scaffold)

Done when:
1. Gateway boots with typed env parsing.
2. `GET /health` works unauthenticated.
3. Non-health routes reject missing/invalid JWT.
4. Authenticated routes proxy to AI backend.
5. `/chat/stream` proxies as SSE.
6. Rate limits enforce with `429` responses.
7. Test suite passes locally without Docker.

## 11) Risks and Mitigations

- JWKS endpoint unavailability
  - Mitigation: clear startup/config errors, explicit auth failure response
- Local IP-based limiter weakness under proxies
  - Mitigation: trust-proxy config and future Redis-backed limiter
- SSE proxy edge cases across different clients
  - Mitigation: dedicated streaming test and minimal response mutation

---

This design is scoped for immediate implementation as a Phase 2 scaffold while preserving clean extension points for auth hardening, multi-service routing, and admin integrations.
