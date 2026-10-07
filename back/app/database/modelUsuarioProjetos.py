def create_usuario_projetos_tables(cursor):
    """
    Cria a tabela de vínculo usuário↔obra (Tarefa 6.2): um usuário não-admin
    só enxerga as obras às quais está vinculado. Admin não precisa de vínculo.

    `id SERIAL` existe só porque o wrapper de cursor (db.py) roda
    `SELECT lastval()` após todo INSERT — numa tabela sem sequência isso
    abortaria a transação em uma conexão nova. A chave real é o UNIQUE.

    Backfill único: quando a tabela é criada pela primeira vez, todo usuário
    não-admin é vinculado a todas as obras da própria empresa, preservando o
    acesso que já tinha antes desta tarefa. Roda só na criação (não a cada
    boot) — senão um vínculo removido pelo admin voltaria sozinho. Fica aqui,
    e não só na migration do Alembic, porque o deploy cria o schema via
    init_db() e não roda `alembic upgrade`.
    """
    cursor.execute("SELECT to_regclass('public.usuario_projetos') IS NOT NULL AS existe")
    ja_existia = cursor.fetchone()[0]

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario_projetos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios (id) ON DELETE CASCADE,
            projeto_id INTEGER NOT NULL REFERENCES projetos (id) ON DELETE CASCADE,
            UNIQUE (usuario_id, projeto_id)
        )
    ''')

    if not ja_existia:
        # Escrito como CTE (começa com WITH, não INSERT) de propósito: o wrapper
        # roda `SELECT lastval()` após todo comando iniciado por INSERT, e se o
        # backfill não inserir nenhuma linha (empresa sem não-admins) a sequência
        # nunca é usada, lastval() falha e aborta a transação inteira do init_db().
        cursor.execute('''
            WITH vinculos AS (
                SELECT u.id AS usuario_id, p.id AS projeto_id
                FROM usuarios u
                JOIN projetos p ON p.empresa_id = u.empresa_id
                WHERE COALESCE(u.is_admin, 0) = 0
            )
            INSERT INTO usuario_projetos (usuario_id, projeto_id)
            SELECT usuario_id, projeto_id FROM vinculos
        ''')
