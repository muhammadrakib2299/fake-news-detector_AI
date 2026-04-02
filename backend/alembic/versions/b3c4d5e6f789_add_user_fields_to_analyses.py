"""Add user_id and user_email columns to analyses

Revision ID: b3c4d5e6f789
Revises: a2b3c4d5e6f7
Create Date: 2026-04-02 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f789'
down_revision: Union[str, Sequence[str], None] = 'a2b3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user_id and user_email columns."""
    op.add_column('analyses', sa.Column('user_id', sa.String(255), nullable=True))
    op.add_column('analyses', sa.Column('user_email', sa.String(255), nullable=True))
    op.create_index('ix_analyses_user_id', 'analyses', ['user_id'])


def downgrade() -> None:
    """Remove user columns."""
    op.drop_index('ix_analyses_user_id', table_name='analyses')
    op.drop_column('analyses', 'user_email')
    op.drop_column('analyses', 'user_id')
