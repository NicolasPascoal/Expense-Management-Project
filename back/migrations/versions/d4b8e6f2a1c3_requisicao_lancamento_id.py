"""requisicoes_materiais.lancamento_id (Tarefa 7.5)

Revision ID: d4b8e6f2a1c3
Revises: c7a1f05e9b2d
Create Date: 2026-10-07 21:00:00.000000

Vincula a requisição ao lançamento gerado a partir dela. Espelha
app/database/modelRequisicoes.py. Idempotente: o init_db() roda antes do
Alembic no deploy (migrar_banco.py) e já adiciona a coluna.
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'd4b8e6f2a1c3'
down_revision: Union[str, Sequence[str], None] = 'c7a1f05e9b2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE requisicoes_materiais "
        "ADD COLUMN IF NOT EXISTS lancamento_id INTEGER "
        "REFERENCES lancamentos_v2 (id) ON DELETE SET NULL"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE requisicoes_materiais DROP COLUMN IF EXISTS lancamento_id")
