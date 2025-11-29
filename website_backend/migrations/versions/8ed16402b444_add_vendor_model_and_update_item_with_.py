"""Add Vendor model and update Item with vendor relationship (batch mode)

Revision ID: 8ed16402b444
Revises: 857d785aafd3
Create Date: 2025-11-29 15:06:28.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ed16402b444'
down_revision = '857d785aafd3'
branch_labels = None
depends_on = None


def upgrade():
    # Create vendors table
    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create item_vendor association table
    op.create_table(
        'item_vendor',
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('item_id', 'vendor_id')
    )
    op.create_index('idx_item_vendor', 'item_vendor', ['item_id', 'vendor_id'], unique=True)

    # Add vendor_id to items table using batch mode
    with op.batch_alter_table('items') as batch_op:
        batch_op.add_column(sa.Column('vendor_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_items_vendor_id',
            'vendors',
            ['vendor_id'],
            ['id'],
            ondelete='SET NULL'
        )


def downgrade():
    # Drop foreign key and column in batch mode
    with op.batch_alter_table('items') as batch_op:
        batch_op.drop_constraint('fk_items_vendor_id', type_='foreignkey')
        batch_op.drop_column('vendor_id')

    # Drop association table and vendors table
    op.drop_table('item_vendor')
    op.drop_table('vendors')
