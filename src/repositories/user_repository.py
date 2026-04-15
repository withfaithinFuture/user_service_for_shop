from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cart import Cart
from src.models.cart_items import CartItems
from src.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_me_data(self, user_id: UUID):
        query = (
            select(
                User.userId,
                User.login,
                User.firstName,
                User.isSeller,
                func.coalesce(func.sum(CartItems.quantity), 0).label("cartCount"),
            )
            .outerjoin(Cart, Cart.userId == User.userId)
            .outerjoin(CartItems, CartItems.cartId == Cart.id)
            .where(User.userId == user_id)
            .group_by(User.userId)
        )

        result = await self.session.execute(query)

        return result.mappings().first()
