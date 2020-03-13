"""empty message

Revision ID: 74efa1bb4ff1
Revises: db02fe5d6a74
Create Date: 2020-01-05 21:29:28.801090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74efa1bb4ff1'
down_revision = 'db02fe5d6a74'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_line_data_bank_create_time'), 'line_data_bank', ['create_time'], unique=False)
    op.create_index(op.f('ix_line_data_bank_line_operator'), 'line_data_bank', ['line_operator'], unique=False)
    op.create_index(op.f('ix_line_data_bank_line_stop_time'), 'line_data_bank', ['line_stop_time'], unique=False)
    op.create_index(op.f('ix_line_data_bank_operate_time'), 'line_data_bank', ['operate_time'], unique=False)
    op.create_index(op.f('ix_line_data_bank_parent_id'), 'line_data_bank', ['parent_id'], unique=False)
    op.create_index(op.f('ix_line_data_bank_platform'), 'line_data_bank', ['platform'], unique=False)
    op.create_index(op.f('ix_line_data_bank_validate_rrpp_status'), 'line_data_bank', ['validate_rrpp_status'], unique=False)
    op.create_index(op.f('ix_platforms_status'), 'platforms', ['status'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_platforms_status'), table_name='platforms')
    op.drop_index(op.f('ix_line_data_bank_z_e'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_z_chain'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_validate_rrpp_status'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_platform'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_parent_id'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_operate_time'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_memo'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_main_route'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_main_e'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_line_stop_time'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_line_operator'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_line_desc'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_create_time'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_backup_route'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_a_e'), table_name='line_data_bank')
    op.drop_index(op.f('ix_line_data_bank_a_chain'), table_name='line_data_bank')
    op.drop_index(op.f('ix_ip_manager_isp'), table_name='ip_manager')
    op.drop_index(op.f('ix_ip_manager_ip_group'), table_name='ip_manager')
    op.drop_index(op.f('ix_ip_manager_gateway'), table_name='ip_manager')
    op.drop_index(op.f('ix_ip_manager_dns'), table_name='ip_manager')
    op.drop_index(op.f('ix_ip_manager_desc'), table_name='ip_manager')
    op.drop_index(op.f('ix_ip_manager_available_ip'), table_name='ip_manager')
    op.drop_index(op.f('ix_ip_group_group_name'), table_name='ip_group')
    op.drop_index(op.f('ix_dns_manager_dns_role'), table_name='dns_manager')
    op.drop_index(op.f('ix_contacts_type'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_phoneNumber'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_name'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_email'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_address'), table_name='contacts')
    # ### end Alembic commands ###
