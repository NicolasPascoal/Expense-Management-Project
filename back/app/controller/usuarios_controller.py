import datetime

import psycopg2

from app.database.db import get_db_connection
from app.utils.permissions import PAPEIS_VALIDOS
from werkzeug.security import check_password_hash, generate_password_hash

# Mesmo mínimo do cadastro público (signup_controller.PASSWORD_MIN)
SENHA_MIN = 6

def get_todos_usuarios(empresa_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # projeto_ids (Tarefa 6.2): obras às quais o usuário está vinculado —
    # irrelevante para admin, que acessa todas.
    cursor.execute('''
        SELECT u.id, u.username, u.is_admin, u.role, u.ativo,
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

def _admins_ativos_travados(cursor, empresa_id):
    """ids dos admins ativos da empresa, com as linhas travadas até o fim da
    transação — duas operações simultâneas não conseguem, juntas, deixar a
    empresa sem nenhum admin."""
    cursor.execute(
        "SELECT id FROM usuarios WHERE empresa_id = ? AND is_admin = 1 AND ativo FOR UPDATE",
        (empresa_id,)
    )
    return {row['id'] for row in cursor.fetchall()}


def _buscar_usuario(cursor, usuario_id, empresa_id):
    cursor.execute(
        "SELECT id, username, is_admin, role, ativo FROM usuarios WHERE id = ? AND empresa_id = ?",
        (usuario_id, empresa_id)
    )
    return cursor.fetchone()


# As funções abaixo retornam (resposta, status_code). Retornos antecipados
# dentro do try: close() devolve a conexão ao pool, que faz rollback e
# libera as travas.

def desativar_usuario(usuario_id, empresa_id, solicitante_id):
    """Substitui a antiga exclusão: apagar removia em cascata tarefas e
    requisições da pessoa. Desativado, perde o acesso na hora (a autenticação
    consulta `ativo`) e o histórico fica."""
    if usuario_id == solicitante_id:
        return {"erro": "Você não pode desativar o seu próprio acesso"}, 400
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        admins = _admins_ativos_travados(cursor, empresa_id)
        usuario = _buscar_usuario(cursor, usuario_id, empresa_id)
        if usuario is None:
            return {"erro": "Não encontrado"}, 404
        if admins == {usuario_id}:
            return {"erro": "Não é possível desativar o último administrador da empresa"}, 400
        cursor.execute("UPDATE usuarios SET ativo = FALSE WHERE id = ?", (usuario_id,))
        conn.commit()
        return {"id": usuario_id, "ativo": False}, 200
    finally:
        conn.close()


def reativar_usuario(usuario_id, empresa_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if _buscar_usuario(cursor, usuario_id, empresa_id) is None:
            return {"erro": "Não encontrado"}, 404
        cursor.execute("UPDATE usuarios SET ativo = TRUE WHERE id = ?", (usuario_id,))
        conn.commit()
        return {"id": usuario_id, "ativo": True}, 200
    finally:
        conn.close()


def alterar_papel(usuario_id, role, empresa_id, solicitante_id):
    """is_admin é derivado do papel (role='admin'), para os dois campos
    nunca divergirem."""
    if role not in PAPEIS_VALIDOS:
        return {"erro": "Papel inválido"}, 400
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        admins = _admins_ativos_travados(cursor, empresa_id)
        usuario = _buscar_usuario(cursor, usuario_id, empresa_id)
        if usuario is None:
            return {"erro": "Não encontrado"}, 404
        perde_admin = bool(usuario['is_admin']) and role != 'admin'
        if perde_admin and usuario_id == solicitante_id:
            return {"erro": "Você não pode remover o seu próprio acesso de administrador"}, 400
        if perde_admin and admins == {usuario_id}:
            return {"erro": "Não é possível remover o último administrador da empresa"}, 400
        cursor.execute(
            "UPDATE usuarios SET role = ?, is_admin = ? WHERE id = ?",
            (role, 1 if role == 'admin' else 0, usuario_id)
        )
        conn.commit()
        return {"id": usuario_id, "role": role, "is_admin": role == 'admin'}, 200
    finally:
        conn.close()


def _validar_nova_senha(nova_senha):
    if not isinstance(nova_senha, str) or len(nova_senha) < SENHA_MIN:
        return {"erro": f"A senha precisa ter pelo menos {SENHA_MIN} caracteres"}, 400
    return None


def _gravar_senha(cursor, usuario_id, nova_senha):
    # UTC truncado no segundo: mesma resolução do `iat` do JWT, comparado em
    # auth_middleware — tokens emitidos antes disso deixam de valer.
    agora = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0, tzinfo=None)
    cursor.execute(
        "UPDATE usuarios SET password = ?, senha_alterada_em = ? WHERE id = ?",
        (generate_password_hash(nova_senha), agora, usuario_id)
    )


def redefinir_senha(usuario_id, nova_senha, empresa_id):
    """Admin redefine a senha de alguém da empresa — encerra as sessões
    abertas dessa pessoa."""
    erro = _validar_nova_senha(nova_senha)
    if erro:
        return erro
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if _buscar_usuario(cursor, usuario_id, empresa_id) is None:
            return {"erro": "Não encontrado"}, 404
        _gravar_senha(cursor, usuario_id, nova_senha)
        conn.commit()
        return {"mensagem": "Senha redefinida"}, 200
    finally:
        conn.close()


def alterar_propria_senha(usuario_id, senha_atual, nova_senha):
    erro = _validar_nova_senha(nova_senha)
    if erro:
        return erro
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM usuarios WHERE id = ?", (usuario_id,))
        usuario = cursor.fetchone()
        if usuario is None or not check_password_hash(usuario['password'], senha_atual or ''):
            return {"erro": "Senha atual incorreta"}, 400
        _gravar_senha(cursor, usuario_id, nova_senha)
        conn.commit()
        return {"mensagem": "Senha alterada"}, 200
    finally:
        conn.close()

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
