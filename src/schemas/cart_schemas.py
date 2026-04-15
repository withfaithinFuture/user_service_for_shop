from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AddToCartRequestSchema(BaseModel):
    productId: UUID
    quantity: int = Field(
        gt=0, description="Количество товара для добавления в корзину"
    )

    model_config = ConfigDict(from_attributes=True)


class AddToCartResponseSchema(BaseModel):
    success: bool
    cartCount: int


class CartMarketSchema(BaseModel):
    marketId: UUID
    marketName: str

    model_config = ConfigDict(from_attributes=True)


class CartItemResponseSchema(BaseModel):
    productId: UUID
    name: str
    price: float
    available: int
    quantity: int
    img: str
    market: CartMarketSchema | None = None

    model_config = ConfigDict(from_attributes=True)


class UpdateCartItemRequestSchema(BaseModel):
    productId: UUID
    quantity: int = Field(gt=0, description="Новое количество товара в корзине")


class UpdateCartItemResponseSchema(BaseModel):
    success: bool
    cartCount: int
    totalPrice: float


class DeleteCartItemResponseSchema(BaseModel):
    success: bool
    cartCount: int
    totalPrice: float


class CartResponseSchema(BaseModel):
    items: list[CartItemResponseSchema]
    totalPrice: float
