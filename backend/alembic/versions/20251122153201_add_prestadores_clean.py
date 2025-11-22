"""add prestadores clean

Revision ID: add_prestadores_clean
Revises: 831c906e4015
Create Date: 2025-11-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'add_prestadores_clean'
down_revision = '831c906e4015'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('prestadores',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_prestador', sa.String(length=20), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('razao_social', sa.String(length=200), nullable=True),
        sa.Column('cnpj', sa.String(length=18), nullable=True),
        sa.Column('cpf', sa.String(length=14), nullable=True),
        sa.Column('crm', sa.String(length=20), nullable=True),
        sa.Column('uf_crm', sa.String(length=2), nullable=True),
        sa.Column('especialidade', sa.String(length=100), nullable=True),
        sa.Column('codigo_cbo', sa.String(length=10), nullable=True),
        sa.Column('cnes', sa.String(length=20), nullable=True),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('cep', sa.String(length=10), nullable=True),
        sa.Column('logradouro', sa.String(length=200), nullable=True),
        sa.Column('numero', sa.String(length=10), nullable=True),
        sa.Column('complemento', sa.String(length=100), nullable=True),
        sa.Column('bairro', sa.String(length=100), nullable=True),
        sa.Column('cidade', sa.String(length=100), nullable=True),
        sa.Column('estado', sa.String(length=2), nullable=True),
        sa.Column('banco_codigo', sa.String(length=10), nullable=True),
        sa.Column('banco_agencia', sa.String(length=10), nullable=True),
        sa.Column('banco_conta', sa.String(length=20), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cnpj'),
        sa.UniqueConstraint('cpf')
    )
    op.create_index(op.f('ix_prestadores_nome'), 'prestadores', ['nome'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_prestadores_nome'), table_name='prestadores')
    op.drop_table('prestadores')
