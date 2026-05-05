from app.database.db import get_db_connection

# Categorias
def get_todas_categorias(projeto_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if projeto_id:
        cursor.execute("SELECT * FROM categorias WHERE projeto_id = ? ORDER BY nome ASC", (projeto_id,))
    else:
        cursor.execute("SELECT * FROM categorias ORDER BY nome ASC")
    linhas = cursor.fetchall()
    conn.close()
    return [dict(linha) for linha in linhas]

def criar_categoria(nome, projeto_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categorias (nome, projeto_id) VALUES (?, ?)", (nome, projeto_id))
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return {"id": novo_id, "nome": nome, "projeto_id": projeto_id}
    except Exception as e:
        conn.close()
        return {"erro": str(e)}

def deletar_categoria(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categorias WHERE id = ?", (id,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0

# Contas
def get_todas_contas(projeto_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if projeto_id:
        cursor.execute("SELECT * FROM contas WHERE projeto_id = ? ORDER BY nome ASC", (projeto_id,))
    else:
        cursor.execute("SELECT * FROM contas ORDER BY nome ASC")
    linhas = cursor.fetchall()
    conn.close()
    return [dict(linha) for linha in linhas]

def criar_conta(nome, projeto_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO contas (nome, projeto_id) VALUES (?, ?)", (nome, projeto_id))
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return {"id": novo_id, "nome": nome, "projeto_id": projeto_id}
    except Exception as e:
        conn.close()
        return {"erro": str(e)}

def deletar_conta(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contas WHERE id = ?", (id,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0
