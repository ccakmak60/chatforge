import { createRemoteJWKSet, jwtVerify } from "jose";
import type { NextFunction, Request, Response } from "express";
import { getEnv } from "../config/env";
import type { AuthClaims } from "../types/auth";

const env = getEnv();
const jwks = createRemoteJWKSet(new URL(env.jwksUri || "https://example.com/.well-known/jwks.json"));

export async function verifyToken(token: string): Promise<AuthClaims> {
  const { payload } = await jwtVerify(token, jwks, {
    algorithms: ["RS256"],
    issuer: env.jwtIssuer || undefined,
    audience: env.jwtAudience || undefined
  });

  return {
    sub: String(payload.sub ?? ""),
    email: payload.email ? String(payload.email) : undefined
  };
}

export async function requireAuth(req: Request, res: Response, next: NextFunction) {
  const header = req.header("authorization");
  const token = header?.startsWith("Bearer ") ? header.slice(7) : "";
  const requestId = (req as Request & { requestId?: string }).requestId ?? "unknown";

  if (!token) {
    return res.status(401).json({
      code: "unauthorized",
      error: "Unauthorized",
      detail: "Missing bearer token",
      request_id: requestId
    });
  }

  try {
    const claims = await verifyToken(token);
    (req as Request & { auth?: AuthClaims }).auth = claims;
    return next();
  } catch {
    return res.status(401).json({
      code: "unauthorized",
      error: "Unauthorized",
      detail: "Invalid token",
      request_id: requestId
    });
  }
}
