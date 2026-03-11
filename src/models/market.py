from datetime import datetime, timezone, date
from uuid import uuid4, UUID
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base_service import Base


class Market(Base):
    __tablename__ = 'market'

    marketId: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    userId: Mapped[UUID] = mapped_column(sa.ForeignKey('users.userId'), nullable=False, index=True)
    marketName: Mapped[str] = mapped_column(sa.String(), unique=True)
    description: Mapped[None | str] = mapped_column(sa.String())
    createdAt: Mapped[date] = mapped_column(sa.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))


    user = relationship('User', back_populates='market', lazy='selectin')
    product = relationship('Product', back_populates='market', lazy='selectin')
    order_market = relationship('OrderMarket', back_populates='market')