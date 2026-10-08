import logging
import os
import secrets

from werkzeug.security import generate_password_hash

logger = logging.getLogger("gabaro.seed")


def create_usuarios_tables(cursor):
    """
    Cria a tabela de Usuarios e insere o administrador inicial.
    """
    # Tabela de Usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            is_admin INTEGER DEFAULT 0,
            role VARCHAR(50) DEFAULT 'prestador',
            empresa_id INTEGER NOT NULL REFERENCES empresas(id),
            ativo BOOLEAN NOT NULL DEFAULT TRUE,
            senha_alterada_em TIMESTAMP
        )
    ''')

    # Pacote "usuários e acesso": `ativo` (desativar em vez de apagar — apagar
    # removia em cascata tarefas/requisições da pessoa) e `senha_alterada_em`
    # (tokens emitidos antes da última troca de senha deixam de valer). ALTER
    # idempotente para bancos existentes e o banco de teste (só roda init_db);
    # a migration Alembic e5c9a3b7d2f4 registra a mesma mudança.
    cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS ativo BOOLEAN NOT NULL DEFAULT TRUE")
    cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS senha_alterada_em TIMESTAMP")

    # Admin inicial, vinculado à empresa seed (id=1) — só num banco vazio.
    # Credencial vem de ADMIN_USERNAME/ADMIN_PASSWORD (as mesmas do
    # create_admin.py); sem elas, gera uma senha aleatória e a escreve uma
    # única vez no log, em vez do antigo admin/admin previsível.
    # O backfill de role a partir de is_admin (antes rodava a cada boot aqui)
    # virou migration de dado única — ver migrations/versions/61a73b52f4cf_*.py.
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        username = os.getenv("ADMIN_USERNAME") or "admin"
        password = os.getenv("ADMIN_PASSWORD")
        if not password:
            password = secrets.token_urlsafe(12)
            logger.warning(
                "Admin inicial criado com senha aleatória — anote e troque após o primeiro login "
                "(defina ADMIN_USERNAME/ADMIN_PASSWORD para escolher): usuário=%s senha=%s",
                username, password
            )
        cursor.execute("INSERT INTO usuarios (username, password, is_admin, role, empresa_id) VALUES (?, ?, 1, 'admin', 1)",
                       (username, generate_password_hash(password)))
        cursor.execute("SELECT setval(pg_get_serial_sequence('usuarios', 'id'), COALESCE((SELECT MAX(id) FROM usuarios), 1))")
