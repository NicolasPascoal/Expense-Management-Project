import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    username = 'nicolas'
    password = 'nicolas12'
    is_admin = 1
    
    hashed_password = generate_password_hash(password)
    
    # Check if user exists
    cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user:
        print(f"User {username} already exists. Updating password, admin status and role...")
        cursor.execute("UPDATE usuarios SET password = ?, is_admin = ?, role = ? WHERE username = ?", 
                       (hashed_password, is_admin, 'admin', username))
    else:
        print(f"Creating user {username}...")
        cursor.execute("INSERT INTO usuarios (username, password, is_admin, role) VALUES (?, ?, ?, ?)", 
                       (username, hashed_password, is_admin, 'admin'))
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    create_admin()
