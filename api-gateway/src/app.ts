import cors from "cors";
import express from "express";
import helmet from "helmet";
import morgan from "morgan";
import { getEnv } from "./config/env";
import { errorHandler, notFound } from "./middleware/error-handler";
import { requestId } from "./middleware/request-id";
import { proxyRouter } from "./routes/proxy";

export function buildApp() {
  const env = getEnv();
  const app = express();

  app.use(helmet());
  app.use(cors({ origin: env.corsOrigin }));
  app.use(morgan("dev"));
  app.use(express.json({ limit: "2mb" }));
  app.use(requestId);

  app.get("/health", (_req, res) => {
    res.status(200).json({ status: "ok", service: "api-gateway" });
  });

  app.use(proxyRouter);

  app.use(notFound);
  app.use(errorHandler);

  return app;
}
