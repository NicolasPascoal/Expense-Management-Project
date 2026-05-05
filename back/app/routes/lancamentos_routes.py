from flask import Blueprint, request, jsonify
from app.controller.lancamentos_controller import (
    get_todos_lancamentos, get_lancamento_por_id, criar_lancamento,
    atualizar_lancamento, deletar_lancamento
)
from app.utils.auth_middleware import token_required

lancamentos_bp = Blueprint('lancamentos', __name__)

@lancamentos_bp.route('/lancamentos', methods=['GET'])
@token_required
def listar_lancamentos():
    projeto_id = request.args.get('projeto_id')
    return jsonify(get_todos_lancamentos(projeto_id)), 200

@lancamentos_bp.route('/lancamentos/<int:id>', methods=['GET'])
@token_required
def obter_lancamento(id):
    res = get_lancamento_por_id(id)
    return jsonify(res) if res else (jsonify({'erro': 'Não encontrado'}), 404)

@lancamentos_bp.route('/lancamentos', methods=['POST'])
@token_required
def novo_lancamento():
    dados = request.get_json()
    projeto_id = dados.get('projeto_id')
    
    if not projeto_id:
        return jsonify({'erro': 'projeto_id é obrigatório'}), 400
        
    # Removemos o projeto_id do corpo para salvar apenas os dados dinâmicos no JSON
    payload = {k: v for k, v in dados.items() if k != 'projeto_id'}
    
    return jsonify(criar_lancamento(projeto_id, payload)), 201

@lancamentos_bp.route('/lancamentos/<int:id>', methods=['PUT'])
@token_required
def editar_lancamento(id):
    dados = request.get_json()
    # No PUT, geralmente mantemos o projeto_id original, mas limpamos o payload
    payload = {k: v for k, v in dados.items() if k not in ['id', 'projeto_id']}
    res = atualizar_lancamento(id, payload)
    return jsonify(res) if res else (jsonify({'erro': 'Não encontrado'}), 404)

@lancamentos_bp.route('/lancamentos/<int:id>', methods=['DELETE'])
@token_required
def remover_lancamento(id):
    return (jsonify({'mensagem': 'Removido'}), 200) if deletar_lancamento(id) else (jsonify({'erro': 'Não encontrado'}), 404)
