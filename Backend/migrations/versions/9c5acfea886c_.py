"""empty message

Revision ID: 9c5acfea886c
Revises: a975ed85d8ac
Create Date: 2023-05-08 03:36:11.786070
"Needed something to update"5.8.23
"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '9c5acfea886c'
down_revision = 'ddc73a8e8f0d'
branch_labels = None
depends_on = None


# define the new column
date_favorited = sa.Column(sa.DateTime())

def upgrade():
    # add the new column to the favorites table
    op.add_column('favorites', 'date_favorited', date_favorited)

    # update the new column with dummy values
    op.execute("UPDATE favorites SET date_favorited = '2022-01-01'")

def downgrade():
    # remove the new column from the favorites table
    op.drop_column('favorites', 'date_favorited')
