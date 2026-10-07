from app.database.db import get_db_connection
from app.utils.tenant import filtro_vinculo

# usuario_id (Tarefa 6.2): quando informado, restringe às obras vinculadas a
# esse usuário; None = todas as obras da empresa (admin).

# Categorias
def get_todas_categorias(empresa_id, projeto_id=None, usuario_id=None):
    vinculo, params_vinculo = filtro_vinculo(usuario_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    if projeto_id:
        cursor.execute('''
            SELECT c.* FROM categorias c
            JOIN projetos p ON c.projeto_id = p.id
            WHERE c.projeto_id = ? AND p.empresa_id = ?''' + vinculo + '''
            ORDER BY c.nome ASC
        ''', (projeto_id, empresa_id) + params_vinculo)
    else:
        cursor.execute('''
            SELECT c.* FROM categorias c
            JOIN projetos p ON c.projeto_id = p.id
            WHERE p.empresa_id = ?''' + vinculo + '''
            ORDER BY c.nome ASC
        ''', (empresa_id,) + params_vinculo)
    linhas = cursor.fetchall()
    conn.close()
    return [dict(linha) for linha in linhas]

def criar_categoria(nome, projeto_id):
    """O chamador (rota) deve validar antes que o usuário acessa projeto_id."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categorias (nome, projeto_id) VALUES (?, ?)", (nome, projeto_id))
        conn.commit()
        novo_id = cursor.lastrowid
        return {"id": novo_id, "nome": nome, "projeto_id": projeto_id}
    finally:
        conn.close()

def deletar_categoria(id, empresa_id, usuario_id=None):
    vinculo, params_vinculo = filtro_vinculo(usuario_id, 'projeto_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM categorias
        WHERE id = ? AND projeto_id IN (SELECT id FROM projetos WHERE empresa_id = ?)
    ''' + vinculo, (id, empresa_id) + params_vinculo)
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0

# Contas
def get_todas_contas(empresa_id, projeto_id=None, usuario_id=None):
    vinculo, params_vinculo = filtro_vinculo(usuario_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    if projeto_id:
        cursor.execute('''
            SELECT c.* FROM contas c
            JOIN projetos p ON c.projeto_id = p.id
            WHERE c.projeto_id = ? AND p.empresa_id = ?''' + vinculo + '''
            ORDER BY c.nome ASC
        ''', (projeto_id, empresa_id) + params_vinculo)
    else:
        cursor.execute('''
            SELECT c.* FROM contas c
            JOIN projetos p ON c.projeto_id = p.id
            WHERE p.empresa_id = ?''' + vinculo + '''
            ORDER BY c.nome ASC
        ''', (empresa_id,) + params_vinculo)
    linhas = cursor.fetchall()
    conn.close()
    return [dict(linha) for linha in linhas]

def criar_conta(nome, projeto_id):
    """O chamador (rota) deve validar antes que o usuário acessa projeto_id."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contas (nome, projeto_id) VALUES (?, ?)", (nome, projeto_id))
        conn.commit()
        novo_id = cursor.lastrowid
        return {"id": novo_id, "nome": nome, "projeto_id": projeto_id}
    finally:
        conn.close()

def deletar_conta(id, empresa_id, usuario_id=None):
    vinculo, params_vinculo = filtro_vinculo(usuario_id, 'projeto_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM contas
        WHERE id = ? AND projeto_id IN (SELECT id FROM projetos WHERE empresa_id = ?)
    ''' + vinculo, (id, empresa_id) + params_vinculo)
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0
