from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API设置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "智能文档问答系统"

    # DeepSeek设置
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"

    # 向量数据库设置
    CHROMA_DB_PATH: str = "./chroma_db"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # 文档处理设置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt"]
    CHUNK_SIZE: int = 350
    CHUNK_OVERLAP: int = 50

    # 检索设置
    SIMILARITY_THRESHOLD: float = 0.7
    MAX_RETRIEVED_DOCS: int = 5

    # 日志设置
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()