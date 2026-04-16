import { buildApp } from "./app";

const port = Number(process.env.PORT ?? 8080);
const app = buildApp();

app.listen(port, () => {
  console.log(`api-gateway listening on ${port}`);
});
