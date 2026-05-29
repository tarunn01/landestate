from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    DEBUG: bool = True
    SECRET_KEY: str
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = "landestate-images-tarun"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()
