import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.ingest import chunk_text, load_document, IngestService


def test_chunk_text_basic():
    text = "word " * 200
    chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) <= 550


def test_chunk_text_small_input():
    text = "Hello world"
    chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == "Hello world"


def test_load_document_txt(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("Hello from a text file.")
    text = load_document(str(f))
    assert "Hello from a text file" in text


def test_load_document_unsupported(tmp_path):
    f = tmp_path / "test.xyz"
    f.write_text("data")
    with pytest.raises(ValueError, match="Unsupported file type"):
        load_document(str(f))


@pytest.mark.asyncio
async def test_ingest_service_processes_file(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_text("This is test content for ingestion. " * 20)

    mock_index = MagicMock()
    mock_index.upsert = MagicMock()

    mock_embed_model = MagicMock()
    mock_embed_model.encode.return_value = [[0.1] * 384]

    with patch("app.services.ingest.get_pinecone_index", return_value=mock_index), \
         patch("app.services.ingest.get_embedding_model", return_value=mock_embed_model):
        service = IngestService()
        result = await service.ingest_file(str(f), bot_id="test-bot", namespace="test")
        assert result.status == "complete"
        assert result.chunks_created > 0
        assert result.bot_id == "test-bot"


def test_ingest_endpoint_accepts_file(client):
    import io
    with patch("app.routers.ingest.IngestService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.ingest_file = AsyncMock(
            return_value=MagicMock(status="complete", chunks_created=5, bot_id="test")
        )
        resp = client.post(
            "/ingest",
            data={"bot_id": "test"},
            files={"file": ("test.txt", io.BytesIO(b"hello world"), "text/plain")},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "complete"
