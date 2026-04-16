import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas import ChatRequest, ChatResponse
from app.services.chat import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    service = ChatService()
    return await service.get_response(
        message=req.message,
        bot_id=req.bot_id,
        session_id=req.session_id,
    )


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    service = ChatService()

    async def event_generator():
        async for token in service.stream_response(
            message=req.message,
            bot_id=req.bot_id,
            session_id=req.session_id,
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
