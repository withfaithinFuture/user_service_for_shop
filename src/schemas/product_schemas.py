from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ProductInternalItemSchema(BaseModel):
    id: UUID
    name: str
    price: Decimal
    available: int
    marketId: UUID


class ProductInternalListResponse(BaseModel):
    items: list[ProductInternalItemSchema]
