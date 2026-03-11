from uuid import uuid4, UUID
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base_service import Base


class CartItems(Base):
    __tablename__ = 'cartItems'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    cartId: Mapped[UUID] = mapped_column(ForeignKey('cart.id'), default=uuid4)
    productId: Mapped[UUID] = mapped_column(ForeignKey('products.id'), default=uuid4)
    quantity: Mapped[int] = mapped_column(sa.INT)


    cart = relationship('Cart', back_populates='cart_items')
    product = relationship('Product', back_populates='cart_items')