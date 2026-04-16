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
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ answer: "ok" }), { status: 200 })
    );

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
