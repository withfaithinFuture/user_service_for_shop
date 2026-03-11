from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path
from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


class Settings(BaseSettings):
    postgres_url: PostgresDsn = Field(env='POSTGRES_URL')

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        extra = "ignore"