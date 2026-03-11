from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.util import total_size

from src.repositories.cart_repository import CartRepository
from src.schemas.cart_schemas import AddToCartResponseSchema, UpdateCartItemRequestSchema, AddToCartRequestSchema
from src.core.exceptions import NotFoundError, NotEnoughStockError
from src.repositories.product_repository import ProductRepository as prodrepo


class CartService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.cart_rep = CartRepository(self.session)
        self.product_rep = prodrepo(self.session)


    async def add_to_cart_service(self, user_id: UUID, data: AddToCartRequestSchema) -> dict:
        product = await self.product_rep.get_product_by_id(product_id=data.productId)
        if not product:
            raise NotFoundError(data.productId, 'Product')

        product, market = product
        if product.available < data.quantity:
            raise NotEnoughStockError(product.id, product.available, data.quantity)

        new_cart_count = await self.cart_rep.add_item_to_cart(user_id=user_id, product_id=data.productId, quantity=data.quantity)

        return {
            'success': True,
            'cartCount': new_cart_count
        }


    async def get_cart_service(self, user_id: UUID) -> dict:
        items = await self.cart_rep.get_cart_items(user_id=user_id)
        items_list = []
        total_price = 0.0

        for cart_item, product, market in items:
            total_price += (float(product.price) * cart_item.quantity)

            items_list.append({
                'productId': product.id,
                'name': product.name,
                'price': float(product.price),
                'available': product.available,
                'quantity': cart_item.quantity,
                'img': product.img,
                'market': {
                    'marketId': market.marketId,
                    'marketName': market.marketName
                }
            })

        return {
            'items': items_list,
            'totalPrice': round(total_price, 2)
        }


    async def update_cart_item_service(self, user_id: UUID, data: UpdateCartItemRequestSchema) -> dict:
        product_data = await self.product_rep.get_product_by_id(data.productId)
        if not product_data:
            raise NotFoundError(data.productId, 'Product')

        product, market = product_data

        if data.quantity > product.available:
            raise NotEnoughStockError(product_id=product.id, available=product.available, requested=data.quantity)

        cart_cnt, total_price = await self.cart_rep.update_items_quantity(user_id=user_id, product_id=data.productId, quantity=data.quantity)

        return {
            'success': True,
            'cartCount': cart_cnt,
            'totalPrice': round(total_price, 2)
        }


    async def delete_cart_item_service(self, user_id: UUID, product_id: UUID) -> dict:
        cart_cnt, total_price = await self.cart_rep.delete_cart_item(user_id=user_id, product_id=product_id)

        return {
            'success': True,
            'cartCount': cart_cnt,
            'totalPrice': round(total_price, 2)
        }