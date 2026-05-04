import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cria a tabela de lançamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            categoria TEXT,
            item TEXT,
            fornecedor TEXT,
            quantidade REAL,
            unitario REAL,
            valor REAL,
            forma TEXT,
            conta TEXT,
            obs TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
