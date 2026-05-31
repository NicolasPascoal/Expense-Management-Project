import sqlite3
import os
import json
import psycopg2
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

PG_USER = os.getenv("PGUSER", "postgres")
PG_PASSWORD = os.getenv("PGPASSWORD", "postgres")
PG_HOST = os.getenv("PGHOST", "localhost")
PG_PORT = os.getenv("PGPORT", "5432")
PG_DATABASE = os.getenv("PGDATABASE", "expense_management")

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(BASE_DIR, 'database.db')

def ensure_database_exists():
    """
    Conecta ao banco de dados padrão 'postgres' para verificar e criar o banco
    de dados de destino caso ele não exista.
    """
    print(f"Conectando ao PostgreSQL (host={PG_HOST}, user={PG_USER}) para verificar o banco...")
    try:
        # Conecta ao banco padrão 'postgres'
        conn = psycopg2.connect(
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Verifica se o banco de dados de destino existe
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (PG_DATABASE,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Criando o banco de dados '{PG_DATABASE}'...")
            cursor.execute(f"CREATE DATABASE {PG_DATABASE}")
            print(f"Banco de dados '{PG_DATABASE}' criado com sucesso!")
        else:
            print(f"Banco de dados '{PG_DATABASE}' ja existe.")
            
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("\n=========================================================================")
        print(" [X] ERRO DE CONEXAO COM O POSTGRESQL!")
        print("=========================================================================")
        print("Nao foi possivel conectar ao seu servidor PostgreSQL.")
        print(f"Configuracoes atuais usadas: Host={PG_HOST}:{PG_PORT}, Usuario={PG_USER}")
        print("\nPor favor, siga estas etapas:")
        print("1. Abra o arquivo 'back/.env' que acabei de criar para voce.")
        print("2. Insira a senha correta do seu usuario 'postgres' na variavel 'PGPASSWORD'.")
        print("3. Se o seu usuario ou porta forem diferentes, ajuste-os tambem.")
        print("4. Salve o arquivo '.env' e execute este script de migracao novamente.")
        print("=========================================================================\n")
        return False

def migrate_data():
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"Erro: Banco de dados SQLite nao encontrado em {SQLITE_DB_PATH}")
        return

    # Garante que o banco de dados existe
    if not ensure_database_exists():
        return

    # Importa a conexão local apenas após garantir que o banco existe
    from app.database.db import get_db_connection, init_db

    print("\nInicializando o schema do PostgreSQL...")
    try:
        init_db()
    except Exception as e:
        print(f"Erro ao inicializar o schema do PostgreSQL: {e}")
        return

    print("Conectando aos bancos para transferir os dados...")
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    try:
        pg_conn = get_db_connection()
        pg_cursor = pg_conn.cursor()
    except Exception as e:
        print(f"Erro ao conectar ao banco recem-criado: {e}")
        sqlite_conn.close()
        return

    # Tabelas a serem migradas na ordem correta (respeitando chaves estrangeiras)
    tables = [
        "projetos",
        "usuarios",
        "lancamentos_v2",
        "lancamentos",
        "categorias",
        "contas",
        "requisicoes_materiais"
    ]

    for table in tables:
        print(f"\nMigrando tabela '{table}'...")
        
        # Verifica se a tabela existe no SQLite
        sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not sqlite_cursor.fetchone():
            print(f"Tabela '{table}' nao existe no SQLite. Pulando...")
            continue

        # Busca todas as linhas do SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"Nenhum dado na tabela '{table}' no SQLite. Pulando...")
            continue

        # Limpa dados antigos no PostgreSQL antes de migrar (para evitar conflitos de chaves primarias)
        print(f"Limpando dados antigos de '{table}' no PostgreSQL...")
        pg_cursor.execute(f"TRUNCATE TABLE {table} CASCADE")

        # Obtem os nomes das colunas
        cols = rows[0].keys()
        cols_str = ", ".join(cols)
        placeholders = ", ".join(["?"] * len(cols)) # O wrapper traduz ? para %s!

        print(f"Inserindo {len(rows)} registros no PostgreSQL...")
        for row in rows:
            values = [row[c] for c in cols]
            pg_cursor.execute(f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})", values)

        # Commita os inserts desta tabela
        pg_conn.commit()
        print(f"Tabela '{table}' migrada com sucesso!")

        # Sincroniza a sequencia SERIAL no PostgreSQL
        try:
            sqlite_cursor.execute(f"PRAGMA table_info({table})")
            columns_info = sqlite_cursor.fetchall()
            has_id = any(c['name'] == 'id' for c in columns_info)
            if has_id:
                pg_cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 1))")
                pg_conn.commit()
                print(f"Sequencia do serial de '{table}' sincronizada com sucesso.")
        except Exception as e:
            print(f"Aviso ao sincronizar sequencia de '{table}': {e}")

    sqlite_conn.close()
    pg_conn.close()
    print("\n=========================================")
    print(" MIGRAÇÃO DE DADOS CONCLUÍDA COM SUCESSO!")
    print("=========================================")

if __name__ == "__main__":
    migrate_data()
