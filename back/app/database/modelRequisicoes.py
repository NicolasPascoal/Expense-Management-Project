def create_requisicoes_tables(cursor):
    """
    Cria a tabela de Requisicoes de Materiais.
    """
    # Tabela de Requisições de Materiais
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requisicoes_materiais (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            nome VARCHAR(255) NOT NULL,
            funcao VARCHAR(255) NOT NULL,
            material TEXT NOT NULL,
            status VARCHAR(50) DEFAULT 'Pendente',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            lancamento_id INTEGER REFERENCES lancamentos_v2 (id) ON DELETE SET NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')

    # Tarefa 7.5: lançamento gerado a partir desta requisição. Também como
    # ALTER idempotente porque bancos já existentes (e o banco de teste, que
    # só roda init_db) têm a tabela sem a coluna — a migration Alembic
    # d4b8e6f2a1c3 registra a mesma mudança no histórico.
    cursor.execute('''
        ALTER TABLE requisicoes_materiais
        ADD COLUMN IF NOT EXISTS lancamento_id INTEGER REFERENCES lancamentos_v2 (id) ON DELETE SET NULL
    ''')
