import request from "supertest";
import { describe, expect, it, vi } from "vitest";
import { buildApp } from "../src/app";

vi.mock("jose", () => ({
  createRemoteJWKSet: vi.fn(() => ({})),
  jwtVerify: vi.fn(async (token: string) => {
    if (token === "valid") {
      return { payload: { sub: "user-1", email: "u@example.com" } };
    }

    throw new Error("invalid");
  })
}));

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
