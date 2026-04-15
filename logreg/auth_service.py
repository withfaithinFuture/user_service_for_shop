from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from logreg.security import create_access_token, hash_password, verify_password
from src.app.config import settings
from src.models.user import User
from src.models.user_token import UserToken


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(self, request):
        existing_user = await self.session.scalar(
            select(User).where(User.login == request.login)
        )
        if existing_user:
            return None, "Пользователь с таким логином уже существует"

        user = User(
            login=request.login,
            passwordHash=hash_password(request.password),
            firstName=request.firstName,
            lastName=request.lastName,
            patronymic=request.patronymic,
            dateOfBirth=request.dateOfBirth,
            city=request.city,
            isSeller=request.isSeller,
            createdAt=datetime.now(timezone.utc),
        )

        self.session.add(user)
        await self.session.flush()

        token_str = create_access_token({"sub": str(user.userId)})
        token = UserToken(
            userId=user.userId,
            token=token_str,
            expiresAt=datetime.utcnow()
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        self.session.add(token)

        return user, token_str

    async def login(self, request):
        user = await self.session.scalar(
            select(User).where(User.login == request.login)
        )
        if not user or not verify_password(request.password, user.passwordHash):
            return None, "Неверный логин или пароль"

        token_str = create_access_token({"sub": str(user.userId)})
        token = UserToken(
            userId=user.userId,
            token=token_str,
            expiresAt=datetime.utcnow()
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        self.session.add(token)

        return user, token_str
