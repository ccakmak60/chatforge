from typing import AsyncIterator

from app.config import settings
from app.schemas import ChatResponse
from app.providers import get_provider
from app.services.ingest import get_pinecone_index, get_embedding_model


SYSTEM_PROMPT = """You are a helpful assistant. Answer the user's question based on the provided context.
If the context doesn't contain relevant information, say so honestly.

Context:
{context}

Question: {question}

Answer:"""


class ChatService:
    def __init__(self):
        self.index = get_pinecone_index()
        self.embed_model = get_embedding_model()
        self.provider = get_provider()

    def _retrieve_context(self, message: str, bot_id: str, namespace: str | None = None) -> tuple[str, list[str]]:
        ns = namespace or settings.pinecone_namespace
        query_embedding_raw = self.embed_model.encode([message])[0]
        query_embedding = query_embedding_raw.tolist() if hasattr(query_embedding_raw, "tolist") else query_embedding_raw
        results = self.index.query(
            vector=query_embedding,
            top_k=settings.retrieval_top_k,
            include_metadata=True,
            namespace=ns,
            filter={"bot_id": {"$eq": bot_id}},
        )
        context_parts = []
        sources = []
        for match in results.matches:
            context_parts.append(match.metadata["text"])
            source = match.metadata.get("source", "unknown")
            if source not in sources:
                sources.append(source)
        context = "\n\n".join(context_parts)
        return context, sources

    async def get_response(
        self, message: str, bot_id: str, session_id: str, namespace: str | None = None
    ) -> ChatResponse:
        context, sources = self._retrieve_context(message, bot_id, namespace)
        prompt = SYSTEM_PROMPT.format(context=context, question=message)
        response = await self.provider.generate(prompt)
        return ChatResponse(
            session_id=session_id,
            bot_id=bot_id,
            response=response,
            sources=sources,
        )

    async def stream_response(
        self, message: str, bot_id: str, session_id: str, namespace: str | None = None
    ) -> AsyncIterator[str]:
        context, _sources = self._retrieve_context(message, bot_id, namespace)
        prompt = SYSTEM_PROMPT.format(context=context, question=message)
        async for token in self.provider.stream(prompt):
            yield token
