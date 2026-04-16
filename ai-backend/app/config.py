from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    llm_runtime: Literal["ollama", "vllm"] = "ollama"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "mistral"
    vllm_base_url: str = "http://vllm:8000"
    vllm_model: str = "mistralai/Mistral-7B-Instruct-v0.2"
    pinecone_api_key: str = ""
    pinecone_index: str = "chatforge"
    pinecone_namespace: str = "default"
    embedding_model: str = "all-MiniLM-L6-v2"
    mlflow_tracking_uri: str = "http://localhost:5000"
    wandb_api_key: str = ""
    wandb_project: str = "chatforge"
    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_top_k: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
