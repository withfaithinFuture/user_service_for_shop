import enum
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base_service import Base


class OrderStatus(enum.Enum):
    GENERATED = "generated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"


class Order(Base):
    __tablename__ = "orders"

    orderId: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    userId: Mapped[UUID] = mapped_column(sa.ForeignKey("users.userId"), nullable=False)
    totalPrice: Mapped[Decimal] = mapped_column(sa.DECIMAL(10, 2))
    deliveryAddress: Mapped[str] = mapped_column(sa.String())
    deliveryCity: Mapped[str] = mapped_column(sa.String())
    phone: Mapped[str] = mapped_column(sa.String())
    deliveryComment: Mapped[None | str] = mapped_column(sa.String())
    status: Mapped[OrderStatus] = mapped_column(
        sa.String, default=OrderStatus.GENERATED.value, nullable=False
    )
    createdAt: Mapped[date] = mapped_column(
        sa.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="orders")
    order_market = relationship("OrderMarket", back_populates="order", lazy="selectin")
    order_items = relationship("OrderItems", back_populates="order")

    __table_args__ = (
        sa.UniqueConstraint("orderId", "userId", name="unique_order_user"),
    )
