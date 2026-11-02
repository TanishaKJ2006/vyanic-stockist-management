"""Create the initial Vyanic stockist schema.

Revision ID: 20261102_01
Revises:
Create Date: 2026-11-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20261102_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.String(length=24),
            server_default="stockist",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "role IN ('admin', 'stockist')",
            name="ck_users_role",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_users_role", "users", ["role"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("sku_code", sa.String(length=64), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "stock_quantity",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("price >= 0", name="ck_products_price_nonnegative"),
        sa.CheckConstraint(
            "stock_quantity >= 0",
            name="ck_products_stock_quantity_nonnegative",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku_code", name="uq_products_sku_code"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_products_category", "products", ["category"], unique=False)

    op.create_table(
        "stockists",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("contact_email", sa.String(length=255), nullable=False),
        sa.Column("contact_phone", sa.String(length=32), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_stockists_city", "stockists", ["city"], unique=False)
    op.create_index(
        "ix_stockists_contact_email",
        "stockists",
        ["contact_email"],
        unique=False,
    )

    op.create_table(
        "stockist_pincodes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stockist_id", sa.Integer(), nullable=False),
        sa.Column("pincode", sa.String(length=16), nullable=False),
        sa.Column("state", sa.String(length=120), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["stockist_id"],
            ["stockists.id"],
            name="fk_stockist_pincodes_stockist_id_stockists",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pincode", name="uq_stockist_pincodes_pincode"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )

def downgrade() -> None:
    op.drop_table("stockist_pincodes")
    op.drop_index("ix_stockists_contact_email", table_name="stockists")
    op.drop_index("ix_stockists_city", table_name="stockists")
    op.drop_table("stockists")
    op.drop_index("ix_products_category", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_table("users")
