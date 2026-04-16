from datetime import datetime, timezone
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base_service import Base


class UserToken(Base):
    __tablename__ = "user_tokens"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    userId: Mapped[UUID] = mapped_column(
        sa.ForeignKey("users.userId", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = mapped_column(sa.String, index=True)
    expiresAt: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True))
    createdAt: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
