import math
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
from src.core.exceptions import NotFoundError, NotEnoughStockError
from src.repositories.order_repository import OrderRepository
from src.repositories.cart_repository import CartRepository
from src.schemas.order_schemas import CreateOrderRequestSchema


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repository = OrderRepository(session)
        self.cart_repository = CartRepository(session)


    async def create_order_service(self, user_id: UUID, order_data: CreateOrderRequestSchema) -> dict:
        cart_items = await self.cart_repository.get_cart_items(user_id=user_id)

        if not cart_items:
            raise NotFoundError(object_id=user_id, object_type='cart')

        total_order_price = 0.0
        markets_data = defaultdict(lambda: {"total": 0.0, "items": []})
        cart_id = cart_items[0][0].cartId

        for cart_item, product, market in cart_items:
            if cart_item.quantity > product.available:
                raise NotEnoughStockError(product_id=product.id, available=product.available, requested=cart_item.quantity)

            item_price_total = float(product.price) * cart_item.quantity
            total_order_price += item_price_total

            markets_data[market.marketId]['total'] += item_price_total
            markets_data[market.marketId]['items'].append({
                "product_model": product,
                "quantity": cart_item.quantity,
                "price": float(product.price)
            })

        order_id = await self.order_repository.create_order_from_cart(user_id=user_id, order_data=order_data, total_order_price=total_order_price, markets_data=markets_data, cart_id=cart_id)

        return {
            "success": True,
            "orderId": str(order_id)
        }


    async def get_user_orders_service(self, user_id: UUID, page: int, limit: int) -> dict:
        offset = (page - 1) * limit
        orders, total_orders_cnt = await self.order_repository.get_user_orders(user_id=user_id, offset=offset, limit=limit)
        total_pages = math.ceil(total_orders_cnt / limit) if total_orders_cnt > 0 else 1

        return {
            "success": True,
            "orders": [
                {
                    "orderId": str(order.orderId),
                    "createdAt": order.createdAt,
                    "status": order.status,
                    "totalPrice": float(order.totalPrice),
                    "totalItems": order.totalItems
                }
                for order in orders
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "totalItems": total_orders_cnt,
                "totalPages": total_pages
            }
        }


    async def get_order_details_service(self, order_id: UUID, user_id: UUID) -> dict:
        order_details = await self.order_repository.get_order_details(order_id=order_id, user_id=user_id)

        if not order_details:
            raise NotFoundError(object_id=order_id, object_type='Order')


        first_order = order_details[0][0]
        markets_dict = {}

        for order, order_market, order_item, product, market in order_details:
            market_id = order_market.marketId

            if market_id not in markets_dict:
                markets_dict[market_id] = {
                    "marketId": market.marketId,
                    "marketName": market.marketName,
                    "status": order_market.status,
                    "totalPrice": float(order_market.totalPrice),
                    "items": []
                }

                markets_dict[market_id]["items"].append({
                    "productId": product.id,
                    "name": product.name,
                    "quantity": order_item.quantity,
                    "priceAtPurchase": float(order_item.priceAtPurchase)
                })

        return {
            "orderId": first_order.orderId,
            "createdAt": first_order.createdAt,
            "status": first_order.status,
            "totalPrice": float(first_order.totalPrice),
            "deliveryAddress": first_order.deliveryAddress,
            "deliveryCity": first_order.deliveryCity,
            "markets": list(markets_dict.values())
        }