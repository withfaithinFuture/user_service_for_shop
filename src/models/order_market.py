import datetime
import enum
from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base_service import Base


class OrderStatus(enum.Enum):
    GENERATED = "generated"
    CONFIRMED = "confirmed"
    PAID = "paid"
    DECLINED = "declined"
    COMPLETED = "completed"


class OrderMarket(Base):
    __tablename__ = "order_markets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    orderId: Mapped[UUID] = mapped_column(
        sa.ForeignKey("orders.orderId"), nullable=False
    )
    marketId: Mapped[UUID] = mapped_column(sa.UUID, nullable=False)
    totalPrice: Mapped[Decimal] = mapped_column(sa.DECIMAL(10, 2))
    status: Mapped[OrderStatus] = mapped_column(
        sa.String, default=OrderStatus.GENERATED.value, nullable=False
    )

    order = relationship("Order", back_populates="order_market")
    order_items = relationship("OrderItems", back_populates="order_market")

    __table_args__ = (
        sa.UniqueConstraint("orderId", "marketId", name="unique_order_market"),
    )
