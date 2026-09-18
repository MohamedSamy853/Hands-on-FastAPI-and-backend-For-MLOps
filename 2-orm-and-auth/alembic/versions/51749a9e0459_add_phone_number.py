"""add phone number

Revision ID: 51749a9e0459
Revises: 
Create Date: 2026-09-12 22:47:54.310749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '51749a9e0459'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(sa.table(), sa.Column("phone_number" , sa.String())) 


def downgrade() -> None:
    """Downgrade schema."""
    #op.remove_column

