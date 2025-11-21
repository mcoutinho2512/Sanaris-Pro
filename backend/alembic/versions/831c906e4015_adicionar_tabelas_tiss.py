"""Adicionar tabelas TISS

Revision ID: 831c906e4015
Revises: 40ecd197ba6e
Create Date: 2025-11-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '831c906e4015'
down_revision = '40ecd197ba6e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tabela: tiss_operadoras
    op.create_table(
        'tiss_operadoras',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('registro_ans', sa.String(length=6), nullable=False),
        sa.Column('razao_social', sa.String(length=200), nullable=False),
        sa.Column('nome_fantasia', sa.String(length=200), nullable=True),
        sa.Column('cnpj', sa.String(length=18), nullable=False),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('site', sa.String(length=200), nullable=True),
        sa.Column('cep', sa.String(length=10), nullable=True),
        sa.Column('logradouro', sa.String(length=200), nullable=True),
        sa.Column('numero', sa.String(length=20), nullable=True),
        sa.Column('complemento', sa.String(length=100), nullable=True),
        sa.Column('bairro', sa.String(length=100), nullable=True),
        sa.Column('cidade', sa.String(length=100), nullable=True),
        sa.Column('estado', sa.String(length=2), nullable=True),
        sa.Column('padrao_tiss_versao', sa.String(length=20), server_default='4.02.01'),
        sa.Column('prazo_envio_dias', sa.Integer(), server_default='30'),
        sa.Column('prazo_pagamento_dias', sa.Integer(), server_default='30'),
        sa.Column('banco_codigo', sa.String(length=10), nullable=True),
        sa.Column('banco_agencia', sa.String(length=20), nullable=True),
        sa.Column('banco_conta', sa.String(length=30), nullable=True),
        sa.Column('ativo', sa.Boolean(), server_default='true'),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('registro_ans')
    )

    # Tabela: tiss_lotes
    op.create_table(
        'tiss_lotes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('operadora_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('numero_lote', sa.String(length=50), nullable=False),
        sa.Column('competencia', sa.String(length=7), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='rascunho'),
        sa.Column('data_envio', sa.DateTime(), nullable=True),
        sa.Column('protocolo_envio', sa.String(length=100), nullable=True),
        sa.Column('data_processamento', sa.DateTime(), nullable=True),
        sa.Column('protocolo_processamento', sa.String(length=100), nullable=True),
        sa.Column('valor_total_informado', sa.Float(), server_default='0.0'),
        sa.Column('valor_total_processado', sa.Float(), server_default='0.0'),
        sa.Column('valor_total_glosa', sa.Float(), server_default='0.0'),
        sa.Column('valor_total_liberado', sa.Float(), server_default='0.0'),
        sa.Column('quantidade_guias', sa.Integer(), server_default='0'),
        sa.Column('quantidade_guias_processadas', sa.Integer(), server_default='0'),
        sa.Column('quantidade_guias_rejeitadas', sa.Integer(), server_default='0'),
        sa.Column('arquivo_xml_path', sa.String(length=500), nullable=True),
        sa.Column('arquivo_retorno_path', sa.String(length=500), nullable=True),
        sa.Column('dados_pagamento', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('data_pagamento', sa.Date(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('motivo_rejeicao', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['operadora_id'], ['tiss_operadoras.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Tabela: tiss_guias
    op.create_table(
        'tiss_guias',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lote_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_guia', sa.String(length=50), nullable=False),
        sa.Column('numero_guia_prestador', sa.String(length=50), nullable=False),
        sa.Column('numero_guia_operadora', sa.String(length=50), nullable=True),
        sa.Column('data_atendimento', sa.Date(), nullable=False),
        sa.Column('hora_inicial', sa.String(length=5), nullable=True),
        sa.Column('hora_final', sa.String(length=5), nullable=True),
        sa.Column('numero_carteira', sa.String(length=50), nullable=False),
        sa.Column('validade_carteira', sa.Date(), nullable=True),
        sa.Column('nome_beneficiario', sa.String(length=200), nullable=False),
        sa.Column('numero_cns', sa.String(length=20), nullable=True),
        sa.Column('codigo_prestador_na_operadora', sa.String(length=50), nullable=True),
        sa.Column('nome_contratado', sa.String(length=200), nullable=False),
        sa.Column('cnpj_contratado', sa.String(length=18), nullable=False),
        sa.Column('cnes', sa.String(length=20), nullable=True),
        sa.Column('nome_profissional', sa.String(length=200), nullable=True),
        sa.Column('numero_conselho_profissional', sa.String(length=20), nullable=True),
        sa.Column('uf_conselho', sa.String(length=2), nullable=True),
        sa.Column('sigla_conselho', sa.String(length=10), nullable=True),
        sa.Column('codigo_cbo', sa.String(length=10), nullable=True),
        sa.Column('indicacao_clinica', sa.String(length=10), nullable=True),
        sa.Column('cid10_principal', sa.String(length=10), nullable=True),
        sa.Column('cid10_secundario', sa.String(length=10), nullable=True),
        sa.Column('cid10_terciario', sa.String(length=10), nullable=True),
        sa.Column('observacoes_clinicas', sa.Text(), nullable=True),
        sa.Column('numero_autorizacao', sa.String(length=50), nullable=True),
        sa.Column('data_autorizacao', sa.Date(), nullable=True),
        sa.Column('valor_total_informado', sa.Float(), server_default='0.0'),
        sa.Column('valor_total_processado', sa.Float(), server_default='0.0'),
        sa.Column('valor_glosa', sa.Float(), server_default='0.0'),
        sa.Column('valor_liberado', sa.Float(), server_default='0.0'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='pendente'),
        sa.Column('motivo_glosa', sa.Text(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['lote_id'], ['tiss_lotes.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Tabela: tiss_procedimentos
    op.create_table(
        'tiss_procedimentos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('guia_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('data_realizacao', sa.Date(), nullable=False),
        sa.Column('hora_inicial', sa.String(length=5), nullable=True),
        sa.Column('hora_final', sa.String(length=5), nullable=True),
        sa.Column('tabela', sa.String(length=10), nullable=False),
        sa.Column('codigo_procedimento', sa.String(length=20), nullable=False),
        sa.Column('descricao_procedimento', sa.String(length=500), nullable=False),
        sa.Column('quantidade_executada', sa.Integer(), server_default='1'),
        sa.Column('via_acesso', sa.String(length=10), nullable=True),
        sa.Column('tecnica_utilizada', sa.String(length=10), nullable=True),
        sa.Column('valor_unitario_informado', sa.Float(), nullable=False),
        sa.Column('valor_total_informado', sa.Float(), nullable=False),
        sa.Column('quantidade_autorizada', sa.Integer(), nullable=True),
        sa.Column('valor_unitario_processado', sa.Float(), nullable=True),
        sa.Column('valor_total_processado', sa.Float(), nullable=True),
        sa.Column('valor_glosa', sa.Float(), server_default='0.0'),
        sa.Column('valor_liberado', sa.Float(), nullable=True),
        sa.Column('codigo_glosa', sa.String(length=10), nullable=True),
        sa.Column('motivo_glosa', sa.String(length=500), nullable=True),
        sa.Column('nome_profissional_executante', sa.String(length=200), nullable=True),
        sa.Column('conselho_profissional', sa.String(length=20), nullable=True),
        sa.Column('numero_conselho', sa.String(length=20), nullable=True),
        sa.Column('uf_conselho', sa.String(length=2), nullable=True),
        sa.Column('codigo_cbo', sa.String(length=10), nullable=True),
        sa.Column('grau_participacao', sa.String(length=10), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['guia_id'], ['tiss_guias.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Tabela: tiss_tabelas_referencia
    op.create_table(
        'tiss_tabelas_referencia',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_tabela', sa.String(length=20), nullable=False),
        sa.Column('codigo_tabela', sa.String(length=10), nullable=False),
        sa.Column('codigo', sa.String(length=20), nullable=False),
        sa.Column('descricao', sa.String(length=500), nullable=False),
        sa.Column('valor_referencia', sa.Float(), nullable=True),
        sa.Column('valor_minimo', sa.Float(), nullable=True),
        sa.Column('valor_maximo', sa.Float(), nullable=True),
        sa.Column('data_inicio_vigencia', sa.Date(), nullable=False),
        sa.Column('data_fim_vigencia', sa.Date(), nullable=True),
        sa.Column('capitulo', sa.String(length=200), nullable=True),
        sa.Column('grupo', sa.String(length=200), nullable=True),
        sa.Column('subgrupo', sa.String(length=200), nullable=True),
        sa.Column('porte_anestesico', sa.String(length=10), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('tiss_procedimentos')
    op.drop_table('tiss_guias')
    op.drop_table('tiss_lotes')
    op.drop_table('tiss_tabelas_referencia')
    op.drop_table('tiss_operadoras')