"""add tiss fields to patients clean

Revision ID: add_tiss_patients_clean
Revises: add_prestadores_clean
Create Date: 2025-11-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'add_tiss_patients_clean'
down_revision = 'add_prestadores_clean'
branch_labels = None
depends_on = None

def upgrade():
    # Adicionar campos TISS em patients
    op.add_column('patients', sa.Column('numero_carteira', sa.String(length=20), nullable=True))
    op.add_column('patients', sa.Column('validade_carteira', sa.Date(), nullable=True))
    op.add_column('patients', sa.Column('operadora_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('patients', sa.Column('cns', sa.String(length=15), nullable=True))
    op.add_column('patients', sa.Column('nome_mae', sa.String(length=200), nullable=True))
    
    # Criar índices
    op.create_index(op.f('ix_patients_numero_carteira'), 'patients', ['numero_carteira'], unique=False)
    op.create_index(op.f('ix_patients_cns'), 'patients', ['cns'], unique=False)
    
    # Criar foreign key
    op.create_foreign_key('fk_patients_operadora', 'patients', 'tiss_operadoras', ['operadora_id'], ['id'])

def downgrade():
    op.drop_constraint('fk_patients_operadora', 'patients', type_='foreignkey')
    op.drop_index(op.f('ix_patients_cns'), table_name='patients')
    op.drop_index(op.f('ix_patients_numero_carteira'), table_name='patients')
    op.drop_column('patients', 'nome_mae')
    op.drop_column('patients', 'cns')
    op.drop_column('patients', 'operadora_id')
    op.drop_column('patients', 'validade_carteira')
    op.drop_column('patients', 'numero_carteira')
