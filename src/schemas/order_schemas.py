from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from src.schemas.pagination_schemas import PaginationSchema
from src.models.order import OrderStatus


class CreateOrderRequestSchema(BaseModel):
    deliveryAddress: str = Field(min_length=5, description='Адрес доставки')
    deliveryCity: str = Field(min_length=2, description='Город доставки')
    phone: str = Field(min_length=10, description='Номер телефона для связи')
    deliveryComment: str | None = Field(description='Комментарий к доставке (необязательно)')


class OrderItemDetailSchema(BaseModel):
    productId: UUID
    name: str
    quantity: int
    buy_price: float


class OrderMarketDetailItemSchema(BaseModel):
    marketId: UUID
    marketName: str
    status: str
    totalPrice: float
    items: list[OrderItemDetailSchema]


class OrderDetailResponseSchema(BaseModel):
    orderId: UUID
    createdAt: str
    status: str
    totalPrice: float
    deliveryAddress: str
    deliveryCity: str
    markets: list[OrderMarketDetailItemSchema]

    model_config = ConfigDict(from_attributes=True)


class CreateOrderResponseSchema(BaseModel):
    success: bool
    orderId: UUID


class OrderHistoryItemSchema(BaseModel):
    orderId: UUID
    createdAt: str
    status: OrderStatus
    totalPrice: float
    totalItems: int

    model_config = ConfigDict(from_attributes=True)


class OrderHistoryResponseSchema(BaseModel):
    orders: list[OrderHistoryItemSchema]
    pagination: PaginationSchema
