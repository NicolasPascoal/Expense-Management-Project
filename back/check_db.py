import json
from app.database.db import get_db_connection

def check_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("--- Projetos ---")
    cursor.execute("SELECT id, nome, colunas FROM projetos")
    for row in cursor.fetchall():
        cols = row['colunas']
        is_json = False
        try:
            if cols:
                json.loads(cols)
                is_json = True
        except:
            pass
        print(f"ID: {row['id']}, Nome: {row['nome']}, Colunas: {cols[:50] if cols else ''}... (Valid JSON: {is_json})")
        
    print("\n--- Usuarios ---")
    cursor.execute("SELECT id, username, is_admin FROM usuarios")
    for row in cursor.fetchall():
        print(f"ID: {row['id']}, Username: {row['username']}, Admin: {row['is_admin']}")
        
    conn.close()

if __name__ == "__main__":
    check_db()
