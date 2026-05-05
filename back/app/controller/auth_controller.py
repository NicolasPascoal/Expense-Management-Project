import jwt
import datetime
from app.database.db import get_db_connection
from werkzeug.security import check_password_hash

SECRET_KEY = "sua_chave_secreta_super_segura" # Em produção, use env var

def login_usuario(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    usuario = cursor.fetchone()
    conn.close()

    if usuario and check_password_hash(usuario['password'], password):
        token = jwt.encode({
            'id': usuario['id'],
            'username': usuario['username'],
            'is_admin': usuario['is_admin'],
            'role': usuario['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")
        
        return {
            'token': token,
            'user': {
                'id': usuario['id'],
                'username': usuario['username'],
                'is_admin': bool(usuario['is_admin']),
                'role': usuario['role']
            }
        }
    
    return None
