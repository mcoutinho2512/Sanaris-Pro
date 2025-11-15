"""fix id types to uuid

Revision ID: fix_varchar_to_uuid
Revises: 05c060e5cc60
Create Date: 2025-01-14

"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_varchar_to_uuid'
down_revision = '05c060e5cc60'

def upgrade():
    # Converter id de VARCHAR para UUID nas tabelas principais
    tables = ['patients', 'appointments', 'medical_records', 'prescriptions', 'prescription_items']
    
    for table in tables:
        try:
            op.execute(f'ALTER TABLE {table} ALTER COLUMN id TYPE UUID USING id::uuid')
            print(f'✅ Convertido {table}.id para UUID')
        except Exception as e:
            print(f'⚠️ Erro ao converter {table}: {e}')

def downgrade():
    tables = ['patients', 'appointments', 'medical_records', 'prescriptions', 'prescription_items']
    for table in tables:
        try:
            op.execute(f'ALTER TABLE {table} ALTER COLUMN id TYPE VARCHAR(36) USING id::varchar')
        except:
            pass
