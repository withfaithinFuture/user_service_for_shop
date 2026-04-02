from uuid import UUID
from pydantic import BaseModel
from decimal import Decimal


class ProductInternalItemSchema(BaseModel):
    id: UUID
    name: str
    price: Decimal
    available: int
    marketId: UUID


class ProductInternalListResponse(BaseModel):
    items: list[ProductInternalItemSchema]