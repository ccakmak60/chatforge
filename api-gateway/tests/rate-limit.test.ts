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
