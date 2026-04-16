import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import ErrorResponse

app = FastAPI(title="ChatForge AI Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            code=500,
            error="internal_error",
            detail=str(exc),
            request_id=request_id,
        ).model_dump(),
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
