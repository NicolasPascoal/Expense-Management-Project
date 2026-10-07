from app.database.db import get_db_connection
from app.utils.tenant import filtro_vinculo

# usuario_id (Tarefa 6.2): quando informado, restringe às obras vinculadas a
# esse usuário; None = todas as obras da empresa (admin).

def get_entradas(empresa_id, projeto_id=None, usuario_id=None):
    vinculo, params_vinculo = filtro_vinculo(usuario_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    if projeto_id:
        cursor.execute('''
            SELECT e.* FROM entradas e
            JOIN projetos p ON e.projeto_id = p.id
            WHERE e.projeto_id = ? AND p.empresa_id = ?''' + vinculo + '''
            ORDER BY e.criado_em DESC
        ''', (projeto_id, empresa_id) + params_vinculo)
    else:
        cursor.execute('''
            SELECT e.* FROM entradas e
            JOIN projetos p ON e.projeto_id = p.id
            WHERE p.empresa_id = ?''' + vinculo + '''
            ORDER BY e.criado_em DESC
        ''', (empresa_id,) + params_vinculo)
    linhas = cursor.fetchall()
    conn.close()
    return [dict(linha) for linha in linhas]

def criar_entrada(projeto_id, descricao, valor, data):
    """O chamador (rota) deve validar antes que o usuário acessa projeto_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO entradas (projeto_id, descricao, valor, data) VALUES (?, ?, ?, ?)",
        (projeto_id, descricao, valor, data)
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return {"id": novo_id, "projeto_id": projeto_id, "descricao": descricao, "valor": valor, "data": data}

def deletar_entrada(id, empresa_id, usuario_id=None):
    vinculo, params_vinculo = filtro_vinculo(usuario_id, 'projeto_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM entradas
        WHERE id = ? AND projeto_id IN (SELECT id FROM projetos WHERE empresa_id = ?)
    ''' + vinculo, (id, empresa_id) + params_vinculo)
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0
