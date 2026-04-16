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
