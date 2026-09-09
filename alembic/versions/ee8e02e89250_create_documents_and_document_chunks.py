"""create documents and document chunks

Revision ID: ee8e02e89250
Revises: 3e6d3808c5b3
Create Date: 2026-09-09 01:31:56.361862

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ee8e02e89250"
down_revision: Union[str, Sequence[str], None] = "3e6d3808c5b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=True),
    )

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("document_chunks")
    op.drop_table("documents")
    