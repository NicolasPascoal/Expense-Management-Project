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
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')
