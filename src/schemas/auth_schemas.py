from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RegisterRequest(BaseModel):
    login: str
    password: str
    firstName: str
    lastName: Optional[str] = None
    patronymic: Optional[str] = None
    dateOfBirth: Optional[date] = None
    city: Optional[str] = None
    telegram: Optional[str] = None
    isSeller: bool = False


class LoginRequest(BaseModel):
    login: str
    password: str


class UserResponseSchema(BaseModel):
    userId: UUID
    login: str
    firstName: str
    isSeller: bool


class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserResponseSchema] = None
    token: Optional[str] = None
    message: Optional[str] = None
