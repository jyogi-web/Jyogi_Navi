"""create users table.

Revision ID: 004
Revises: 003
Create Date: 2026-03-27

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("discord_user_id", sa.String(64), nullable=False, unique=True),
        sa.Column("user_name", sa.String(64), nullable=False, server_default=""),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "MEMBER", name="userrole"),
            nullable=False,
            server_default="MEMBER",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_users_discord_user_id", "users", ["discord_user_id"])


def downgrade() -> None:
    op.drop_index("ix_users_discord_user_id", table_name="users")
    op.drop_table("users")
