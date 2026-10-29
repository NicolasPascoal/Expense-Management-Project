"""categorias padrão nas obras que não têm nenhuma delas

Revision ID: f6d2b8c4e1a7
Revises: e5c9a3b7d2f4
Create Date: 2026-10-29 12:00:00.000000

Só a primeira obra do banco recebia as categorias padrão; obras criadas pelo
cadastro público ou por "nova obra" nasciam sem nenhuma, e o formulário de
lançamento mostrava uma lista fixa do frontend que sumia assim que a primeira
categoria era cadastrada (parecia que as outras tinham sido excluídas).

Adiciona as padrão a toda obra que não tem nenhuma delas — inclusive a que já
cadastrou uma categoria própria depois do problema. Obra que já tem alguma
padrão não é tocada. Idempotente: rodar de novo não duplica nada.

Lista congelada aqui de propósito (não importa CATEGORIAS_PADRAO): a migration
precisa continuar fazendo a mesma coisa mesmo que a lista do app mude depois.
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'f6d2b8c4e1a7'
down_revision: Union[str, Sequence[str], None] = 'e5c9a3b7d2f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CATEGORIAS_PADRAO = ["Documentação", "Terraplanagem", "Fundação", "Ferramentas", "Material de construção", "Mão de obra", "Equipamentos/aluguel", "Taxas e impostos", "Outros"]


def upgrade() -> None:
    valores = ", ".join("('" + nome.replace("'", "''") + "')" for nome in CATEGORIAS_PADRAO)
    op.execute(f"""
        INSERT INTO categorias (nome, projeto_id)
        SELECT padrao.nome, p.id
        FROM projetos p
        CROSS JOIN (VALUES {valores}) AS padrao(nome)
        WHERE NOT EXISTS (
            SELECT 1 FROM categorias c
            WHERE c.projeto_id = p.id
              AND lower(c.nome) IN (SELECT lower(nome) FROM (VALUES {valores}) AS v(nome))
        )
    """)


def downgrade() -> None:
    # Sem volta: depois do upgrade não dá para distinguir categoria inserida
    # aqui de categoria padrão já existente (ou já usada em lançamentos).
    pass
