import math
from collections import defaultdict
from uuid import UUID

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config import settings
from src.core.exceptions import NotEnoughStockError, NotFoundError
from src.repositories.cart_repository import CartRepository
from src.repositories.order_repository import OrderRepository
from src.schemas.order_schemas import CreateOrderRequestSchema

SELLER_SERVICE_URL = settings.SELLER_SERVICE_URL


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repository = OrderRepository(session)
        self.cart_repository = CartRepository(session)

    async def get_products_info(self, products_ids: list[UUID]) -> dict:
        str_ids = [str(id) for id in products_ids]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{SELLER_SERVICE_URL}/products/by-ids",
                    json={"productIds": str_ids},
                )
                response.raise_for_status()
                return {product["id"]: product for product in response.json()}

            except Exception:
                raise HTTPException(status_code=503, detail="Сервис товаров недоступен")

    async def reserve_products_at_seller(self, items_to_reserve: list[dict]):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{SELLER_SERVICE_URL}/internal/products/reserve",
                    json={"items": items_to_reserve},
                )

                if response.status_code == 400:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Ошибка резервирования: {response.text}",
                    )

                response.raise_for_status()

            except httpx.RequestError:
                raise HTTPException(
                    status_code=503,
                    detail="Сервис товаров недоступен для резервирования",
                )

    async def create_order_service(
        self, user_id: UUID, order_data: CreateOrderRequestSchema
    ) -> dict:
        cart_items = await self.cart_repository.get_cart_items(user_id=user_id)

        if not cart_items:
            raise NotFoundError(object_id=user_id, object_type="cart")

        product_ids = [item.productId for item in cart_items]
        cart_id = cart_items[0].cartId
        products_info = await self.get_products_info(products_ids=product_ids)

        total_order_price = 0.0
        markets_data = defaultdict(lambda: {"total": 0.0, "items": []})
        items_for_reservation = []

        for cart_item in cart_items:
            id_str = str(cart_item.productId)
            product_data = products_info.get(id_str)

            if not product_data:
                raise HTTPException(
                    status_code=400, detail=f"Товар {id_str} больше недоступен"
                )

            if cart_item.quantity > product_data["available"]:
                raise NotEnoughStockError(
                    product_id=cart_item.productId,
                    available=product_data["available"],
                    requested=cart_item.quantity,
                )

            price = float(product_data["price"])
            item_price_total = price * cart_item.quantity
            total_order_price += item_price_total
            market_id = product_data["marketId"]

            markets_data[market_id]["total"] += item_price_total
            markets_data[market_id]["items"].append(
                {"product_id": id_str, "quantity": cart_item.quantity, "price": price}
            )

            items_for_reservation.append(
                {"productId": id_str, "quantity": cart_item.quantity}
            )

        await self.reserve_products_at_seller(items_to_reserve=items_for_reservation)

        order_id = await self.order_repository.create_order_from_cart(
            user_id=user_id,
            order_data=order_data,
            total_order_price=total_order_price,
            markets_data=markets_data,
            cart_id=cart_id,
        )

        return {"success": True, "orderId": str(order_id)}

    async def get_user_orders_service(
        self, user_id: UUID, page: int, limit: int
    ) -> dict:
        offset = (page - 1) * limit
        orders, total_orders_cnt = await self.order_repository.get_user_orders(
            user_id=user_id, offset=offset, limit=limit
        )
        total_pages = math.ceil(total_orders_cnt / limit) if total_orders_cnt > 0 else 1

        return {
            "success": True,
            "orders": [
                {
                    "orderId": str(order.orderId),
                    "createdAt": order.createdAt,
                    "status": order.status,
                    "totalPrice": float(order.totalPrice),
                    "totalItems": order.totalItems,
                }
                for order in orders
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "totalItems": total_orders_cnt,
                "totalPages": total_pages,
            },
        }

    async def get_order_details_service(self, order_id: UUID, user_id: UUID) -> dict:
        order_details = await self.order_repository.get_order_details(
            order_id=order_id, user_id=user_id
        )

        if not order_details:
            raise NotFoundError(object_id=order_id, object_type="Order")

        product_ids = list(set([row.OrderItems.productId for row in order_details]))
        product_info = await self.get_products_info(products_ids=product_ids)
        first_order = order_details[0][0]
        markets_dict = {}

        for details in order_details:
            order_market = details.OrderMarket
            order_item = details.OrderItems
            market_id_str = str(order_market.marketId)

            if market_id_str not in markets_dict:
                markets_dict[market_id_str] = {
                    "marketId": order_market.marketId,
                    "status": order_market.status,
                    "totalPrice": float(order_market.totalPrice),
                    "items": [],
                }

            markets_dict[market_id_str]["items"].append(
                {
                    "productId": order_item.productId,
                    "name": product_info[str(order_item.productId)]["name"],
                    "quantity": order_item.quantity,
                    "priceAtPurchase": float(order_item.priceAtPurchase),
                }
            )

        return {
            "orderId": first_order.orderId,
            "createdAt": first_order.createdAt,
            "status": first_order.status,
            "totalPrice": float(first_order.totalPrice),
            "deliveryAddress": first_order.deliveryAddress,
            "deliveryCity": first_order.deliveryCity,
            "markets": list(markets_dict.values()),
        }
