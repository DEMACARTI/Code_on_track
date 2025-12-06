"""init schema

Revision ID: 0001
Revises: 
Create Date: 2025-12-01 13:38:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'VIEWER', 'SERVICE', name='userrole', native_enum=False), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    # Vendors
    op.create_table('vendors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('contact_info', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Items
    op.create_table('items',
        sa.Column('uid', sa.String(), nullable=False),
        sa.Column('component_type', sa.String(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=True),
        sa.Column('lot_no', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('uid')
    )
    op.create_index(op.f('ix_items_status'), 'items', ['status'], unique=False)

    # Item Events
    op.create_table('item_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_uid', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('performed_by', sa.String(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['item_uid'], ['items.uid'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )

    # Engravings
    op.create_table('engravings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('item_uid', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('raw_payload', sa.JSON(), nullable=True),
        sa.Column('orphan', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['item_uid'], ['items.uid'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id')
    )

    # Audit Logs
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('target_id', sa.String(), nullable=False),
        sa.Column('diff', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('engravings')
    op.drop_table('item_events')
    op.drop_index(op.f('ix_items_status'), table_name='items')
    op.drop_table('items')
    op.drop_table('vendors')
    op.drop_table('users')
    sa.Enum(name='userrole').drop(op.get_bind())
