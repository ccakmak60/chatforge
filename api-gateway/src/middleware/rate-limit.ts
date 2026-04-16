import rateLimit from "express-rate-limit";
import { getEnv } from "../config/env";

export function createGlobalLimiter() {
  const env = getEnv();

  return rateLimit({
    windowMs: Number(env.rateLimitWindowMs),
    max: Number(env.rateLimitMax),
    standardHeaders: true,
    legacyHeaders: false,
    handler: (req, res) => {
      const requestId = (req as typeof req & { requestId?: string }).requestId ?? "unknown";

      res.status(429).json({
        code: "rate_limited",
        error: "Too Many Requests",
        detail: "Rate limit exceeded",
        request_id: requestId
      });
    }
  });
}
