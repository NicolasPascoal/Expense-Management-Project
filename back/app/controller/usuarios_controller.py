import psycopg2

from app.database.db import get_db_connection
from werkzeug.security import generate_password_hash

def get_todos_usuarios(empresa_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # projeto_ids (Tarefa 6.2): obras às quais o usuário está vinculado —
    # irrelevante para admin, que acessa todas.
    cursor.execute('''
        SELECT u.id, u.username, u.is_admin, u.role,
               COALESCE(
                   (SELECT array_agg(up.projeto_id ORDER BY up.projeto_id)
                    FROM usuario_projetos up WHERE up.usuario_id = u.id),
                   '{}'
               ) AS projeto_ids
        FROM usuarios u
        WHERE u.empresa_id = ?
    ''', (empresa_id,))
    usuarios = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return usuarios

def criar_usuario(username, password, empresa_id, is_admin=0, role='prestador'):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (username, password, is_admin, role, empresa_id) VALUES (?, ?, ?, ?, ?)",
            (username, generate_password_hash(password), 1 if is_admin else 0, role, empresa_id)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        return {"id": novo_id, "username": username, "is_admin": bool(is_admin), "role": role, "empresa_id": empresa_id}
    except psycopg2.errors.UniqueViolation:
        # username já cadastrado (UNIQUE global, ver STATUS.md Tarefa 1.1) — erro de
        # validação esperado, não bug interno: não deve virar 500.
        conn.rollback()
        return {"erro": "Nome de usuário já está em uso"}
    finally:
        conn.close()

def deletar_usuario(id, empresa_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Impede deletar o admin principal (id 1)
    if id == 1:
        conn.close()
        return False
    cursor.execute("DELETE FROM usuarios WHERE id = ? AND empresa_id = ?", (id, empresa_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def definir_projetos_usuario(usuario_id, projeto_ids, empresa_id):
    """Substitui o conjunto de obras vinculadas a um usuário (Tarefa 6.2).
    Retorna (resposta, status_code). Valida que usuário e todas as obras são
    da empresa — nunca vincula a obra de outro tenant."""
    if not isinstance(projeto_ids, list) or not all(isinstance(p, int) and not isinstance(p, bool) for p in projeto_ids):
        return {"erro": "projeto_ids precisa ser uma lista de ids"}, 400
    projeto_ids = sorted(set(projeto_ids))

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT is_admin FROM usuarios WHERE id = ? AND empresa_id = ?", (usuario_id, empresa_id))
        usuario = cursor.fetchone()
        if usuario is None:
            return {"erro": "Não encontrado"}, 404
        if usuario['is_admin']:
            return {"erro": "Administradores já acessam todas as obras"}, 400

        if projeto_ids:
            cursor.execute(
                "SELECT COUNT(*) FROM projetos WHERE empresa_id = ? AND id = ANY(?)",
                (empresa_id, projeto_ids)
            )
            if cursor.fetchone()[0] != len(projeto_ids):
                return {"erro": "projeto_ids inválido"}, 400

        cursor.execute("DELETE FROM usuario_projetos WHERE usuario_id = ?", (usuario_id,))
        for projeto_id in projeto_ids:
            cursor.execute(
                "INSERT INTO usuario_projetos (usuario_id, projeto_id) VALUES (?, ?)",
                (usuario_id, projeto_id)
            )
        conn.commit()
        return {"id": usuario_id, "projeto_ids": projeto_ids}, 200
    finally:
        conn.close()
