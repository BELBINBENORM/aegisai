"""add document chunk embeddings

Revision ID: a0609d96ba01
Revises: ee8e02e89250
Create Date: 2026-09-09 06:53:22.667957

"""
from typing import Sequence, Union
from pgvector.sqlalchemy import Vector

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0609d96ba01'
down_revision: Union[str, Sequence[str], None] = 'ee8e02e89250'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "document_chunks",
        sa.Column(
            "embedding",
            Vector(768),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("document_chunks", "embedding")