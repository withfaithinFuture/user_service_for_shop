from uuid import UUID

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config import settings
from src.core.exceptions import NotEnoughStockError, NotFoundError
from src.repositories.cart_repository import CartRepository
from src.schemas.cart_schemas import AddToCartRequestSchema, UpdateCartItemRequestSchema

SELLER_SERVICE_URL = settings.SELLER_SERVICE_URL


class CartService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.cart_rep = CartRepository(self.session)

    async def get_products_from_seller(self, products_ids: list[UUID]) -> dict:
        if not products_ids:
            return {}

        str_ids = [str(id) for id in products_ids]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{SELLER_SERVICE_URL}/products/by-ids",
                    json={"productIds": str_ids},
                )
                response.raise_for_status()
                products_data = response.json()

                return {UUID(p["id"]): p for p in products_data}

            except Exception as e:
                print(f"Ошибка связи с сервисом селлера: {e}")
                raise HTTPException(
                    status_code=503, detail="Сервис товаров временно недоступен"
                )

    async def add_to_cart_service(
        self, user_id: UUID, data: AddToCartRequestSchema
    ) -> dict:
        products_info = await self.get_products_from_seller([data.productId])
        prod_data = products_info.get(data.productId)

        if not prod_data:
            raise NotFoundError(data.productId, "Product")

        if prod_data["available"] < data.quantity:
            raise NotEnoughStockError(
                data.productId, prod_data["available"], data.quantity
            )

        new_cart_count = await self.cart_rep.add_item_to_cart(
            user_id=user_id, product_id=data.productId, quantity=data.quantity
        )

        return {"success": True, "cartCount": new_cart_count}

    async def get_cart_service(self, user_id: UUID) -> dict:
        cart_items = await self.cart_rep.get_cart_items(user_id=user_id)
        if not cart_items:
            return {"items": [], "totalPrice": 0.0}

        product_ids = [item.productId for item in cart_items]
        products_info = await self.get_products_from_seller(products_ids=product_ids)

        items_list = []
        total_price = 0.0

        for item in cart_items:
            prod_data = products_info.get(item.productId)

            if not prod_data:
                continue

            price = float(prod_data["price"])
            total_price += price * item.quantity

            items_list.append(
                {
                    "productId": item.productId,
                    "name": prod_data["name"],
                    "price": price,
                    "available": prod_data["available"],
                    "quantity": item.quantity,
                    "img": prod_data.get("img"),
                    "market": prod_data.get("market"),
                }
            )

        return {"items": items_list, "totalPrice": round(total_price, 2)}

    async def update_cart_item_service(
        self, user_id: UUID, data: UpdateCartItemRequestSchema
    ) -> dict:
        products_info = await self.get_products_from_seller([data.productId])
        prod_data = products_info.get(data.productId)

        if not prod_data:
            raise NotFoundError(data.productId, "Product")

        if data.quantity > prod_data["available"]:
            raise NotEnoughStockError(
                product_id=data.productId,
                available=prod_data["available"],
                requested=data.quantity,
            )

        cart_cnt = await self.cart_rep.update_items_quantity(
            user_id=user_id, product_id=data.productId, quantity=data.quantity
        )
        cart_data = await self.get_cart_service(user_id)

        return {
            "success": True,
            "cartCount": cart_cnt,
            "totalPrice": cart_data["totalPrice"],
        }

    async def delete_cart_item_service(self, user_id: UUID, product_id: UUID) -> dict:
        cart_cnt = await self.cart_rep.delete_cart_item(
            user_id=user_id, product_id=product_id
        )
        cart_data = await self.get_cart_service(user_id)

        return {
            "success": True,
            "cartCount": cart_cnt,
            "totalPrice": cart_data["totalPrice"],
        }
