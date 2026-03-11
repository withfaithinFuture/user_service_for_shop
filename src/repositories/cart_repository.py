from typing import Any, Sequence
from sqlalchemy import select, func, Row, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.models.cart_items import CartItems
from src.models.market import Market
from src.models.product import Product
from src.models.cart import Cart


class CartRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def add_item_to_cart(self, user_id: UUID, product_id: UUID, quantity: int) -> int:

        query_cart = select(Cart).where(Cart.userId == user_id)
        result = await self.session.execute(query_cart)
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(userId=user_id)
            self.session.add(cart)
            await self.session.commit()
            await self.session.refresh(cart)

        query_item = select(CartItems).where((CartItems.cartId == cart.id) &
    (CartItems.productId == product_id))

        result = await self.session.execute(query_item)
        item = result.scalar_one_or_none()

        if item:
            item.quantity += quantity
        else:
            new_item = CartItems(cartId=cart.id, productId=product_id, quantity=quantity)
            self.session.add(new_item)

        await self.session.flush()

        query_cnt = select(func.coalesce(func.sum(CartItems.quantity), 0)).where(CartItems.cartId == cart.id)
        result = await self.session.scalar(query_cnt)

        return result


    async def get_cart_items(self, user_id: UUID) -> Sequence[Row[tuple[Any, Any, Any]]]:
        query = (
            select(CartItems, Product, Market)
            .join(Cart, Cart.id == CartItems.cartId)
            .join(Product, Product.id == CartItems.productId)
            .join(Market, Market.marketId == Product.marketId)
            .where(Cart.userId == user_id)
        )

        result = await self.session.execute(query)

        return result.all()


    async def update_items_quantity(self, user_id: UUID, product_id: UUID, quantity: int) -> tuple[int, float]:
        query_cart = select(Cart).where(Cart.userId == user_id)
        result = await self.session.execute(query_cart)
        cart = result.scalar()

        query_update = (
            update(CartItems).where(
                CartItems.cartId == cart.id,
                CartItems.productId == product_id
            ).values(quantity=quantity)
        )

        result_upd = await self.session.execute(query_update)
        await self.session.flush()

        query_totals = (
            select(
                func.coalesce(func.sum(CartItems.quantity), 0).label('cartCount'),
                func.coalesce(func.sum(CartItems.quantity * Product.price), 0).label('totalPrice')
            ).join(Product, Product.id == CartItems.productId)
            .where(CartItems.cartId == cart.id)
        )

        result_totals = await self.session.execute(query_totals)
        await self.session.flush()

        total = result_totals.first()

        cart_cnt = 0
        total_price = 0.0
        if total:
            cart_cnt = total.cartCount
            total_price = float(total.totalPrice)

        return cart_cnt, total_price


    async def delete_cart_item(self, user_id: UUID, product_id: UUID) -> tuple[int, float]:
        query_cart = select(Cart).where(Cart.userId == user_id)
        cart = await self.session.scalar(query_cart)
        if not cart:
            return 0, 0.0

        query_delete = (
            delete(CartItems).where(
                CartItems.cartId == cart.id,
                CartItems.productId == product_id
            )
        )

        await self.session.execute(query_delete)
        await self.session.flush()

        query_totals = select(
            func.coalesce(func.sum(CartItems.quantity), 0).label('cartCount'),
            func.coalesce(func.sum(CartItems.quantity * Product.price), 0).label('totalPrice')
        ).select_from(CartItems).join(Product, Product.id == CartItems.productId).where(CartItems.cartId == cart.id)

        result_totals = await self.session.execute(query_totals)
        data = result_totals.first()

        await self.session.flush()

        cart_cnt, total_price = 0, 0.0
        if data:
            cart_cnt = data.cartCount
            total_price = float(data.totalPrice)

        return cart_cnt, total_price