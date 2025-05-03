"""Initial migration

Revision ID: 001
Create Date: 2025-05-03

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create loans table
    op.create_table(
        'loans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('issue_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('return_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='ACTIVE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_loans_id'), 'loans', ['id'], unique=False)
    op.create_index(op.f('ix_loans_user_id'), 'loans', ['user_id'], unique=False)
    op.create_index(op.f('ix_loans_book_id'), 'loans', ['book_id'], unique=False)
    op.create_index(op.f('ix_loans_status'), 'loans', ['status'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_loans_status'), table_name='loans')
    op.drop_index(op.f('ix_loans_book_id'), table_name='loans')
    op.drop_index(op.f('ix_loans_user_id'), table_name='loans')
    op.drop_index(op.f('ix_loans_id'), table_name='loans')
    
    # Drop loans table
    op.drop_table('loans')
