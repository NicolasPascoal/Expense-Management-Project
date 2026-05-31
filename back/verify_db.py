import json
from app.database.db import get_db_connection

def verify():
    conn = get_db_connection()
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
