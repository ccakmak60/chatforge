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
