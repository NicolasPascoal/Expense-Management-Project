from app.database.db import get_db_connection
from app.utils.tenant import filtro_vinculo
import json

# usuario_id (Tarefa 6.2): quando informado, restringe às obras vinculadas a
# esse usuário; None = todas as obras da empresa (admin).

def get_todos_lancamentos(empresa_id, projeto_id=None, usuario_id=None):
    vinculo, params_vinculo = filtro_vinculo(usuario_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    if projeto_id:
        cursor.execute('''
            SELECT l.* FROM lancamentos_v2 l
            JOIN projetos p ON l.projeto_id = p.id
            WHERE l.projeto_id = ? AND p.empresa_id = ?
        ''' + vinculo, (projeto_id, empresa_id) + params_vinculo)
    else:
        cursor.execute('''
            SELECT l.* FROM lancamentos_v2 l
            JOIN projetos p ON l.projeto_id = p.id
            WHERE p.empresa_id = ?
        ''' + vinculo, (empresa_id,) + params_vinculo)
    linhas = cursor.fetchall()
    conn.close()

    resultado = []
    for linha in linhas:
        item = dict(linha)
        if item.get('dados'):
            try:
                dados_json = json.loads(item['dados'])
                # Mescla os dados do JSON no dicionário principal
                item.update(dados_json)
            except json.JSONDecodeError:
                pass
        resultado.append(item)
    return resultado

def get_lancamento_por_id(id, empresa_id, usuario_id=None):
    vinculo, params_vinculo = filtro_vinculo(usuario_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.* FROM lancamentos_v2 l
        JOIN projetos p ON l.projeto_id = p.id
        WHERE l.id = ? AND p.empresa_id = ?
    ''' + vinculo, (id, empresa_id) + params_vinculo)
    linha = cursor.fetchone()
    conn.close()
    if linha:
        item = dict(linha)
        if item.get('dados'):
            try:
                item.update(json.loads(item['dados']))
            except json.JSONDecodeError:
                pass
        return item
    return None

def criar_lancamento(projeto_id, dados, empresa_id):
    """O chamador (rota) deve validar antes que o usuário acessa projeto_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO lancamentos_v2 (projeto_id, dados)
        VALUES (?, ?)
    ''', (projeto_id, json.dumps(dados)))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return get_lancamento_por_id(novo_id, empresa_id)

def atualizar_lancamento(id, dados, empresa_id, usuario_id=None):
    if get_lancamento_por_id(id, empresa_id, usuario_id) is None:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE lancamentos_v2
        SET dados=?
        WHERE id = ?
    ''', (json.dumps(dados), id))
    conn.commit()
    conn.close()
    return get_lancamento_por_id(id, empresa_id)

def deletar_lancamento(id, empresa_id, usuario_id=None):
    if get_lancamento_por_id(id, empresa_id, usuario_id) is None:
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lancamentos_v2 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return True
