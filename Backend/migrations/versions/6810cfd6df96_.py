"""empty message

Revision ID: 6810cfd6df96
Revises: e719489ca670
Create Date: 2023-04-26 20:31:34.753063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6810cfd6df96'
down_revision = 'e719489ca670'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.add_column(sa.Column('link', sa.String(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.drop_column('link')

    # ### end Alembic commands ###