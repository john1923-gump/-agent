from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "学科知识整合智能体"
    DEBUG: bool = True

    LLM_BASE_URL: str = "https://api-inference.modelscope.cn/v1/"
    LLM_API_KEY: str = "ms-placeholder"
    LLM_MODEL: str = "deepseek-ai/DeepSeek-V3.2"

    EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"
    FAISS_INDEX_DIR: str = str(BASE_DIR / "data" / "indexes")
    UPLOAD_DIR: str = str(BASE_DIR / "data" / "uploads")

    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 80
    TOP_K: int = 5

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = str(BASE_DIR / ".env")


settings = Settings()

Path(settings.FAISS_INDEX_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
