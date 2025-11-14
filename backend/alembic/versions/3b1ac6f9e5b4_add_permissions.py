"""Add permissions system

Revision ID: 3b1ac6f9e5b4
Revises: 
Create Date: 2025-11-14 16:13:27.306599

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# revision identifiers
revision = '3b1ac6f9e5b4'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Tabela de permissões disponíveis
    op.create_table(
        'permissions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.String(255)),
        sa.Column('module', sa.String(50)),
        sa.Column('action', sa.String(50)),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
    )
    
    # Tabela de permissões por usuário
    op.create_table(
        'user_permissions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('permission_id', UUID(as_uuid=True), sa.ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('granted_by_id', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('granted_at', sa.DateTime, default=datetime.utcnow)
    )
    
    # Índices
    op.create_index('idx_user_permissions_user', 'user_permissions', ['user_id'])
    op.create_index('idx_permissions_module', 'permissions', ['module'])

def downgrade():
    op.drop_table('user_permissions')
    op.drop_table('permissions')
