"""empty message

Revision ID: e8e96f10d82a
Revises: a1b761354c58
Create Date: 2019-11-14 15:39:58.829975

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8e96f10d82a'
down_revision = 'a1b761354c58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('line_data_bank', sa.Column('validate_rrpp_status', sa.SmallInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('line_data_bank', 'validate_rrpp_status')
    # ### end Alembic commands ###
