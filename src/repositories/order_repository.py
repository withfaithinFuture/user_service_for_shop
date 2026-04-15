from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy import Row, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cart_items import CartItems
from src.models.order import Order, OrderStatus
from src.models.order_item import OrderItems
from src.models.order_market import OrderMarket
from src.schemas.order_schemas import CreateOrderRequestSchema


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order_from_cart(
        self,
        user_id: UUID,
        order_data: CreateOrderRequestSchema,
        total_order_price: float,
        markets_data: dict,
        cart_id: UUID,
    ) -> UUID | None:

        new_order = Order(
            userId=user_id,
            totalPrice=Decimal(total_order_price),
            deliveryAddress=order_data.deliveryAddress,
            deliveryCity=order_data.deliveryCity,
            phone=order_data.phone,
            deliveryComment=order_data.deliveryComment,
            status=OrderStatus.GENERATED.value,
        )
        self.session.add(new_order)
        await self.session.flush()

        for market_id, market_info in markets_data.items():
            order_market = OrderMarket(
                orderId=new_order.orderId,
                marketId=market_id,
                totalPrice=market_info["total"],
                status=OrderStatus.GENERATED.value,
            )
            self.session.add(order_market)
            await self.session.flush()

            for item in market_info["items"]:
                order_item = OrderItems(
                    orderId=new_order.orderId,
                    orderMarketId=order_market.id,
                    productId=item["product_id"],
                    quantity=item["quantity"],
                    priceAtPurchase=item["price"],
                )
                self.session.add(order_item)

        await self.session.execute(delete(CartItems).where(CartItems.cartId == cart_id))

        return new_order.orderId

    async def get_user_orders(
        self, user_id: UUID, limit: int, offset: int
    ) -> tuple[Sequence[Row], int]:
        count_query = (
            select(func.count()).select_from(Order).where(Order.userId == user_id)
        )
        total_orders_cnt = await self.session.scalar(count_query)

        if not total_orders_cnt:
            return [], 0

        query = (
            select(
                Order.orderId,
                Order.createdAt,
                Order.status,
                Order.totalPrice,
                func.coalesce(func.sum(OrderItems.quantity), 0).label("totalItems"),
            )
            .outerjoin(OrderMarket, OrderMarket.orderId == Order.orderId)
            .outerjoin(OrderItems, OrderItems.orderMarketId == OrderMarket.id)
            .where(Order.userId == user_id)
            .group_by(Order.orderId)
            .order_by(Order.createdAt.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        orders = result.all()

        return orders, total_orders_cnt

    async def get_order_details(self, order_id: UUID, user_id: UUID) -> Sequence[Row]:
        query = (
            select(Order, OrderMarket, OrderItems)
            .join(OrderMarket, OrderMarket.orderId == Order.orderId)
            .join(OrderItems, OrderItems.orderMarketId == OrderMarket.id)
            .where(Order.userId == user_id, Order.orderId == order_id)
        )

        result = await self.session.execute(query)
        return result.all()
