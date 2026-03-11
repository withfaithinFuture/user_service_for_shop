from uuid import UUID
from fastapi import APIRouter
from fastapi.params import Query, Depends
from src.core.exceptions import NotFoundError
from src.app.dependencies import get_product_service
from src.services.product_service import ProductService
from src.schemas.product_schemas import ProductListResponseSchema, ProductFilterParams, ProductItemSchema


router = APIRouter(prefix="/api/products", tags=["products"])


@router.get('', response_model=ProductListResponseSchema)
async def get_products(filters_params: ProductFilterParams = Depends(), product_service: ProductService = Depends(get_product_service)):

    return await product_service.get_products_service(filters=filters_params)


@router.get('/{product_id}', response_model=ProductItemSchema)
async def get_product_by_id(product_id: UUID, product_service: ProductService = Depends(get_product_service)):
    result =  await product_service.get_product_by_id_service(product_id=product_id)
    if result is None:
        raise NotFoundError(object_id=product_id, object_type='Product')

    return result