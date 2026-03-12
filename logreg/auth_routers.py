from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.auth_schemas import RegisterRequest, LoginRequest, AuthResponse, UserResponseSchema
from logreg.auth_service import AuthService
from src.db.db import get_session
from logreg.security import get_current_user
from src.models.user import User


router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session)
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
            "isSeller": user.isSeller
        },
        "token": result
    }

@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    """Авторизация (получение токена)"""
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
            "isSeller": user.isSeller
        },
        "token": result
    }

@router.get("/me", response_model=UserResponseSchema)
async def get_auth_me(current_user: User = Depends(get_current_user)):
    return {
        "userId": current_user.userId,
        "login": current_user.login,
        "firstName": current_user.firstName,
        "isSeller": current_user.isSeller
    }