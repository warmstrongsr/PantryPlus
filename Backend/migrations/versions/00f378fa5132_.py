"""empty message

Revision ID: 00f378fa5132
Revises: 
Create Date: 2023-05-05 18:54:51.341053

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '00f378fa5132'
down_revision = 'baf968b21d3e'
branch_labels = None
depends_on = None


def upgrade():
    # update the new column with dummy values
    op.execute("UPDATE favorites SET date_favorited = '2022-01-01'")

def downgrade():
    # update the new column with dummy values
    op.execute("UPDATE favorites SET date_favorited = '2022-01-01'")
