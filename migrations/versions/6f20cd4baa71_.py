"""empty message

Revision ID: 6f20cd4baa71
Revises: c1cc5dae3f50
Create Date: 2019-11-23 19:12:32.649696

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f20cd4baa71'
down_revision = 'c1cc5dae3f50'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mpls', sa.Column('local_route', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'mpls', 'ip_group', ['local_route'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'mpls', type_='foreignkey')
    op.drop_column('mpls', 'local_route')
    # ### end Alembic commands ###
