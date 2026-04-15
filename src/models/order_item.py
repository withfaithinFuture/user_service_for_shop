from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base_service import Base


class OrderItems(Base):
    __tablename__ = "OrderItems"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    orderId: Mapped[UUID] = mapped_column(
        sa.ForeignKey("orders.orderId", ondelete="CASCADE"), nullable=False
    )
    orderMarketId: Mapped[UUID] = mapped_column(
        ForeignKey("order_markets.id"), default=uuid4
    )
    productId: Mapped[UUID] = mapped_column(sa.UUID, nullable=False)
    quantity: Mapped[int] = mapped_column(sa.INT)
    priceAtPurchase: Mapped[Decimal] = mapped_column(sa.DECIMAL(10, 2))

    order = relationship("Order", back_populates="order_items")
    order_market = relationship("OrderMarket", back_populates="order_items")
