from app.database.db import get_db_connection

def get_tarefas(usuario_id, is_admin):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if is_admin:
        # Admin vê todas as tarefas com info do prestador
        cursor.execute('''
            SELECT t.*, u.username as prestador_nome 
            FROM tarefas t
            LEFT JOIN usuarios u ON t.prestador_id = u.id
            ORDER BY t.data_criacao DESC
        ''')
    else:
        # Prestador vê apenas as suas tarefas
        cursor.execute('''
            SELECT t.*, u.username as prestador_nome 
            FROM tarefas t
            LEFT JOIN usuarios u ON t.prestador_id = u.id
            WHERE t.prestador_id = ?
            ORDER BY t.data_criacao DESC
        ''', (usuario_id,))
        
    tarefas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tarefas

def criar_tarefa(dados):
    titulo = dados.get('titulo')
    descricao = dados.get('descricao', '')
    prestador_id = dados.get('prestador_id')
    status = dados.get('status', 'Pendente')
    observacoes = dados.get('observacoes', '')

    if not titulo or not prestador_id:
        return {'erro': 'Título e Prestador são obrigatórios'}, 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO tarefas (titulo, descricao, prestador_id, status, observacoes)
            VALUES (?, ?, ?, ?, ?)
        ''', (titulo, descricao, prestador_id, status, observacoes))
        conn.commit()
        novo_id = cursor.lastrowid
    except Exception as e:
        conn.close()
        return {'erro': f'Erro ao criar tarefa: {str(e)}'}, 500
        
    conn.close()
    return {'mensagem': 'Tarefa criada com sucesso!', 'id': novo_id}, 201

def atualizar_tarefa(tarefa_id, dados, usuario_id, is_admin):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se a tarefa existe e a quem pertence
    cursor.execute('SELECT prestador_id FROM tarefas WHERE id = ?', (tarefa_id,))
    tarefa = cursor.fetchone()

    if not tarefa:
        conn.close()
        return {'erro': 'Tarefa não encontrada'}, 404

    if not is_admin and tarefa['prestador_id'] != usuario_id:
        conn.close()
        return {'erro': 'Acesso negado'}, 403

    try:
        if is_admin:
            # Admin pode atualizar tudo
            titulo = dados.get('titulo')
            descricao = dados.get('descricao')
            prestador_id = dados.get('prestador_id')
            status = dados.get('status')
            observacoes = dados.get('observacoes')
            
            updates = []
            params = []
            
            if titulo is not None:
                updates.append("titulo = ?")
                params.append(titulo)
            if descricao is not None:
                updates.append("descricao = ?")
                params.append(descricao)
            if prestador_id is not None:
                updates.append("prestador_id = ?")
                params.append(prestador_id)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if observacoes is not None:
                updates.append("observacoes = ?")
                params.append(observacoes)
                
            if not updates:
                conn.close()
                return {'mensagem': 'Nenhum dado para atualizar'}, 200
                
            query = f"UPDATE tarefas SET {', '.join(updates)} WHERE id = ?"
            params.append(tarefa_id)
            cursor.execute(query, tuple(params))
            
        else:
            # Prestador só pode atualizar status e observações
            status = dados.get('status')
            observacoes = dados.get('observacoes')
            
            updates = []
            params = []
            
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if observacoes is not None:
                updates.append("observacoes = ?")
                params.append(observacoes)
                
            if not updates:
                conn.close()
                return {'mensagem': 'Nenhum dado para atualizar'}, 200
                
            query = f"UPDATE tarefas SET {', '.join(updates)} WHERE id = ?"
            params.append(tarefa_id)
            cursor.execute(query, tuple(params))

        conn.commit()
    except Exception as e:
        conn.close()
        return {'erro': f'Erro ao atualizar tarefa: {str(e)}'}, 500

    conn.close()
    return {'mensagem': 'Tarefa atualizada com sucesso!'}, 200

def deletar_tarefa(tarefa_id, is_admin):
    if not is_admin:
        return {'erro': 'Acesso negado'}, 403

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tarefas WHERE id = ?', (tarefa_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        return {'erro': 'Tarefa não encontrada'}, 404
        
    conn.commit()
    conn.close()
    return {'mensagem': 'Tarefa deletada com sucesso!'}, 200
