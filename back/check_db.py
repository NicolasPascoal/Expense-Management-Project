import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Projetos ---")
    cursor.execute("SELECT id, nome, colunas FROM projetos")
    for row in cursor.fetchall():
        cols = row[2]
        is_json = False
        try:
            if cols:
                json.loads(cols)
                is_json = True
        except:
            pass
        print(f"ID: {row[0]}, Nome: {row[1]}, Colunas: {cols[:50]}... (Valid JSON: {is_json})")
        
    print("\n--- Usuarios ---")
    cursor.execute("SELECT id, username, is_admin FROM usuarios")
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Username: {row[1]}, Admin: {row[2]}")
        
    conn.close()

if __name__ == "__main__":
    check_db()
