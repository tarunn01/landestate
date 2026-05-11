from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    DEBUG: bool = True
    SECRET_KEY: str
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = "landestate-images-tarun"

    class Config:
        env_file = ".env"


settings = Settings()
