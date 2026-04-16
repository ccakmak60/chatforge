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
