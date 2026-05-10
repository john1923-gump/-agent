from pydantic import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "BGE-small-zh"
    rag_top_k: int = 5
    chunk_size: int = 700
    chunk_overlap: int = 100
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
