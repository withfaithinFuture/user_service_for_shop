import datetime
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID
from fastapi.params import Query
from pydantic import BaseModel, ConfigDict

from src.schemas.pagination_schemas import PaginationSchema
from src.models.product import ProductCategory


@dataclass
class ProductFilterParams:
    page: int = Query(1, ge=1, description='Номер страницы')
    limit: int = Query(12, ge=1, le=100, description='Количество товаров на странице')
    search: str | None = Query(None, description='Поиск по названию товара')
    category: str | None = Query(None, description='Фильтр по категории товара')
    min_price: float | None = Query(None, ge=0, description='Минимальная цена товара')
    max_price: float | None = Query(None, ge=0, description='Максимальная цена товара')
    available: bool | None = Query(None, description='Фильтр по наличию товара')


class MarketShortSchema(BaseModel):
    marketId: UUID
    marketName: str

    model_config = ConfigDict(from_attributes=True)


class ProductItemSchema(BaseModel):
    id: UUID
    name: str
    description: str
    category: ProductCategory
    price: Decimal
    img: str
    available: int
    createdAt: datetime.date

    market: MarketShortSchema

    model_config = ConfigDict(from_attributes=True)


class ProductListResponseSchema(BaseModel):
    items: list[ProductItemSchema]
    pagination: PaginationSchema