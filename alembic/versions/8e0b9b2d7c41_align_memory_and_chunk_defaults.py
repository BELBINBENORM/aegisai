"""align nullable compatibility fields

Revision ID: 8e0b9b2d7c41
Revises: c97e5631a50f
"""
from alembic import op

revision = "8e0b9b2d7c41"
down_revision = "c97e5631a50f"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("memories", "session_id", nullable=True)
    op.alter_column("document_chunks", "session_id", nullable=True)
    op.alter_column("document_chunks", "search_text", nullable=True)


def downgrade():
    op.alter_column("document_chunks", "search_text", nullable=False)
    op.alter_column("document_chunks", "session_id", nullable=False)
    op.alter_column("memories", "session_id", nullable=False)
