from dotenv import load_dotenv

load_dotenv()

from pathlib import Path

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_url: PostgresDsn
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    SELLER_SERVICE_URL: str
    TEST_DATABASE_URL: str
    TEST_USER: dict = {
        "login": "test_log",
        "password": "NiceC1!",
        "firstName": "Леха",
        "lastName": "Тестов",
        "patronymic": "Тестович",
        "dateOfBirth": "1990-01-01",
        "city": "Москва",
        "isSeller": False,
    }
    ORDER_PAYLOAD: dict = {
        "deliveryAddress": "ул. Тестовая, д. 10",
        "deliveryCity": "Москва",
        "phone": "89991234567",
        "deliveryComment": "Оставить у двери",
    }

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env", extra="ignore"
    )


settings = Settings()
