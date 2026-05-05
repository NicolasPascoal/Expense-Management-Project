import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON") # Habilita suporte a chaves estrangeiras
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de Projetos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            colunas TEXT -- JSON string com a definição das colunas
        )
    ''')

    # Garantir que existe ao menos um projeto para as chaves estrangeiras
    cursor.execute("SELECT COUNT(*) FROM projetos")
    default_cols = '[{"name":"data","label":"Data","type":"text"},{"name":"categoria","label":"Categoria","type":"select"},{"name":"item","label":"Item / Descrição","type":"text"},{"name":"fornecedor","label":"Fornecedor","type":"text"},{"name":"quantidade","label":"Qtd","type":"number"},{"name":"unitario","label":"Unitário (R$)","type":"text"},{"name":"valor","label":"Valor Pago (R$)","type":"text"},{"name":"forma","label":"Forma","type":"select"},{"name":"conta","label":"Conta","type":"select"},{"name":"obs","label":"Observações","type":"textarea"}]'
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO projetos (id, nome, colunas) VALUES (?, ?, ?)", (1, "Projeto Principal", default_cols))
    else:
        # Garante que o projeto 1 tenha colunas se estiver vazio (correção para bancos já criados)
        cursor.execute("UPDATE projetos SET colunas = ? WHERE id = 1 AND (colunas IS NULL OR colunas = '[]' OR colunas = '')", (default_cols,))

    # Nova tabela de lançamentos (versão 2)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos_v2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER NOT NULL,
            dados TEXT NOT NULL,
            FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE CASCADE
        )
    ''')
    
    # Mantemos a tabela antiga por enquanto
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

    # Tabela de Categorias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            projeto_id INTEGER,
            FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE CASCADE
        )
    ''')
    try:
        cursor.execute("ALTER TABLE categorias ADD COLUMN projeto_id INTEGER REFERENCES projetos(id) ON DELETE CASCADE")
        cursor.execute("UPDATE categorias SET projeto_id = 1 WHERE projeto_id IS NULL")
    except:
        pass

    # Tabela de Contas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            projeto_id INTEGER,
            FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE CASCADE
        )
    ''')
    try:
        cursor.execute("ALTER TABLE contas ADD COLUMN projeto_id INTEGER REFERENCES projetos(id) ON DELETE CASCADE")
        cursor.execute("UPDATE contas SET projeto_id = 1 WHERE projeto_id IS NULL")
    except:
        pass

    # Tabela de Usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            role TEXT DEFAULT 'prestador'
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN is_admin INTEGER DEFAULT 0")
    except:
        pass 

    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN role TEXT DEFAULT 'prestador'")
    except:
        pass

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        from werkzeug.security import generate_password_hash
        cursor.execute("INSERT INTO usuarios (username, password, is_admin, role) VALUES (?, ?, ?, ?)", 
                       ("admin", generate_password_hash("admin"), 1, "admin"))
    else:
        cursor.execute("UPDATE usuarios SET is_admin = 1, role = 'admin' WHERE username = 'admin'")
        cursor.execute("UPDATE usuarios SET role = 'admin' WHERE is_admin = 1")

    # Tabela de Requisições de Materiais
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requisicoes_materiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            funcao TEXT NOT NULL,
            material TEXT NOT NULL,
            status TEXT DEFAULT 'Pendente',
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        categorias_iniciais = ["Documentação","Terraplanagem","Fundação","Ferramentas","Material de construção","Mão de obra","Equipamentos/aluguel","Taxas e impostos","Outros"]
        cursor.executemany("INSERT INTO categorias (nome, projeto_id) VALUES (?, ?)", [(c, 1) for c in categorias_iniciais])

    cursor.execute("SELECT COUNT(*) FROM contas")
    if cursor.fetchone()[0] == 0:
        contas_iniciais = ["FF Alves Construtora","Victor Praça Pascoal","Vanderlei Almeida Simões","SPE Luiz Pascoal"]
        cursor.executemany("INSERT INTO contas (nome, projeto_id) VALUES (?, ?)", [(c, 1) for c in contas_iniciais])
    
    conn.commit()
    conn.close()
