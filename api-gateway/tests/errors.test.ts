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
