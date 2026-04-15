from datetime import date, datetime, timezone
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base_service import Base


class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    userId: Mapped[UUID] = mapped_column(
        sa.ForeignKey("users.userId"), nullable=False, unique=True
    )
    createdAt: Mapped[date] = mapped_column(
        sa.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="cart")
    cart_items = relationship(
        "CartItems",
        back_populates="cart",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
