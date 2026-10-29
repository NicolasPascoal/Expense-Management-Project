# Toda obra nova nasce com estas categorias (criação de obra, cadastro público e
# seed do init_db). Antes só a primeira obra do banco as recebia; as demais
# mostravam uma lista fixa do frontend que sumia ao cadastrar a primeira
# categoria. A migration f6d2b8c4e1a7 tem uma cópia congelada desta lista.
CATEGORIAS_PADRAO = ["Documentação","Terraplanagem","Fundação","Ferramentas","Material de construção","Mão de obra","Equipamentos/aluguel","Taxas e impostos","Outros"]


def criar_categorias_padrao(cursor, projeto_id):
    cursor.executemany("INSERT INTO categorias (nome, projeto_id) VALUES (?, ?)", [(c, projeto_id) for c in CATEGORIAS_PADRAO])


def create_categorias_tables(cursor):
    """
    Cria as tabelas de Categorias e Contas e insere as categorias iniciais padrao.
    Contas não têm seed: cada empresa cadastra as suas (eram nomes reais da
    obra original, que apareciam para todo cliente novo).
    """
    # Tabela de Categorias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            projeto_id INTEGER REFERENCES projetos (id) ON DELETE CASCADE
        )
    ''')

    # Tabela de Contas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contas (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            projeto_id INTEGER REFERENCES projetos (id) ON DELETE CASCADE
        )
    ''')

    # Seeds iniciais
    cursor.execute("SELECT id FROM projetos ORDER BY id ASC LIMIT 1")
    primeiro_projeto = cursor.fetchone()
    if primeiro_projeto:
        pid = primeiro_projeto[0]
        
        cursor.execute("SELECT COUNT(*) FROM categorias")
        if cursor.fetchone()[0] == 0:
            criar_categorias_padrao(cursor, pid)
            cursor.execute("SELECT setval(pg_get_serial_sequence('categorias', 'id'), COALESCE((SELECT MAX(id) FROM categorias), 1))")

