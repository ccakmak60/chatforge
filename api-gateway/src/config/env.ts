export interface Env {
  port: number;
  corsOrigin: string;
  jwksUri: string;
  jwtIssuer: string;
  jwtAudience: string;
  rateLimitWindowMs: number;
  rateLimitMax: number;
}

export function getEnv(): Env {
  return {
    port: Number(process.env.PORT ?? 8080),
    corsOrigin: process.env.CORS_ORIGIN ?? "http://localhost:3000",
    jwksUri: process.env.JWKS_URI ?? "",
    jwtIssuer: process.env.JWT_ISSUER ?? "",
    jwtAudience: process.env.JWT_AUDIENCE ?? "",
    rateLimitWindowMs: Number(process.env.RATE_LIMIT_WINDOW_MS ?? 60000),
    rateLimitMax: Number(process.env.RATE_LIMIT_MAX ?? 60)
  };
}
