import type { NextFunction, Request, Response } from "express";

export function notFound(req: Request, res: Response) {
  const requestId = (req as Request & { requestId?: string }).requestId ?? "unknown";

  res.status(404).json({
    code: "not_found",
    error: "Not Found",
    detail: "Route does not exist",
    request_id: requestId
  });
}

export function errorHandler(err: unknown, req: Request, res: Response, _next: NextFunction) {
  const requestId = (req as Request & { requestId?: string }).requestId ?? "unknown";
  const detail = err instanceof Error ? err.message : "Unexpected error";

  res.status(500).json({
    code: "internal_error",
    error: "Internal Server Error",
    detail,
    request_id: requestId
  });
}
