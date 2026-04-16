import { Router } from "express";
import { forwardJson, forwardSse } from "../lib/proxy-client";
import { requireAuth } from "../middleware/auth";
import { createGlobalLimiter } from "../middleware/rate-limit";

export function createProxyRouter() {
  const proxyRouter = Router();
  const limiter = createGlobalLimiter();

  proxyRouter.use(requireAuth, limiter);
  proxyRouter.post("/ingest", (req, res) => forwardJson(req, res, "/ingest"));
  proxyRouter.post("/chat", (req, res) => forwardJson(req, res, "/chat"));
  proxyRouter.post("/chat/stream", (req, res) =>
    forwardSse(req, res, "/chat/stream")
  );
  proxyRouter.post("/finetune", (req, res) =>
    forwardJson(req, res, "/finetune")
  );
  proxyRouter.post("/evaluate", (req, res) =>
    forwardJson(req, res, "/evaluate")
  );
  proxyRouter.get("/models", (req, res) => forwardJson(req, res, "/models"));

  return proxyRouter;
}
