from flask import Blueprint, request, jsonify
from app.database.db import get_db_connection
from app.utils.auth_middleware import token_required, admin_required
import json

projeto_bp = Blueprint('projetos', __name__)

@projeto_bp.route('/projetos', methods=['GET'])
@token_required
def listar_projetos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projetos')
    projetos = [dict(row) for row in cursor.fetchall()]
    
    # Parse as colunas de JSON string para objeto
    for p in projetos:
        if p['colunas']:
            p['colunas'] = json.loads(p['colunas'])
        else:
            p['colunas'] = []
            
    conn.close()
    return jsonify(projetos)

@projeto_bp.route('/projetos', methods=['POST'])
@admin_required
def criar_projeto():
    dados = request.get_json()
    nome = dados.get('nome')
    colunas = dados.get('colunas', [])
    
    if not nome:
        return jsonify({'erro': 'Nome do projeto é obrigatório'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO projetos (nome, colunas) VALUES (?, ?)',
        (nome, json.dumps(colunas))
    )
    projeto_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': projeto_id, 'nome': nome, 'colunas': colunas}), 201

@projeto_bp.route('/projetos/<int:id>', methods=['PUT'])
@admin_required
def atualizar_projeto(id):
    dados = request.get_json()
    nome = dados.get('nome')
    colunas = dados.get('colunas')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if nome and colunas is not None:
        cursor.execute('UPDATE projetos SET nome = ?, colunas = ? WHERE id = ?', (nome, json.dumps(colunas), id))
    elif nome:
        cursor.execute('UPDATE projetos SET nome = ? WHERE id = ?', (nome, id))
    elif colunas is not None:
        cursor.execute('UPDATE projetos SET colunas = ? WHERE id = ?', (json.dumps(colunas), id))
        
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Projeto atualizado'})

@projeto_bp.route('/projetos/<int:id>', methods=['DELETE'])
@admin_required
def deletar_projeto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM projetos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Projeto removido'})
