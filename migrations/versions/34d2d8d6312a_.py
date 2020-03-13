"""empty message

Revision ID: 34d2d8d6312a
Revises: ffe8d0bc974b
Create Date: 2019-11-18 15:20:58.576601

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34d2d8d6312a'
down_revision = 'ffe8d0bc974b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('desc', sa.String(length=200), nullable=True),
    sa.Column('file_path', sa.String(length=200), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('line_order', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['line_order'], ['line_data_bank.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_files_file_path'), 'files', ['file_path'], unique=False)
    op.create_index(op.f('ix_files_name'), 'files', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_files_name'), table_name='files')
    op.drop_index(op.f('ix_files_file_path'), table_name='files')
    op.drop_table('files')
    # ### end Alembic commands ###
