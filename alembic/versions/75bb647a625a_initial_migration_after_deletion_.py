"""initial_migration after deletion product market

Revision ID: 75bb647a625a
Revises: 3d4644498c2a
Create Date: 2026-04-01 01:22:49.941720

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "75bb647a625a"
down_revision: Union[str, Sequence[str], None] = "3d4644498c2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Удаляем внешние ключи
    op.drop_constraint(
        op.f("OrderItems_productId_fkey"), "OrderItems", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("cartItems_productId_fkey"), "cartItems", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("order_markets_marketId_fkey"), "order_markets", type_="foreignkey"
    )

    # 2. Удаляем индексы
    op.drop_index(op.f("ix_products_category"), table_name="products")
    op.drop_index(op.f("ix_products_marketId"), table_name="products")
    op.drop_index(op.f("ix_market_userId"), table_name="market")

    # 3. Удаляем таблицы в правильном порядке
    op.drop_table("OrderItems")
    op.drop_table("cartItems")
    op.drop_table("order_markets")
    op.drop_table("products")
    op.drop_table("market")


def downgrade() -> None:
    """Downgrade schema."""
    # Восстанавливаем в обратном порядке

    # Сначала market
    op.create_table(
        "market",
        sa.Column("marketId", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("userId", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("marketName", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("description", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "createdAt",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["userId"], ["users.userId"], name=op.f("market_userId_fkey")
        ),
        sa.PrimaryKeyConstraint("marketId", name=op.f("market_pkey")),
        sa.UniqueConstraint(
            "marketName",
            name=op.f("market_marketName_key"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
    )
    op.create_index(op.f("ix_market_userId"), "market", ["userId"], unique=False)

    # Потом products
    op.create_table(
        "products",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("marketId", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("description", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "category",
            postgresql.ENUM(
                "electronics",
                "clothing",
                "food",
                "home",
                "beauty",
                "sports",
                "books",
                "other",
                name="productcategory",
            ),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "price",
            sa.NUMERIC(precision=10, scale=2),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("img", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("available", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "createdAt",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["marketId"], ["market.marketId"], name=op.f("products_marketId_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("products_pkey")),
    )
    op.create_index(
        op.f("ix_products_marketId"), "products", ["marketId"], unique=False
    )
    op.create_index(
        op.f("ix_products_category"), "products", ["category"], unique=False
    )

    # Восстанавливаем внешние ключи
    op.create_foreign_key(
        op.f("order_markets_marketId_fkey"),
        "order_markets",
        "market",
        ["marketId"],
        ["marketId"],
    )
    op.create_foreign_key(
        op.f("cartItems_productId_fkey"), "cartItems", "products", ["productId"], ["id"]
    )
    op.create_foreign_key(
        op.f("OrderItems_productId_fkey"),
        "OrderItems",
        "products",
        ["productId"],
        ["id"],
    )
