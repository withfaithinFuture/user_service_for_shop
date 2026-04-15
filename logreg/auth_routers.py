from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from logreg.auth_service import AuthService
from logreg.security import get_current_user
from src.db.db import get_session
from src.models.user import User
from src.schemas.auth_schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponseSchema,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthResponse,
    description="Создание нового юзера и возвращение токена доступа",
)
async def register(
    request: RegisterRequest, session: AsyncSession = Depends(get_session)
):
    auth_service = AuthService(session)
    user, result = await auth_service.register(request)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)

    return {
        "success": True,
        "user": {
            "userId": user.userId,
            "login": user.login,
            "firstName": user.firstName,
            "isSeller": user.isSeller,
        },
        "token": result,
    }


@router.post(
    "/login",
    response_model=AuthResponse,
    description="Вход в систему, возвращение токена доступа",
)
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):

    auth_service = AuthService(session)
    user, result = await auth_service.login(request)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result)

    return {
        "success": True,
        "user": {
            "userId": user.userId,
            "login": user.login,
            "firstName": user.firstName,
            "isSeller": user.isSeller,
        },
        "token": result,
    }


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
    description="Возвращение информации о текущем авторизованном юзере",
)
async def get_auth_me(current_user: User = Depends(get_current_user)):
    return {
        "userId": current_user.userId,
        "login": current_user.login,
        "firstName": current_user.firstName,
        "isSeller": current_user.isSeller,
    }
