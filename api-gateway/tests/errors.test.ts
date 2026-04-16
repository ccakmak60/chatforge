import request from "supertest";
import { describe, expect, it, vi } from "vitest";
import { buildApp } from "../src/app";

vi.mock("../src/middleware/auth", () => ({
  requireAuth: (_req: unknown, _res: unknown, next: () => void) => next()
}));

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
