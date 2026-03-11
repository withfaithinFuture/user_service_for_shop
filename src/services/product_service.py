import math
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.product_schemas import ProductFilterParams
from src.repositories.product_repository import ProductRepository as prodrepo


class ProductService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = prodrepo(session)


    async def get_products_service(self, filters: ProductFilterParams) -> dict:

        offset = (filters.page - 1) * filters.limit
        items, total_items = await self.repo.get_products(filters=filters)

        total_pages = math.ceil(total_items / filters.limit) if total_items > 0 else 0

        return {
            'items': items,
            'pagination': {
                'page': filters.page,
                'limit': filters.limit,
                'totalItems': total_items,
                'totalPages': total_pages
            }
        }


    async def get_product_by_id_service(self, product_id: UUID) -> dict | None:
        data = await self.repo.get_product_by_id(product_id=product_id)

        if not data:
            return None

        product, market = data

        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "price": float(product.price),
            "available": product.available,
            "img": product.img,
            "market": {
                "marketId": market.marketId,
                "marketName": market.marketName
            }
        }
