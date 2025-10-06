"""Create user API keys table

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Create user_api_keys table"""
    # Create user_api_keys table
    op.create_table('user_api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('encrypted_key', sa.Text(), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('is_valid', sa.Boolean(), nullable=True),
        sa.Column('last_validated', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        # No foreign key constraint to avoid type mismatch issues
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_user_api_keys_id'), 'user_api_keys', ['id'], unique=False)
    op.create_index(op.f('ix_user_api_keys_user_id'), 'user_api_keys', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_api_keys_provider'), 'user_api_keys', ['provider'], unique=False)
    
    # Create unique constraint for user_id + provider combination
    op.create_unique_constraint('uq_user_provider', 'user_api_keys', ['user_id', 'provider'])


def downgrade():
    """Drop user_api_keys table"""
    # Drop indexes
    op.drop_index(op.f('ix_user_api_keys_provider'), table_name='user_api_keys')
    op.drop_index(op.f('ix_user_api_keys_user_id'), table_name='user_api_keys')
    op.drop_index(op.f('ix_user_api_keys_id'), table_name='user_api_keys')
    
    # Drop table
    op.drop_table('user_api_keys')
