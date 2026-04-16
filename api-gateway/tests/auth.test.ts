import request from "supertest";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { buildApp } from "../src/app";

const fetchMock = vi.fn();
vi.stubGlobal("fetch", fetchMock);

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
  beforeEach(() => {
    fetchMock.mockReset();
  });

  it("returns 401 when token missing", async () => {
    const app = buildApp();
    const res = await request(app).get("/models");

    expect(res.status).toBe(401);
    expect(res.body.code).toBe("unauthorized");
  });

  it("allows request with valid bearer token", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ models: [] }), { status: 200 })
    );

    const app = buildApp();
    const res = await request(app)
      .get("/models")
      .set("authorization", "Bearer valid");

    expect([200, 502]).toContain(res.status);
  });
});
