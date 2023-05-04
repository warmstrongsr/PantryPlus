"""empty message

Revision ID: 660ab7046197
Revises: 3e9e41e312b1
Create Date: 2023-04-29 14:35:53.238058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '660ab7046197'
down_revision = '3e9e41e312b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.add_column(sa.Column('api_recipe', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.drop_column('api_recipe')

    # ### end Alembic commands ###
