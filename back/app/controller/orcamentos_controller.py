from app.database.db import get_db_connection
from app.utils.tenant import filtro_vinculo

# usuario_id (Tarefa 6.2): quando informado, restringe às obras vinculadas a
# esse usuário; None = todas as obras da empresa (admin).

def get_orcamentos(empresa_id, projeto_id=None, usuario_id=None):
    vinculo, params_vinculo = filtro_vinculo(usuario_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    if projeto_id:
        cursor.execute('''
            SELECT o.id, o.projeto_id, o.categoria_id, o.valor_orcado, c.nome AS categoria_nome
            FROM orcamentos o
            JOIN projetos p ON o.projeto_id = p.id
            JOIN categorias c ON o.categoria_id = c.id
            WHERE o.projeto_id = ? AND p.empresa_id = ?''' + vinculo + '''
            ORDER BY c.nome ASC
        ''', (projeto_id, empresa_id) + params_vinculo)
    else:
        cursor.execute('''
            SELECT o.id, o.projeto_id, o.categoria_id, o.valor_orcado, c.nome AS categoria_nome
            FROM orcamentos o
            JOIN projetos p ON o.projeto_id = p.id
            JOIN categorias c ON o.categoria_id = c.id
            WHERE p.empresa_id = ?''' + vinculo + '''
            ORDER BY c.nome ASC
        ''', (empresa_id,) + params_vinculo)
    linhas = cursor.fetchall()
    conn.close()
    return [dict(linha) for linha in linhas]

def upsert_orcamento(projeto_id, categoria_id, valor_orcado):
    """O chamador (rota) deve validar antes que o usuário acessa projeto_id e que categoria_id é desse projeto."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM orcamentos WHERE projeto_id = ? AND categoria_id = ?",
        (projeto_id, categoria_id)
    )
    existente = cursor.fetchone()

    if existente:
        cursor.execute(
            "UPDATE orcamentos SET valor_orcado = ? WHERE id = ?",
            (valor_orcado, existente['id'])
        )
        orcamento_id = existente['id']
    else:
        cursor.execute(
            "INSERT INTO orcamentos (projeto_id, categoria_id, valor_orcado) VALUES (?, ?, ?)",
            (projeto_id, categoria_id, valor_orcado)
        )
        orcamento_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return {"id": orcamento_id, "projeto_id": projeto_id, "categoria_id": categoria_id, "valor_orcado": valor_orcado}

def deletar_orcamento(id, empresa_id, usuario_id=None):
    vinculo, params_vinculo = filtro_vinculo(usuario_id, 'projeto_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM orcamentos
        WHERE id = ? AND projeto_id IN (SELECT id FROM projetos WHERE empresa_id = ?)
    ''' + vinculo, (id, empresa_id) + params_vinculo)
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0
