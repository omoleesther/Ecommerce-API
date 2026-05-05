"""added payment_reference

Revision ID: 3a00b397097e
Revises: 685a4a180e5f
Create Date: 2026-04-09 14:56:34.408016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a00b397097e'
down_revision: Union[str, Sequence[str], None] = '685a4a180e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
