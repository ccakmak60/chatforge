import json

import mlflow

from app.config import settings
from app.schemas import EvaluateResponse
from app.providers import get_provider
from app.services.ingest import get_pinecone_index, get_embedding_model


def compute_faithfulness(answer: str, context: str) -> float:
    answer_words = set(answer.lower().split())
    context_words = set(context.lower().split())
    if not answer_words:
        return 0.0
    overlap = answer_words & context_words
    return len(overlap) / len(answer_words)


def compute_relevance(answer: str, expected: str) -> float:
    answer_words = set(answer.lower().split())
    expected_words = set(expected.lower().split())
    if not expected_words:
        return 0.0
    overlap = answer_words & expected_words
    return len(overlap) / len(expected_words)


class EvaluateService:
    def __init__(self):
        self.index = get_pinecone_index()
        self.embed_model = get_embedding_model()
        self.provider = get_provider()

    async def evaluate(
        self, bot_id: str, test_data: list[dict]
    ) -> EvaluateResponse:
        faithfulness_scores = []
        relevance_scores = []

        for item in test_data:
            question = item["question"]
            expected = item["expected"]

            query_emb_raw = self.embed_model.encode([question])[0]
            query_emb = query_emb_raw.tolist() if hasattr(query_emb_raw, "tolist") else query_emb_raw
            results = self.index.query(
                vector=query_emb,
                top_k=settings.retrieval_top_k,
                include_metadata=True,
                namespace=settings.pinecone_namespace,
                filter={"bot_id": {"$eq": bot_id}},
            )
            context = "\n".join(m.metadata["text"] for m in results.matches)

            answer = await self.provider.generate(
                f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
            )

            faithfulness_scores.append(compute_faithfulness(answer, context))
            relevance_scores.append(compute_relevance(answer, expected))

        metrics = {
            "faithfulness": sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0.0,
            "relevance": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0,
            "num_samples": len(test_data),
        }

        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        with mlflow.start_run(run_name=f"eval-{bot_id}") as run:
            mlflow.log_metrics(metrics)
            mlflow.log_param("bot_id", bot_id)
            run_id = run.info.run_id

        return EvaluateResponse(status="complete", metrics=metrics, run_id=run_id)

    async def evaluate_from_file(
        self, bot_id: str, test_dataset_path: str
    ) -> EvaluateResponse:
        with open(test_dataset_path, "r", encoding="utf-8") as f:
            test_data = json.load(f)
        return await self.evaluate(bot_id=bot_id, test_data=test_data)
