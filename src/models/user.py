from datetime import datetime, timezone
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base_service import Base


class User(Base):
    __tablename__ = "users"

    userId: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    login: Mapped[str] = mapped_column(sa.String(), unique=True)
    passwordHash: Mapped[str] = mapped_column(sa.String(), nullable=False)
    firstName: Mapped[str] = mapped_column(sa.String())
    lastName: Mapped[str] = mapped_column(sa.String())
    patronymic: Mapped[None | str] = mapped_column(sa.String())
    dateOfBirth: Mapped[datetime] = mapped_column(sa.Date)
    city: Mapped[str] = mapped_column(sa.String())
    telegram: Mapped[None | str] = mapped_column(sa.String(), unique=True)
    telegramChatId: Mapped[None | str] = mapped_column(sa.String(), unique=True)
    isSeller: Mapped[bool] = mapped_column(sa.Boolean, index=True)
    createdAt: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    cart = relationship("Cart", back_populates="user", uselist=False)  # 1k1
    orders = relationship("Order", back_populates="user", lazy="selectin")
