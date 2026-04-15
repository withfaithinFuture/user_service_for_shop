import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    login: str
    password: str
    firstName: str
    lastName: str
    patronymic: str
    dateOfBirth: datetime.date
    city: str
    telegram: str
    telegramChatId: str
    isSeller: str
    createdAt: datetime.date

    model_config = ConfigDict(from_attributes=True)


class UserMeResponseSchema(BaseModel):
    userId: UUID
    login: str
    firstName: str
    isSeller: bool
    cartCount: int = Field(0, description="Количество товаров в корзине")

    model_config = ConfigDict(from_attributes=True)
