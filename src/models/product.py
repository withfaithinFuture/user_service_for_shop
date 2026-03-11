from datetime import datetime, timezone, date
import enum
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base_service import Base
from decimal import Decimal


class ProductCategory(enum.Enum):
    electronics = "electronics"
    clothing = "clothing"
    food = "food"
    home = "home"
    beauty = "beauty"
    sports = "sports"
    books = "books"
    other = "other"


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    marketId: Mapped[UUID] = mapped_column(ForeignKey('market.marketId'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(sa.String())
    description: Mapped[str] = mapped_column(sa.String())
    category: Mapped[ProductCategory] = mapped_column(Enum(ProductCategory), index=True)
    price: Mapped[Decimal] = mapped_column(sa.DECIMAL(10, 2))
    img: Mapped[str] = mapped_column(sa.String())
    available: Mapped[int] = mapped_column(sa.INT)
    createdAt: Mapped[date] = mapped_column(sa.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))


    market = relationship('Market', back_populates='product')
    cart_items = relationship('CartItems', back_populates='product', lazy='selectin')
    order_items = relationship('OrderItems', back_populates='product')