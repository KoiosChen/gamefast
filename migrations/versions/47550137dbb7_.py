"""empty message

Revision ID: 47550137dbb7
Revises: 4c9dd90e82b2
Create Date: 2019-11-23 18:24:40.924432

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '47550137dbb7'
down_revision = '4c9dd90e82b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mpls', 'ip')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mpls', sa.Column('ip', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('mpls_ibfk_1', 'mpls', 'ip_manager', ['ip'], ['id'])
    op.create_index('ix_mpls_ip', 'mpls', ['ip'], unique=False)
    # ### end Alembic commands ###
