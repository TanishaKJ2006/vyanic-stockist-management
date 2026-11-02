"""Allow assignment-compatible viewer accounts while preserving stockists.

Revision ID: 20261102_02
Revises: 20261102_01
Create Date: 2026-11-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20261102_02"
down_revision: Union[str, None] = "20261102_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role IN ('admin', 'viewer', 'stockist')",
    )


def downgrade() -> None:
    bind = op.get_bind()
    viewer_count = bind.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE role = 'viewer'")
    ).scalar_one()
    if viewer_count:
        raise RuntimeError(
            "Cannot remove the viewer role while viewer accounts still exist."
        )

    op.drop_constraint("ck_users_role", "users", type_="check")
    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role IN ('admin', 'stockist')",
    )
