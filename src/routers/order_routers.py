from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette import status

from logreg.security import get_current_user
from src.app.dependencies import get_order_service
from src.models.user import User
from src.schemas.order_schemas import (
    CreateOrderRequestSchema,
    CreateOrderResponseSchema,
)
from src.services.order_service import OrderService

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post(
    "/",
    response_model=CreateOrderResponseSchema,
    status_code=status.HTTP_201_CREATED,
    description="Создание нового заказа из текущей корзины юзера",
)
async def create_order(
    data: CreateOrderRequestSchema,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):

    return await order_service.create_order_service(
        user_id=current_user.userId, order_data=data
    )


@router.get("/", description="Возвращение списка заказов юзера с пагинацией")
async def get_user_orders(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=10, le=50, description="Количество заказов на странице"),
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):

    return await order_service.get_user_orders_service(
        user_id=current_user.userId, page=page, limit=limit
    )


@router.get("/{order_id}", description="Возвращение полной информации о заказе")
async def get_order_details(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):

    return await order_service.get_order_details_service(
        user_id=current_user.userId, order_id=order_id
    )
