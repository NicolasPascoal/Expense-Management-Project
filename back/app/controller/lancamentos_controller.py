from app.database.db import get_db_connection

def get_todos_lancamentos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lancamentos")
    linhas = cursor.fetchall()
    conn.close()
    return [dict(linha) for linha in linhas]

def get_lancamento_por_id(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lancamentos WHERE id = ?", (id,))
    linha = cursor.fetchone()
    conn.close()
    return dict(linha) if linha else None

def criar_lancamento(dados):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO lancamentos (data, categoria, item, fornecedor, quantidade, unitario, valor, forma, conta, obs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        dados.get('data'), dados.get('categoria'), dados.get('item'),
        dados.get('fornecedor'), dados.get('quantidade'), dados.get('unitario'),
        dados.get('valor'), dados.get('forma'), dados.get('conta'), dados.get('obs')
    ))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return get_lancamento_por_id(novo_id)

def atualizar_lancamento(id, dados):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE lancamentos 
        SET data=?, categoria=?, item=?, fornecedor=?, quantidade=?, unitario=?, valor=?, forma=?, conta=?, obs=?
        WHERE id = ?
    ''', (
        dados.get('data'), dados.get('categoria'), dados.get('item'),
        dados.get('fornecedor'), dados.get('quantidade'), dados.get('unitario'),
        dados.get('valor'), dados.get('forma'), dados.get('conta'), dados.get('obs'),
        id
    ))
    conn.commit()
    conn.close()
    return get_lancamento_por_id(id)

def deletar_lancamento(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM lancamentos WHERE id = ?", (id,))
    if cursor.fetchone() is None:
        conn.close()
        return False
    cursor.execute("DELETE FROM lancamentos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return True
