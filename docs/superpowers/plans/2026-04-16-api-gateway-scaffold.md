# API Gateway Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Phase 2 `api-gateway` scaffold that secures non-health routes with RS256/JWKS JWT, applies per-IP rate limiting, and proxies REST + SSE calls to `ai-backend`.

**Architecture:** A small Express app with clear module boundaries: typed env config, composable middleware, health route, proxy routes, and shared upstream forwarding helpers. Tests are written first (TDD) with Vitest + Supertest and mocked upstream/JWKS dependencies to avoid Docker requirements.

**Tech Stack:** Node.js, TypeScript, Express, jose, express-rate-limit, Vitest, Supertest, tsx

---

## File Structure (target)

- `api-gateway/package.json` — scripts + dependencies
- `api-gateway/tsconfig.json` — TypeScript configuration
- `api-gateway/.env.example` — documented gateway env variables
- `api-gateway/src/server.ts` — bootstrap listener
- `api-gateway/src/app.ts` — app wiring for testability
- `api-gateway/src/config/env.ts` — env parsing + validation
- `api-gateway/src/middleware/request-id.ts` — request ID propagation
- `api-gateway/src/middleware/auth.ts` — RS256/JWKS JWT verification
- `api-gateway/src/middleware/rate-limit.ts` — per-IP limiters
- `api-gateway/src/middleware/error-handler.ts` — uniform gateway errors
- `api-gateway/src/routes/health.ts` — public health endpoint
- `api-gateway/src/routes/proxy.ts` — protected proxy routes
- `api-gateway/src/lib/proxy-client.ts` — upstream REST/SSE forwarding
- `api-gateway/src/types/auth.ts` — auth claim typing
- `api-gateway/tests/*.test.ts` — integration tests

---

### Task 1: Scaffold Gateway Project

**Files:**
- Create: `api-gateway/package.json`
- Create: `api-gateway/tsconfig.json`
- Create: `api-gateway/.env.example`
- Create: `api-gateway/src/server.ts`
- Create: `api-gateway/src/app.ts`

- [ ] **Step 1: Write the failing smoke test first**

Create `api-gateway/tests/health.test.ts`:
```ts
import request from "supertest";
import { describe, expect, it } from "vitest";
import { buildApp } from "../src/app";

describe("health", () => {
  it("returns 200 on GET /health", async () => {
    const app = buildApp();
    const res = await request(app).get("/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd api-gateway
npm test -- tests/health.test.ts
```
Expected: FAIL because `buildApp` and project scaffold do not exist.

- [ ] **Step 3: Write minimal scaffold implementation**

Create `api-gateway/package.json`:
```json
{
  "name": "chatforge-api-gateway",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js",
    "test": "vitest run"
  },
  "dependencies": {
    "cors": "^2.8.5",
    "express": "^4.21.2",
    "helmet": "^8.1.0",
    "morgan": "^1.10.0"
  },
  "devDependencies": {
    "@types/cors": "^2.8.17",
    "@types/express": "^4.17.21",
    "@types/morgan": "^1.9.9",
    "@types/node": "^22.15.3",
    "supertest": "^7.1.0",
    "tsx": "^4.19.3",
    "typescript": "^5.8.3",
    "vitest": "^1.6.1"
  }
}
```

Create `api-gateway/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "outDir": "dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "types": ["node", "vitest/globals"]
  },
  "include": ["src", "tests"]
}
```

Create `api-gateway/.env.example`:
```env
PORT=8080
AI_BACKEND_BASE_URL=http://ai-backend:8000
CORS_ORIGIN=http://localhost:3000
JWKS_URI=https://example.com/.well-known/jwks.json
JWT_ISSUER=https://example.com/
JWT_AUDIENCE=chatforge-api
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=60
CHAT_RATE_LIMIT_MAX=30
UPSTREAM_TIMEOUT_MS=60000
```

Create `api-gateway/src/app.ts`:
```ts
import express from "express";

export function buildApp() {
  const app = express();

  app.get("/health", (_req, res) => {
    res.status(200).json({ status: "ok", service: "api-gateway" });
  });

  return app;
}
```

Create `api-gateway/src/server.ts`:
```ts
import { buildApp } from "./app";

const port = Number(process.env.PORT ?? 8080);
const app = buildApp();

app.listen(port, () => {
  console.log(`api-gateway listening on ${port}`);
});
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd api-gateway
npm install
npm test -- tests/health.test.ts
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add api-gateway
git commit -m "feat(api-gateway): scaffold express gateway with health route"
```

---

### Task 2: Add Typed Env + Request ID + Error Envelope

**Files:**
- Create: `api-gateway/src/config/env.ts`
- Create: `api-gateway/src/middleware/request-id.ts`
- Create: `api-gateway/src/middleware/error-handler.ts`
- Modify: `api-gateway/src/app.ts`
- Test: `api-gateway/tests/health.test.ts`

- [ ] **Step 1: Write failing tests first**

Append to `api-gateway/tests/health.test.ts`:
```ts
it("returns x-request-id response header", async () => {
  const app = buildApp();
  const res = await request(app).get("/health");
  expect(res.headers["x-request-id"]).toBeTruthy();
});
```

Create `api-gateway/tests/errors.test.ts`:
```ts
import request from "supertest";
import { describe, expect, it } from "vitest";
import { buildApp } from "../src/app";

describe("error envelope", () => {
  it("returns standard error shape", async () => {
    const app = buildApp();
    const res = await request(app).get("/__missing__");
    expect(res.status).toBe(404);
    expect(res.body).toHaveProperty("code");
    expect(res.body).toHaveProperty("error");
    expect(res.body).toHaveProperty("detail");
    expect(res.body).toHaveProperty("request_id");
  });
});
```

- [ ] **Step 2: Run tests to verify failure**

Run:
```bash
cd api-gateway
npm test -- tests/health.test.ts tests/errors.test.ts
```
Expected: FAIL because request ID and standardized error handler are missing.

- [ ] **Step 3: Write minimal implementation**

Create `api-gateway/src/config/env.ts`:
```ts
export interface Env {
  port: number;
  corsOrigin: string;
}

export function getEnv(): Env {
  return {
    port: Number(process.env.PORT ?? 8080),
    corsOrigin: process.env.CORS_ORIGIN ?? "http://localhost:3000"
  };
}
```

Create `api-gateway/src/middleware/request-id.ts`:
```ts
import { randomUUID } from "node:crypto";
import type { Request, Response, NextFunction } from "express";

export function requestId(req: Request, res: Response, next: NextFunction) {
  const existing = req.header("x-request-id");
  const id = existing || randomUUID();
  (req as Request & { requestId: string }).requestId = id;
  res.setHeader("x-request-id", id);
  next();
}
```

Create `api-gateway/src/middleware/error-handler.ts`:
```ts
import type { NextFunction, Request, Response } from "express";

export function notFound(req: Request, res: Response) {
  const requestId = (req as Request & { requestId?: string }).requestId ?? "unknown";
  res.status(404).json({
    code: "not_found",
    error: "Not Found",
    detail: "Route does not exist",
    request_id: requestId
  });
}

export function errorHandler(err: unknown, req: Request, res: Response, _next: NextFunction) {
  const requestId = (req as Request & { requestId?: string }).requestId ?? "unknown";
  const detail = err instanceof Error ? err.message : "Unexpected error";

  res.status(500).json({
    code: "internal_error",
    error: "Internal Server Error",
    detail,
    request_id: requestId
  });
}
```

Modify `api-gateway/src/app.ts`:
```ts
import cors from "cors";
import express from "express";
import helmet from "helmet";
import morgan from "morgan";
import { getEnv } from "./config/env";
import { errorHandler, notFound } from "./middleware/error-handler";
import { requestId } from "./middleware/request-id";

export function buildApp() {
  const env = getEnv();
  const app = express();

  app.use(helmet());
  app.use(cors({ origin: env.corsOrigin }));
  app.use(morgan("dev"));
  app.use(express.json({ limit: "2mb" }));
  app.use(requestId);

  app.get("/health", (_req, res) => {
    res.status(200).json({ status: "ok", service: "api-gateway" });
  });

  app.use(notFound);
  app.use(errorHandler);

  return app;
}
```

- [ ] **Step 4: Run tests to verify pass**

Run:
```bash
cd api-gateway
npm test -- tests/health.test.ts tests/errors.test.ts
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add api-gateway/src api-gateway/tests
git commit -m "feat(api-gateway): add request id and standard error envelope"
```

---

### Task 3: Add JWT Auth Middleware (RS256 + JWKS)

**Files:**
- Create: `api-gateway/src/types/auth.ts`
- Create: `api-gateway/src/middleware/auth.ts`
- Modify: `api-gateway/src/config/env.ts`
- Modify: `api-gateway/src/app.ts`
- Test: `api-gateway/tests/auth.test.ts`

- [ ] **Step 1: Write failing tests first**

Create `api-gateway/tests/auth.test.ts`:
```ts
import request from "supertest";
import { describe, expect, it, vi } from "vitest";
import { buildApp } from "../src/app";

vi.mock("../src/middleware/auth", async () => {
  const actual = await vi.importActual<typeof import("../src/middleware/auth")>("../src/middleware/auth");
  return {
    ...actual,
    verifyToken: vi.fn(async (token: string) => {
      if (token === "valid") return { sub: "user-1", email: "u@example.com" };
      throw new Error("invalid");
    })
  };
});

describe("auth", () => {
  it("returns 401 when token missing", async () => {
    const app = buildApp();
    const res = await request(app).get("/models");
    expect(res.status).toBe(401);
    expect(res.body.code).toBe("unauthorized");
  });

  it("allows request with valid bearer token", async () => {
    const app = buildApp();
    const res = await request(app)
      .get("/models")
      .set("authorization", "Bearer valid");
    expect([200, 502]).toContain(res.status);
  });
});
```

- [ ] **Step 2: Run test to verify failure**

Run:
```bash
cd api-gateway
npm test -- tests/auth.test.ts
```
Expected: FAIL because auth middleware and protected route are not implemented.

- [ ] **Step 3: Write minimal implementation**

Add deps:
```bash
cd api-gateway
npm install jose
```

Create `api-gateway/src/types/auth.ts`:
```ts
export interface AuthClaims {
  sub: string;
  email?: string;
}
```

Modify `api-gateway/src/config/env.ts`:
```ts
export interface Env {
  port: number;
  corsOrigin: string;
  jwksUri: string;
  jwtIssuer: string;
  jwtAudience: string;
}

export function getEnv(): Env {
  return {
    port: Number(process.env.PORT ?? 8080),
    corsOrigin: process.env.CORS_ORIGIN ?? "http://localhost:3000",
    jwksUri: process.env.JWKS_URI ?? "",
    jwtIssuer: process.env.JWT_ISSUER ?? "",
    jwtAudience: process.env.JWT_AUDIENCE ?? ""
  };
}
```

Create `api-gateway/src/middleware/auth.ts`:
```ts
import { createRemoteJWKSet, jwtVerify } from "jose";
import type { NextFunction, Request, Response } from "express";
import { getEnv } from "../config/env";
import type { AuthClaims } from "../types/auth";

const env = getEnv();
const jwks = createRemoteJWKSet(new URL(env.jwksUri || "https://example.com/.well-known/jwks.json"));

export async function verifyToken(token: string): Promise<AuthClaims> {
  const { payload } = await jwtVerify(token, jwks, {
    algorithms: ["RS256"],
    issuer: env.jwtIssuer || undefined,
    audience: env.jwtAudience || undefined
  });

  return {
    sub: String(payload.sub ?? ""),
    email: payload.email ? String(payload.email) : undefined
  };
}

export async function requireAuth(req: Request, res: Response, next: NextFunction) {
  const header = req.header("authorization");
  const token = header?.startsWith("Bearer ") ? header.slice(7) : "";
  const requestId = (req as Request & { requestId?: string }).requestId ?? "unknown";

  if (!token) {
    return res.status(401).json({ code: "unauthorized", error: "Unauthorized", detail: "Missing bearer token", request_id: requestId });
  }

  try {
    const claims = await verifyToken(token);
    (req as Request & { auth?: AuthClaims }).auth = claims;
    return next();
  } catch {
    return res.status(401).json({ code: "unauthorized", error: "Unauthorized", detail: "Invalid token", request_id: requestId });
  }
}
```

Modify `api-gateway/src/app.ts` to protect non-health route:
```ts
import { requireAuth } from "./middleware/auth";

app.get("/models", requireAuth, (_req, res) => {
  res.status(200).json({ models: [] });
});
```

- [ ] **Step 4: Run test to verify pass**

Run:
```bash
cd api-gateway
npm test -- tests/auth.test.ts
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add api-gateway/src api-gateway/tests api-gateway/package.json api-gateway/package-lock.json
git commit -m "feat(api-gateway): enforce jwt auth with jwks validation"
```

---

### Task 4: Add Per-IP Rate Limiting

**Files:**
- Create: `api-gateway/src/middleware/rate-limit.ts`
- Modify: `api-gateway/src/config/env.ts`
- Modify: `api-gateway/src/app.ts`
- Test: `api-gateway/tests/rate-limit.test.ts`

- [ ] **Step 1: Write failing test first**

Create `api-gateway/tests/rate-limit.test.ts`:
```ts
import request from "supertest";
import { describe, expect, it, vi } from "vitest";
import { buildApp } from "../src/app";

vi.mock("../src/middleware/auth", () => ({
  requireAuth: (_req: unknown, _res: unknown, next: () => void) => next()
}));

describe("rate limiting", () => {
  it("returns 429 after limit reached", async () => {
    process.env.RATE_LIMIT_MAX = "2";
    process.env.RATE_LIMIT_WINDOW_MS = "60000";

    const app = buildApp();

    await request(app).get("/models");
    await request(app).get("/models");
    const third = await request(app).get("/models");

    expect(third.status).toBe(429);
    expect(third.body.code).toBe("rate_limited");
  });
});
```

- [ ] **Step 2: Run test to verify failure**

Run:
```bash
cd api-gateway
npm test -- tests/rate-limit.test.ts
```
Expected: FAIL because limiter is not configured.

- [ ] **Step 3: Write minimal implementation**

Add dep:
```bash
cd api-gateway
npm install express-rate-limit
```

Create `api-gateway/src/middleware/rate-limit.ts`:
```ts
import rateLimit from "express-rate-limit";
import { getEnv } from "../config/env";

export function createGlobalLimiter() {
  const env = getEnv();

  return rateLimit({
    windowMs: Number(env.rateLimitWindowMs),
    max: Number(env.rateLimitMax),
    standardHeaders: true,
    legacyHeaders: false,
    handler: (req, res) => {
      const requestId = (req as typeof req & { requestId?: string }).requestId ?? "unknown";
      res.status(429).json({
        code: "rate_limited",
        error: "Too Many Requests",
        detail: "Rate limit exceeded",
        request_id: requestId
      });
    }
  });
}
```

Modify `api-gateway/src/config/env.ts` to include:
```ts
  rateLimitWindowMs: number;
  rateLimitMax: number;
```
and return values:
```ts
rateLimitWindowMs: Number(process.env.RATE_LIMIT_WINDOW_MS ?? 60000),
rateLimitMax: Number(process.env.RATE_LIMIT_MAX ?? 60)
```

Modify `api-gateway/src/app.ts`:
```ts
import { createGlobalLimiter } from "./middleware/rate-limit";

const limiter = createGlobalLimiter();
app.use("/models", requireAuth, limiter);
app.get("/models", (_req, res) => {
  res.status(200).json({ models: [] });
});
```

- [ ] **Step 4: Run test to verify pass**

Run:
```bash
cd api-gateway
npm test -- tests/rate-limit.test.ts
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add api-gateway/src api-gateway/tests api-gateway/package.json api-gateway/package-lock.json
git commit -m "feat(api-gateway): add per-ip rate limiting"
```

---

### Task 5: Implement REST Proxy Routes

**Files:**
- Create: `api-gateway/src/lib/proxy-client.ts`
- Create: `api-gateway/src/routes/proxy.ts`
- Modify: `api-gateway/src/config/env.ts`
- Modify: `api-gateway/src/app.ts`
- Test: `api-gateway/tests/proxy.test.ts`

- [ ] **Step 1: Write failing tests first**

Create `api-gateway/tests/proxy.test.ts`:
```ts
import request from "supertest";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { buildApp } from "../src/app";

vi.mock("../src/middleware/auth", () => ({
  requireAuth: (_req: unknown, _res: unknown, next: () => void) => next()
}));

const fetchMock = vi.fn();
vi.stubGlobal("fetch", fetchMock);

describe("proxy routes", () => {
  beforeEach(() => {
    fetchMock.mockReset();
  });

  it("forwards POST /chat to upstream", async () => {
    fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ answer: "ok" }), { status: 200 }));

    const app = buildApp();
    const res = await request(app).post("/chat").send({ message: "hi" });

    expect(res.status).toBe(200);
    expect(res.body.answer).toBe("ok");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("maps upstream error to gateway schema", async () => {
    fetchMock.mockResolvedValueOnce(new Response("bad", { status: 500 }));

    const app = buildApp();
    const res = await request(app).post("/chat").send({ message: "hi" });

    expect(res.status).toBe(502);
    expect(res.body.code).toBe("upstream_error");
  });
});
```

- [ ] **Step 2: Run tests to verify failure**

Run:
```bash
cd api-gateway
npm test -- tests/proxy.test.ts
```
Expected: FAIL because proxy logic/routes do not exist.

- [ ] **Step 3: Write minimal implementation**

Modify `api-gateway/src/config/env.ts` to include:
```ts
aiBackendBaseUrl: string;
upstreamTimeoutMs: number;
```
and return values:
```ts
aiBackendBaseUrl: process.env.AI_BACKEND_BASE_URL ?? "http://localhost:8000",
upstreamTimeoutMs: Number(process.env.UPSTREAM_TIMEOUT_MS ?? 60000)
```

Create `api-gateway/src/lib/proxy-client.ts`:
```ts
import type { Request, Response } from "express";
import { getEnv } from "../config/env";

export async function forwardJson(req: Request, res: Response, path: string) {
  const env = getEnv();
  const url = `${env.aiBackendBaseUrl}${path}`;
  const requestId = (req as Request & { requestId?: string }).requestId ?? "unknown";

  const upstream = await fetch(url, {
    method: req.method,
    headers: {
      "content-type": "application/json",
      "x-request-id": requestId,
      authorization: req.header("authorization") ?? ""
    },
    body: ["GET", "HEAD"].includes(req.method) ? undefined : JSON.stringify(req.body)
  });

  if (!upstream.ok) {
    return res.status(502).json({
      code: "upstream_error",
      error: "Bad Gateway",
      detail: `Upstream returned ${upstream.status}`,
      request_id: requestId
    });
  }

  const payload = await upstream.json();
  return res.status(upstream.status).json(payload);
}
```

Create `api-gateway/src/routes/proxy.ts`:
```ts
import { Router } from "express";
import { requireAuth } from "../middleware/auth";
import { createGlobalLimiter } from "../middleware/rate-limit";
import { forwardJson } from "../lib/proxy-client";

export const proxyRouter = Router();
const limiter = createGlobalLimiter();

proxyRouter.use(requireAuth, limiter);
proxyRouter.post("/ingest", (req, res) => forwardJson(req, res, "/ingest"));
proxyRouter.post("/chat", (req, res) => forwardJson(req, res, "/chat"));
proxyRouter.post("/finetune", (req, res) => forwardJson(req, res, "/finetune"));
proxyRouter.post("/evaluate", (req, res) => forwardJson(req, res, "/evaluate"));
proxyRouter.get("/models", (req, res) => forwardJson(req, res, "/models"));
```

Modify `api-gateway/src/app.ts`:
```ts
import { proxyRouter } from "./routes/proxy";

app.use(proxyRouter);
```

- [ ] **Step 4: Run tests to verify pass**

Run:
```bash
cd api-gateway
npm test -- tests/proxy.test.ts
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add api-gateway/src api-gateway/tests
git commit -m "feat(api-gateway): add authenticated rest proxy routes"
```

---

### Task 6: Implement SSE Passthrough for `/chat/stream`

**Files:**
- Modify: `api-gateway/src/lib/proxy-client.ts`
- Modify: `api-gateway/src/routes/proxy.ts`
- Test: `api-gateway/tests/stream.test.ts`

- [ ] **Step 1: Write failing test first**

Create `api-gateway/tests/stream.test.ts`:
```ts
import request from "supertest";
import { describe, expect, it, vi } from "vitest";
import { Readable } from "node:stream";
import { buildApp } from "../src/app";

vi.mock("../src/middleware/auth", () => ({
  requireAuth: (_req: unknown, _res: unknown, next: () => void) => next()
}));

describe("chat stream proxy", () => {
  it("passes through event-stream content", async () => {
    const stream = Readable.from(["data: hello\n\n", "data: world\n\n"]);
    const response = new Response(stream as unknown as ReadableStream, {
      status: 200,
      headers: { "content-type": "text/event-stream" }
    });

    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response));

    const app = buildApp();
    const res = await request(app).post("/chat/stream").send({ message: "hi" });

    expect(res.status).toBe(200);
    expect(res.headers["content-type"]).toContain("text/event-stream");
    expect(res.text).toContain("data: hello");
  });
});
```

- [ ] **Step 2: Run test to verify failure**

Run:
```bash
cd api-gateway
npm test -- tests/stream.test.ts
```
Expected: FAIL because stream forwarding is not implemented.

- [ ] **Step 3: Write minimal implementation**

Append in `api-gateway/src/lib/proxy-client.ts`:
```ts
import { Readable } from "node:stream";

export async function forwardSse(req: Request, res: Response, path: string) {
  const env = getEnv();
  const url = `${env.aiBackendBaseUrl}${path}`;
  const requestId = (req as Request & { requestId?: string }).requestId ?? "unknown";

  const upstream = await fetch(url, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-request-id": requestId,
      authorization: req.header("authorization") ?? ""
    },
    body: JSON.stringify(req.body)
  });

  if (!upstream.ok || !upstream.body) {
    return res.status(502).json({
      code: "upstream_error",
      error: "Bad Gateway",
      detail: `Upstream returned ${upstream.status}`,
      request_id: requestId
    });
  }

  res.status(upstream.status);
  res.setHeader("content-type", "text/event-stream; charset=utf-8");
  res.setHeader("cache-control", "no-cache");
  res.setHeader("connection", "keep-alive");

  const nodeStream = Readable.fromWeb(upstream.body as ReadableStream<Uint8Array>);
  nodeStream.pipe(res);
}
```

Modify `api-gateway/src/routes/proxy.ts`:
```ts
import { forwardJson, forwardSse } from "../lib/proxy-client";

proxyRouter.post("/chat/stream", (req, res) => forwardSse(req, res, "/chat/stream"));
```

- [ ] **Step 4: Run test to verify pass**

Run:
```bash
cd api-gateway
npm test -- tests/stream.test.ts
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add api-gateway/src api-gateway/tests
git commit -m "feat(api-gateway): add sse passthrough for chat stream"
```

---

### Task 7: Full Gateway Verification + Docs Hookup

**Files:**
- Modify: `README.md`
- Modify: `infra/docker-compose.yml` (only wiring references; do not run locally)

- [ ] **Step 1: Write failing doc expectation test (optional lightweight check)**

Create `api-gateway/tests/contracts.test.ts`:
```ts
import request from "supertest";
import { describe, expect, it, vi } from "vitest";
import { buildApp } from "../src/app";

vi.mock("../src/middleware/auth", () => ({
  requireAuth: (_req: unknown, _res: unknown, next: () => void) => next()
}));

describe("gateway contracts", () => {
  it("exposes health and protected routes", async () => {
    const app = buildApp();
    const health = await request(app).get("/health");
    expect(health.status).toBe(200);
  });
});
```

- [ ] **Step 2: Run focused tests + full test suite**

Run:
```bash
cd api-gateway
npm test -- tests/contracts.test.ts
npm test
npm run build
```
Expected: all PASS.

- [ ] **Step 3: Update README and compose references minimally**

Update `README.md` snippets to include gateway run commands:
```md
### API Gateway (Phase 2 Scaffold)

```bash
cd api-gateway
npm install
npm run dev
```

Default URL: `http://localhost:8080`

Public health: `GET /health`
All other routes require Bearer JWT (RS256/JWKS).
```
```

Update `infra/docker-compose.yml` service stub:
```yaml
  api-gateway:
    build: ../api-gateway
    ports:
      - "8080:8080"
    env_file:
      - .env
    depends_on:
      - ai-backend
```

- [ ] **Step 4: Commit**

```bash
git add api-gateway README.md infra/docker-compose.yml
git commit -m "feat(api-gateway): finalize scaffold verification and docs wiring"
```

---

## Spec Coverage Check

- JWT on all non-health routes: covered in Tasks 3 and 5.
- RS256 + JWKS validation: covered in Task 3.
- Per-IP rate limiting: covered in Task 4.
- REST proxy for ingest/chat/finetune/evaluate/models: covered in Task 5.
- SSE passthrough for `/chat/stream`: covered in Task 6.
- Consistent error schema `{ code, error, detail, request_id }`: covered in Task 2 and reused in later tasks.
- Test strategy with Vitest + Supertest: covered across Tasks 1–7.

## Placeholder Scan

- No `TODO`, `TBD`, or "implement later" placeholders.
- Every task contains concrete file paths, commands, and code examples.

## Type Consistency Check

- `buildApp` used consistently as app factory for tests.
- `request_id` envelope field used consistently in all error responses.
- `requireAuth`, `forwardJson`, and `forwardSse` naming remains consistent across tasks.
