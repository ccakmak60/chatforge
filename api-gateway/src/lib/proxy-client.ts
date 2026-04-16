import type { Request, Response } from "express";
import { Readable } from "node:stream";
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

  const nodeStream = Readable.fromWeb(
    upstream.body as unknown as import("node:stream/web").ReadableStream
  );
  nodeStream.pipe(res);
}
