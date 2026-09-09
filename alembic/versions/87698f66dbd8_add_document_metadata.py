"""add document metadata

Revision ID: 87698f66dbd8
Revises: a0609d96ba01
Create Date: 2026-09-09 12:19:27.955285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87698f66dbd8'
down_revision: Union[str, Sequence[str], None] = 'a0609d96ba01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("metadata", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "metadata")