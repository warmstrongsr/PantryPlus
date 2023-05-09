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
    # add the new column to the favorites table
    op.add_column('favorites', sa.Column('date_favorited', sa.DateTime(), nullable=True))
    
    # set dummy data for existing rows
    op.execute("UPDATE favorites SET date_favorited = :date", {"date": datetime.utcnow()})


def downgrade():
    # remove the new column from the favorites table
    op.drop_column('favorites', 'date_favorited')
