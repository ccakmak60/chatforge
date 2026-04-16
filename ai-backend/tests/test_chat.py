import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.chat import ChatService


@pytest.mark.asyncio
async def test_chat_service_returns_response():
    mock_index = MagicMock()
    mock_index.query.return_value = MagicMock(
        matches=[
            MagicMock(metadata={"text": "Paris is the capital of France.", "source": "doc.txt"}, score=0.95),
        ]
    )
    mock_embed = MagicMock()
    mock_embed.encode.return_value = [[0.1] * 384]

    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "Paris is the capital of France."

    with patch("app.services.chat.get_pinecone_index", return_value=mock_index), \
         patch("app.services.chat.get_embedding_model", return_value=mock_embed), \
         patch("app.services.chat.get_provider", return_value=mock_provider):
        service = ChatService()
        result = await service.get_response(
            message="What is the capital of France?",
            bot_id="test-bot",
            session_id="sess-1",
        )
        assert result.response == "Paris is the capital of France."
        assert len(result.sources) == 1
        assert result.session_id == "sess-1"


def test_chat_endpoint_returns_json(client):
    with patch("app.routers.chat.ChatService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.get_response = AsyncMock(
            return_value=MagicMock(
                session_id="s1", bot_id="b1",
                response="Hello", sources=["doc.txt"],
            )
        )
        resp = client.post("/chat", json={
            "session_id": "s1", "bot_id": "b1", "message": "Hi"
        })
        assert resp.status_code == 200
        assert resp.json()["response"] == "Hello"


def test_chat_stream_endpoint(client):
    async def mock_stream(*args, **kwargs):
        for word in ["Hello", " ", "world"]:
            yield word

    with patch("app.routers.chat.ChatService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.stream_response = mock_stream
        resp = client.post(
            "/chat/stream",
            json={"session_id": "s1", "bot_id": "b1", "message": "Hi"},
        )
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]
