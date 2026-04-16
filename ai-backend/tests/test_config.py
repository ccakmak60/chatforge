from app.config import Settings


def test_default_settings():
    s = Settings(pinecone_api_key="test", wandb_api_key="test")
    assert s.llm_runtime == "ollama"
    assert s.chunk_size == 500
    assert s.retrieval_top_k == 5


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_request_id_header(client):
    resp = client.get("/health")
    assert "X-Request-ID" in resp.headers
