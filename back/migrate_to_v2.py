import json
from app.database.db import get_db_connection

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
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Garantir que as novas tabelas existem
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            colunas TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos_v2 (
            id SERIAL PRIMARY KEY,
            projeto_id INTEGER NOT NULL,
            dados TEXT NOT NULL,
            FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE CASCADE
        )
    ''')

    # 2. Verificar se a tabela antiga tem dados
    try:
        cursor.execute("SELECT * FROM lancamentos")
        old_data = cursor.fetchall()
    except Exception:
        print("Tabela 'lancamentos' antiga não existe ou erro ao ler. Criando projeto inicial vazio.")
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
        cursor.execute("SELECT setval(pg_get_serial_sequence('projetos', 'id'), COALESCE((SELECT MAX(id) FROM projetos), 1))")
    else:
        projeto_id = projeto['id']

    # 4. Migrar dados
    if old_data:
        print(f"Migrando {len(old_data)} registros para a nova estrutura...")
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
