def create_categorias_tables(cursor):
    """
    Cria as tabelas de Categorias e Contas e insere os registros iniciais padrao.
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
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        categorias_iniciais = ["Documentação","Terraplanagem","Fundação","Ferramentas","Material de construção","Mão de obra","Equipamentos/aluguel","Taxas e impostos","Outros"]
        cursor.executemany("INSERT INTO categorias (nome, projeto_id) VALUES (?, 1)", [(c,) for c in categorias_iniciais])
        cursor.execute("SELECT setval(pg_get_serial_sequence('categorias', 'id'), COALESCE((SELECT MAX(id) FROM categorias), 1))")

    cursor.execute("SELECT COUNT(*) FROM contas")
    if cursor.fetchone()[0] == 0:
        contas_iniciais = ["FF Alves Construtora","Victor Praça Pascoal","Vanderlei Almeida Simões","SPE Luiz Pascoal"]
        cursor.executemany("INSERT INTO contas (nome, projeto_id) VALUES (?, 1)", [(c,) for c in contas_iniciais])
        cursor.execute("SELECT setval(pg_get_serial_sequence('contas', 'id'), COALESCE((SELECT MAX(id) FROM contas), 1))")
