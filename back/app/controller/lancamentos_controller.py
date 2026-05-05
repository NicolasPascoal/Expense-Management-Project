from app.database.db import get_db_connection
import json

def get_todos_lancamentos(projeto_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if projeto_id:
        cursor.execute("SELECT * FROM lancamentos_v2 WHERE projeto_id = ?", (projeto_id,))
    else:
        cursor.execute("SELECT * FROM lancamentos_v2")
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

def get_lancamento_por_id(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lancamentos_v2 WHERE id = ?", (id,))
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

def criar_lancamento(projeto_id, dados):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO lancamentos_v2 (projeto_id, dados)
        VALUES (?, ?)
    ''', (projeto_id, json.dumps(dados)))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return get_lancamento_por_id(novo_id)

def atualizar_lancamento(id, dados):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE lancamentos_v2 
        SET dados=?
        WHERE id = ?
    ''', (json.dumps(dados), id))
    conn.commit()
    conn.close()
    return get_lancamento_por_id(id)

def deletar_lancamento(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM lancamentos_v2 WHERE id = ?", (id,))
    if cursor.fetchone() is None:
        conn.close()
        return False
    cursor.execute("DELETE FROM lancamentos_v2 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return True
