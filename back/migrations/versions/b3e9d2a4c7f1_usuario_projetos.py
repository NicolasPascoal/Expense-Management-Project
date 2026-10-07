"""usuario_projetos: vínculo usuário↔obra (Tarefa 6.2)

Revision ID: b3e9d2a4c7f1
Revises: 61a73b52f4cf
Create Date: 2026-10-07 19:30:00.000000

Espelha app/database/modelUsuarioProjetos.py. Idempotente de propósito: o
init_db() que roda no boot do app normalmente já criou a tabela (e fez o
backfill) antes de alguém rodar `alembic upgrade` — o deploy hoje não roda
Alembic. Backfill só acontece se esta migration for quem cria a tabela.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b3e9d2a4c7f1'
down_revision: Union[str, Sequence[str], None] = '61a73b52f4cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if sa.inspect(op.get_bind()).has_table('usuario_projetos'):
        return

    op.create_table('usuario_projetos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('projeto_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['projeto_id'], ['projetos.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('usuario_id', 'projeto_id')
    )
    # Preserva o acesso que todo não-admin tinha antes (todas as obras da empresa).
    op.execute(
        "INSERT INTO usuario_projetos (usuario_id, projeto_id) "
        "SELECT u.id, p.id FROM usuarios u JOIN projetos p ON p.empresa_id = u.empresa_id "
        "WHERE COALESCE(u.is_admin, 0) = 0"
    )


def downgrade() -> None:
    op.drop_table('usuario_projetos')
