"""Initial schema with all tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-04-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create animais table
    op.create_table(
        'animais',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rfid', sa.String(50), nullable=True),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('raca', sa.String(50), nullable=False),
        sa.Column('data_nascimento', sa.Date(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='ATIVO'),
        sa.Column('criada_em', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('atualizada_em', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rfid'),
        sa.CheckConstraint("status IN ('ATIVO', 'VENDIDO', 'FALECIDO')")
    )

    # Create lotes table
    op.create_table(
        'lotes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('data_inicio', sa.Date(), nullable=False),
        sa.Column('data_fim', sa.Date(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='ATIVO'),
        sa.Column('criada_em', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('atualizada_em', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('ATIVO', 'FINALIZADO', 'CANCELADO')")
    )

    # Create pesagens table
    op.create_table(
        'pesagens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('animal_id', sa.Integer(), nullable=False),
        sa.Column('peso_kg', sa.Numeric(8, 2), nullable=False),
        sa.Column('peso_arroba', sa.Numeric(8, 2), nullable=True),
        sa.Column('data', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('criada_em', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('atualizada_em', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['animal_id'], ['animais.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create alimentacao table
    op.create_table(
        'alimentacao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('animal_id', sa.Integer(), nullable=False),
        sa.Column('tipo_alimento', sa.String(100), nullable=False),
        sa.Column('quantidade_kg', sa.Numeric(8, 2), nullable=False),
        sa.Column('data_alimento', sa.Date(), nullable=False),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('criada_em', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('atualizada_em', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['animal_id'], ['animais.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create vacinas table
    op.create_table(
        'vacinas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('animal_id', sa.Integer(), nullable=False),
        sa.Column('nome_vacina', sa.String(100), nullable=False),
        sa.Column('data_aplicacao', sa.Date(), nullable=False),
        sa.Column('proxima_dose', sa.Date(), nullable=True),
        sa.Column('veterinario', sa.String(100), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('criada_em', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('atualizada_em', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['animal_id'], ['animais.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create cotacoes table
    op.create_table(
        'cotacoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('preco_arroba', sa.Numeric(8, 2), nullable=False),
        sa.Column('data_referencia', sa.Date(), nullable=False),
        sa.Column('criada_em', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('atualizada_em', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_animais_rfid', 'animais', ['rfid'])
    op.create_index('idx_animais_status', 'animais', ['status'])
    op.create_index('idx_pesagens_animal_id', 'pesagens', ['animal_id'])
    op.create_index('idx_pesagens_data', 'pesagens', ['data'])
    op.create_index('idx_alimentacao_animal_id', 'alimentacao', ['animal_id'])
    op.create_index('idx_vacinas_animal_id', 'vacinas', ['animal_id'])
    op.create_index('idx_cotacoes_data', 'cotacoes', ['data_referencia'])
    op.create_index('idx_cotacoes_preco', 'cotacoes', ['preco_arroba'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_cotacoes_preco', 'cotacoes')
    op.drop_index('idx_cotacoes_data', 'cotacoes')
    op.drop_index('idx_vacinas_animal_id', 'vacinas')
    op.drop_index('idx_alimentacao_animal_id', 'alimentacao')
    op.drop_index('idx_pesagens_data', 'pesagens')
    op.drop_index('idx_pesagens_animal_id', 'pesagens')
    op.drop_index('idx_animais_status', 'animais')
    op.drop_index('idx_animais_rfid', 'animais')

    # Drop tables
    op.drop_table('cotacoes')
    op.drop_table('vacinas')
    op.drop_table('alimentacao')
    op.drop_table('pesagens')
    op.drop_table('lotes')
    op.drop_table('animais')
