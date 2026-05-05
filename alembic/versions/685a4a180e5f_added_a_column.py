"""added a column

Revision ID: 685a4a180e5f
Revises: 04053494fe4a
Create Date: 2026-04-09 14:53:59.269732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '685a4a180e5f'
down_revision: Union[str, Sequence[str], None] = '04053494fe4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
