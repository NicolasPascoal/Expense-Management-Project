"""reaplica os backfills de dado da baseline

Revision ID: c7a1f05e9b2d
Revises: b3e9d2a4c7f1
Create Date: 2026-10-07 20:00:00.000000

Os backfills da baseline (61a73b52f4cf) saíram do boot do backend na
Tarefa 3.1, mas o deploy nunca rodou Alembic — e bancos criados pelo
init_db() (staging) recebem a baseline via `stamp`, que não executa o
upgrade(). Resultado: esses UPDATEs nunca rodaram fora de dev/teste.

Esta revision repete os mesmos UPDATEs. Todos são idempotentes, então
reexecutar em bancos onde a baseline já rodou de verdade não muda nada.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c7a1f05e9b2d'
down_revision: Union[str, Sequence[str], None] = 'b3e9d2a4c7f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_DEFAULT_COLS = (
    '[{"name":"data","label":"Data","type":"text"},'
    '{"name":"categoria","label":"Categoria","type":"select"},'
    '{"name":"item","label":"Item / Descrição","type":"text"},'
    '{"name":"fornecedor","label":"Fornecedor","type":"text"},'
    '{"name":"quantidade","label":"Qtd","type":"number"},'
    '{"name":"unitario","label":"Unitário (R$)","type":"text"},'
    '{"name":"valor","label":"Valor Pago (R$)","type":"text"},'
    '{"name":"forma","label":"Forma","type":"select"},'
    '{"name":"conta","label":"Conta","type":"select"},'
    '{"name":"obs","label":"Observações","type":"textarea"}]'
)


def upgrade() -> None:
    op.execute("UPDATE usuarios SET is_admin = 1, role = 'admin' WHERE username = 'admin'")
    op.execute("UPDATE usuarios SET role = 'admin' WHERE is_admin = 1")
    op.execute(
        sa.text(
            "UPDATE projetos SET colunas = :cols "
            "WHERE id = 1 AND (colunas IS NULL OR colunas = '[]' OR colunas = '')"
        ).bindparams(cols=_DEFAULT_COLS)
    )


def downgrade() -> None:
    # Backfill de dado: não há estado anterior a restaurar.
    pass
