def create_tarefas_tables(cursor):
    """
    Cria a tabela de Tarefas.
    """
    # Tabela de Tarefas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            descricao TEXT,
            prestador_id INTEGER,
            status VARCHAR(50) DEFAULT 'Pendente',
            observacoes TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (prestador_id) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')
