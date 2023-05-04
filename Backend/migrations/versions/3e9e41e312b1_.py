"""empty message

Revision ID: 3e9e41e312b1
Revises: d478ed47d0ff
Create Date: 2023-04-29 13:27:09.293324

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e9e41e312b1'
down_revision = 'd478ed47d0ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('api_recipe', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('api_recipe')

    # ### end Alembic commands ###
