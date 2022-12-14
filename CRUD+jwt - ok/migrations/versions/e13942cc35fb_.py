"""empty message

Revision ID: e13942cc35fb
Revises: c711379f0f0f
Create Date: 2022-08-04 13:05:29.588812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e13942cc35fb'
down_revision = 'c711379f0f0f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('usuario', 'email2')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usuario', sa.Column('email2', sa.VARCHAR(length=100), nullable=True))
    # ### end Alembic commands ###
