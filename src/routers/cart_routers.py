from uuid import UUID
from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status
from src.services.cart_service import CartService
from src.schemas.cart_schemas import (
    AddToCartResponseSchema,
    CartResponseSchema,
    UpdateCartItemResponseSchema,
    UpdateCartItemRequestSchema,
    DeleteCartItemResponseSchema,
    AddToCartRequestSchema,
)
from logreg.security import get_current_user
from src.models.user import User
from src.app.dependencies import get_cart_service

router = APIRouter(prefix="/api/v1/cart", tags=["cart"])


@router.post(
    "/",
    response_model=AddToCartResponseSchema,
    status_code=status.HTTP_201_CREATED,
    description="Добавление товара в корзину юзера",
)
async def add_to_cart(
    data: AddToCartRequestSchema,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):

    return await cart_service.add_to_cart_service(
        user_id=current_user.userId, data=data
    )


@router.get(
    "/",
    response_model=CartResponseSchema,
    description="Возвращение содержимого корзины юзера",
)
async def get_cart(
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):

    return await cart_service.get_cart_service(user_id=current_user.userId)


@router.patch(
    "/{product_id}",
    response_model=UpdateCartItemResponseSchema,
    description="Изменение количества указанного товара в корзине",
)
async def update_cart_item(
    data: UpdateCartItemRequestSchema,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):

    return await cart_service.update_cart_item_service(
        user_id=current_user.userId, data=data
    )


@router.delete(
    "/item/{product_id}",
    response_model=DeleteCartItemResponseSchema,
    description="Удаляние товара из корзины юзера",
)
async def delete_cart_item(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):

    return await cart_service.delete_cart_item_service(
        user_id=current_user.userId, product_id=product_id
    )
