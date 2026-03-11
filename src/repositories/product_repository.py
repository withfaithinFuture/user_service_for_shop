from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.product_schemas import ProductFilterParams
from src.models.market import Market
from src.models.product import Product


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_products(self, filters: ProductFilterParams) -> tuple[list[dict], int]:

        query = select(Product, Market).join(Market, Market.marketId == Product.marketId)

        if filters.search:
            query = query.where(Product.name.ilike(f'%{filters.search}%'))

        if filters.category:
            query = query.where(Product.category == filters.category)

        if filters.min_price is not None:
            query = query.where(Product.price >= filters.min_price)

        if filters.max_price is not None:
            query = query.where(Product.price <= filters.max_price)

        if filters.available:
            query = query.where(Product.available > 0)

        cnt_query = select(func.count()).select_from(query.subquery())
        total_items = await self.session.scalar(cnt_query)

        if not total_items:
            return [], 0

        query = query.order_by(Product.id).limit(filters.limit).offset(filters.offset)
        result = await self.session.execute(query)
        data = result.all()

        items = []
        for product, market in data:
            items.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'category': product.category,
                'available': product.available,
                'market': {
                    'marketId': market.marketId,
                    'name': market.name
                }
            })

        return items, total_items


    async def get_product_by_id(self, product_id: UUID) -> dict | None:
        query = select(Product, Market).join(Market, Market.marketId == Product.marketId).where(Product.id == product_id)
        result = await self.session.execute(query)

        return result.first()



