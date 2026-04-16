from pathlib import Path
import json

from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.schemas import IngestResponse


def get_pinecone_index():
    pc = Pinecone(api_key=settings.pinecone_api_key)
    return pc.Index(settings.pinecone_index)


def get_embedding_model():
    return SentenceTransformer(settings.embedding_model)


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks


def load_document(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif ext == ".docx":
        from docx import Document

        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    elif ext == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


class IngestService:
    def __init__(self):
        self.index = get_pinecone_index()
        self.embed_model = get_embedding_model()

    async def ingest_file(
        self, file_path: str, bot_id: str, namespace: str | None = None
    ) -> IngestResponse:
        ns = namespace or settings.pinecone_namespace
        text = load_document(file_path)
        chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)

        raw_embeddings = self.embed_model.encode(chunks)
        embeddings = raw_embeddings.tolist() if hasattr(raw_embeddings, "tolist") else raw_embeddings

        vectors = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            vec_id = f"{bot_id}_{Path(file_path).stem}_{i}"
            vectors.append(
                {
                    "id": vec_id,
                    "values": emb,
                    "metadata": {
                        "text": chunk,
                        "bot_id": bot_id,
                        "source": Path(file_path).name,
                    },
                }
            )

        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            self.index.upsert(vectors=vectors[i : i + batch_size], namespace=ns)

        return IngestResponse(status="complete", chunks_created=len(chunks), bot_id=bot_id)
