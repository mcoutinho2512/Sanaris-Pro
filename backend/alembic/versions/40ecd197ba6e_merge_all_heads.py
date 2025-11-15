"""merge_all_heads

Revision ID: 40ecd197ba6e
Revises: fix_varchar_to_uuid, convert_all_ids_uuid
Create Date: 2025-11-14 20:20:58.565616

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40ecd197ba6e'
down_revision = ('fix_varchar_to_uuid', 'convert_all_ids_uuid')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
