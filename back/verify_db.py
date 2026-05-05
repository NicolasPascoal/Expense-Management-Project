import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def verify():
    if not os.path.exists(DB_PATH):
        print("Banco de dados não encontrado.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("--- Verificando Projetos ---")
    cursor.execute("SELECT * FROM projetos")
    projetos = cursor.fetchall()
    for p in projetos:
        print(f"ID: {p['id']}, Nome: {p['nome']}")
        colunas = json.loads(p['colunas'])
        print(f"  Colunas ({len(colunas)}): {[c['name'] for c in colunas]}")

    print("\n--- Verificando Lançamentos (Top 5) ---")
    cursor.execute("SELECT * FROM lancamentos_v2 LIMIT 5")
    lancamentos = cursor.fetchall()
    for l in lancamentos:
        dados = json.loads(l['dados'])
        print(f"Projeto ID: {l['projeto_id']}, Dados: {dados}")

    conn.close()

if __name__ == "__main__":
    verify()
