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
            categorias_iniciais = ["Documentação","Terraplanagem","Fundação","Ferramentas","Material de construção","Mão de obra","Equipamentos/aluguel","Taxas e impostos","Outros"]
            cursor.executemany("INSERT INTO categorias (nome, projeto_id) VALUES (?, ?)", [(c, pid) for c in categorias_iniciais])
            cursor.execute("SELECT setval(pg_get_serial_sequence('categorias', 'id'), COALESCE((SELECT MAX(id) FROM categorias), 1))")

