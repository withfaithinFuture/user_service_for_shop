from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path
from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: PostgresDsn = Field(env='POSTGRES_URL')
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    SELLER_SERVICE_URL: str = os.getenv("SELLER_SERVICE_URL")

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        extra = "ignore"

settings = Settings()