export interface Env {
  port: number;
  corsOrigin: string;
}

export function getEnv(): Env {
  return {
    port: Number(process.env.PORT ?? 8080),
    corsOrigin: process.env.CORS_ORIGIN ?? "http://localhost:3000"
  };
}
