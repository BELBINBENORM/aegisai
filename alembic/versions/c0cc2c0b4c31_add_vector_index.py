"""add vector index

Revision ID: c0cc2c0b4c31
Revises: ae6f394fd601
Create Date: 2026-09-10 22:19:26.709075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0cc2c0b4c31'
down_revision: Union[str, Sequence[str], None] = 'ae6f394fd601'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw
        """
    )
