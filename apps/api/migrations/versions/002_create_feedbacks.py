"""create feedbacks table.

Revision ID: 002
Revises: 001
Create Date: 2026-03-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "feedbacks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(36),
            sa.ForeignKey("sessions.id"),
            nullable=False,
        ),
        sa.Column(
            "message_id", sa.String(36), nullable=False, server_default=sa.text("''")
        ),
        sa.Column("rating", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_index("ix_feedbacks_session_id", "feedbacks", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_feedbacks_session_id", table_name="feedbacks")
    op.drop_table("feedbacks")
