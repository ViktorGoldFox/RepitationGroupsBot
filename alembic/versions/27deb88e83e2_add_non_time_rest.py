"""add non time rest

Revision ID: 27deb88e83e2
Revises: 20260628_add_rest_display_columns
Create Date: 2026-06-28 22:03:15.279449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27deb88e83e2'
down_revision: Union[str, Sequence[str], None] = '20260628_add_rest_display_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
