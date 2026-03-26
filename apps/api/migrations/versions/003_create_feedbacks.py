"""create feedbacks table.

Revision ID: 003
Revises: 002
Create Date: 2026-03-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
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
        sa.Column("rating", sa.String(10), nullable=False),
        sa.Column("comment", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_feedbacks_session_id", "feedbacks", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_feedbacks_session_id", table_name="feedbacks")
    op.drop_table("feedbacks")
