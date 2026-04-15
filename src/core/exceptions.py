import datetime as dt
import logging
from uuid import UUID

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, object_id: UUID, object_type: str):
        self.object_id = object_id
        self.object_type = object_type

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"{self.object_type}_not_found",
                "message": f"{self.object_type} with id={self.object_id} was not found",
                f"{self.object_type}_id": str(self.object_id),
            },
        )


class NotEnoughStockError(HTTPException):
    def __init__(self, product_id: UUID, available: int, requested: int):
        self.product_id = product_id
        self.available = available
        self.requested = requested

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "not_enough_stock",
                "message": f"Product with id={self.product_id} has only {self.available} items available, but {self.requested} were requested",
                "product_id": str(self.product_id),
                "available": self.available,
                "requested": self.requested,
            },
        )
