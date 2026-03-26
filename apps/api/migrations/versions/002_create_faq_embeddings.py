"""create faq_embeddings table.

Revision ID: 002
Revises: 001
Create Date: 2026-03-25

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "faq_embeddings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_type", sa.String(50), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_table("faq_embeddings")
