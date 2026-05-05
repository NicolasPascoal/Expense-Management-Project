import sqlite3
import json
import os

# Configurações de caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

DEFAULT_COLUMNS = [
    {"name": "data", "label": "Data", "type": "text"},
    {"name": "categoria", "label": "Categoria", "type": "select"},
    {"name": "item", "label": "Item", "type": "text"},
    {"name": "fornecedor", "label": "Fornecedor", "type": "text"},
    {"name": "quantidade", "label": "Qtd", "type": "number"},
    {"name": "unitario", "label": "Unitário", "type": "number"},
    {"name": "valor", "label": "Valor", "type": "number"},
    {"name": "forma", "label": "Forma", "type": "select"},
    {"name": "conta", "label": "Conta", "type": "select"},
    {"name": "obs", "label": "Observações", "type": "textarea"}
]

def migrate():
    if not os.path.exists(DB_PATH):
        print("Banco de dados não encontrado. Nada para migrar.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Garantir que as novas tabelas existem (caso o app não tenha rodado ainda)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            colunas TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos_v2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER NOT NULL,
            dados TEXT NOT NULL,
            FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE CASCADE
        )
    ''')

    # 2. Verificar se a tabela antiga tem dados
    try:
        cursor.execute("SELECT * FROM lancamentos")
        old_data = cursor.fetchall()
    except sqlite3.OperationalError:
        print("Tabela 'lancamentos' antiga não existe. Criando projeto inicial vazio.")
        old_data = []

    # 3. Criar projeto padrão se não existir
    cursor.execute("SELECT id FROM projetos WHERE nome = 'Obra Itanhaém'")
    projeto = cursor.fetchone()
    
    if not projeto:
        print("Criando projeto 'Obra Itanhaém'...")
        cursor.execute(
            "INSERT INTO projetos (nome, colunas) VALUES (?, ?)",
            ('Obra Itanhaém', json.dumps(DEFAULT_COLUMNS))
        )
        projeto_id = cursor.lastrowid
    else:
        projeto_id = projeto['id']

    # 4. Migrar dados
    if old_data:
        print(f"Migrando {len(old_data)} registros para a nova estrutura...")
        # Verificar se já foram migrados (opcional, aqui vamos apenas migrar o que não estiver na v2)
        # Para simplificar, vamos migrar tudo se a v2 estiver vazia
        cursor.execute("SELECT count(*) as count FROM lancamentos_v2 WHERE projeto_id = ?", (projeto_id,))
        if cursor.fetchone()['count'] == 0:
            for row in old_data:
                dados = {
                    "data": row["data"],
                    "categoria": row["categoria"],
                    "item": row["item"],
                    "fornecedor": row["fornecedor"],
                    "quantidade": row["quantidade"],
                    "unitario": row["unitario"],
                    "valor": row["valor"],
                    "forma": row["forma"],
                    "conta": row["conta"],
                    "obs": row["obs"]
                }
                cursor.execute(
                    "INSERT INTO lancamentos_v2 (projeto_id, dados) VALUES (?, ?)",
                    (projeto_id, json.dumps(dados))
                )
            print("Migração concluída com sucesso!")
        else:
            print("Os dados já parecem ter sido migrados para este projeto.")
    else:
        print("Nenhum dado antigo encontrado para migrar.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
