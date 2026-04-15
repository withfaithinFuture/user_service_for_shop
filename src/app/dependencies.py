from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.services.cart_service import CartService
from src.services.order_service import OrderService
from src.services.user_service import UserService


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)


def get_cart_service(session: AsyncSession = Depends(get_session)):
    return CartService(session)


def get_order_service(session: AsyncSession = Depends(get_session)):
    return OrderService(session)
