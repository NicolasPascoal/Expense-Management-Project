def create_empresas_tables(cursor):
    """
    Cria a tabela de Empresas (tenant) e insere a empresa seed (id=1) numa
    instalação nova. Bancos que já existiam mantêm o nome que tinham — a
    empresa 1 herdou o histórico legado da antiga instância única.
    """
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM empresas")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO empresas (id, nome) VALUES (1, 'Minha Construtora')")
        cursor.execute("SELECT setval(pg_get_serial_sequence('empresas', 'id'), COALESCE((SELECT MAX(id) FROM empresas), 1))")
