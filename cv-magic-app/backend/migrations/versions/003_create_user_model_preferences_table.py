"""
Create user_model_preferences table

Revision ID: 003_create_user_model_preferences_table
Revises: 002_create_user_api_keys_table
Create Date: 2025-10-06
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_create_user_model_preferences_table'
down_revision = '002_create_user_api_keys_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user_model_preferences',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_unique_constraint('uq_user_model_preference_user', 'user_model_preferences', ['user_id'])


def downgrade() -> None:
    op.drop_constraint('uq_user_model_preference_user', 'user_model_preferences', type_='unique')
    op.drop_table('user_model_preferences')


