from app.database.db import get_db_connection
from werkzeug.security import generate_password_hash

def create_admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    username = 'nicolas'
    password = 'nicolas12'
    is_admin = 1
    
    hashed_password = generate_password_hash(password)
    
    # Verifica se o usuário já existe
    cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user:
        print(f"Usuário {username} já existe. Atualizando senha, privilégios de admin e cargo...")
        cursor.execute("UPDATE usuarios SET password = ?, is_admin = ?, role = ? WHERE username = ?", 
                       (hashed_password, is_admin, 'admin', username))
    else:
        print(f"Criando usuário {username}...")
        cursor.execute("INSERT INTO usuarios (username, password, is_admin, role) VALUES (?, ?, ?, ?)", 
                       (username, hashed_password, is_admin, 'admin'))
    
    conn.commit()
    conn.close()
    print("Sucesso!")

if __name__ == "__main__":
    create_admin()
