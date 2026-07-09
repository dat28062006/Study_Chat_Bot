from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://raguser:ragpass@localhost:5432/ragdb"
    redis_url: str = "redis://localhost:6379"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    openai_api_key: str = ""
    openai_base_url: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-southeast-1"
    s3_bucket: str = ""

    upload_dir: str = "./uploads"
    use_s3: bool = False

    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""

    n8n_webhook_url: str = ""

    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 3

    class Config:
        env_file = (".env", "../.env")
        extra = "ignore"


settings = Settings()
