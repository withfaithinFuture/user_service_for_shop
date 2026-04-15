from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import Row, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cart import Cart
from src.models.cart_items import CartItems


class CartRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_item_to_cart(
        self, user_id: UUID, product_id: UUID, quantity: int
    ) -> int:

        query_cart = select(Cart).where(Cart.userId == user_id)
        result = await self.session.execute(query_cart)
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(userId=user_id)
            self.session.add(cart)
            await self.session.commit()
            await self.session.refresh(cart)

        query_item = select(CartItems).where(
            (CartItems.cartId == cart.id) & (CartItems.productId == product_id)
        )

        result = await self.session.execute(query_item)
        item = result.scalar_one_or_none()

        if item:
            item.quantity += quantity
        else:
            new_item = CartItems(
                cartId=cart.id, productId=product_id, quantity=quantity
            )
            self.session.add(new_item)

        await self.session.flush()

        query_cnt = select(func.coalesce(func.sum(CartItems.quantity), 0)).where(
            CartItems.cartId == cart.id
        )
        result = await self.session.scalar(query_cnt)

        return result

    async def get_cart_items(
        self, user_id: UUID
    ) -> Sequence[Row[tuple[Any, Any, Any]]]:

        query = (
            select(CartItems)
            .join(Cart, Cart.id == CartItems.cartId)
            .where(Cart.userId == user_id)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_items_quantity(
        self, user_id: UUID, product_id: UUID, quantity: int
    ) -> tuple[int, float]:
        query_cart = select(Cart).where(Cart.userId == user_id)
        result = await self.session.execute(query_cart)
        cart = result.scalar()

        query_update = (
            update(CartItems)
            .where(CartItems.cartId == cart.id, CartItems.productId == product_id)
            .values(quantity=quantity)
        )

        await self.session.execute(query_update)
        await self.session.flush()

        query_cnt = select(func.coalesce(func.sum(CartItems.quantity), 0)).where(
            CartItems.cartId == cart.id
        )
        return await self.session.scalar(query_cnt)

    async def delete_cart_item(self, user_id: UUID, product_id: UUID) -> int:
        query_cart = select(Cart).where(Cart.userId == user_id)
        cart = await self.session.scalar(query_cart)
        if not cart:
            return 0

        query_delete = delete(CartItems).where(
            CartItems.cartId == cart.id, CartItems.productId == product_id
        )

        await self.session.execute(query_delete)
        await self.session.flush()

        query_cnt = select(func.coalesce(func.sum(CartItems.quantity), 0)).where(
            CartItems.cartId == cart.id
        )

        return await self.session.scalar(query_cnt)
