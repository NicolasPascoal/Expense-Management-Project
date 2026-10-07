"""usuarios.ativo e usuarios.senha_alterada_em (pacote usuários e acesso)

Revision ID: e5c9a3b7d2f4
Revises: d4b8e6f2a1c3
Create Date: 2026-10-07 22:00:00.000000

Espelha app/database/modelUsuarios.py. Idempotente: o init_db() roda antes
do Alembic no deploy (migrar_banco.py) e já adiciona as colunas.
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'e5c9a3b7d2f4'
down_revision: Union[str, Sequence[str], None] = 'd4b8e6f2a1c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS ativo BOOLEAN NOT NULL DEFAULT TRUE")
    op.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS senha_alterada_em TIMESTAMP")


def downgrade() -> None:
    op.execute("ALTER TABLE usuarios DROP COLUMN IF EXISTS senha_alterada_em")
    op.execute("ALTER TABLE usuarios DROP COLUMN IF EXISTS ativo")
