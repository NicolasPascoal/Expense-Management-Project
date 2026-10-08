"""
Papéis expandidos (Tarefa 6.1, ver STATUS.md): cada papel não-admin tem um
conjunto explícito de permissões — substitui o antigo padrão "libera tudo
exceto prestador" por uma lista de permissão positiva, mais segura por
padrão (um papel desconhecido não ganha acesso nenhum).

Desde a Tarefa 6.2, 'acesso_financeiro' de qualquer papel não-admin vale só
para as obras às quais o usuário está vinculado (usuario_projetos) — o recorte
por obra é feito nas queries (app/utils/tenant.py), não aqui. Por isso
'gestor_obra' passou a ter 'acesso_financeiro': ele só vê as obras dele.
"""

PERMISSOES_POR_PAPEL = {
    'financeiro': {'acesso_financeiro'},
    'gestor_obra': {'acesso_financeiro', 'aprovar_requisicoes', 'gerenciar_tarefas'},
    'prestador': set(),
}


# Papéis aceitos ao criar/editar usuário: admin + os da matriz acima.
PAPEIS_VALIDOS = ('admin', *PERMISSOES_POR_PAPEL)


def tem_permissao(user, permissao):
    """is_admin sempre passa (autoridade máxima); caso contrário, checa o
    conjunto de permissões do papel. Papel desconhecido nunca tem permissão."""
    if user.get('is_admin'):
        return True
    return permissao in PERMISSOES_POR_PAPEL.get(user.get('role'), set())
