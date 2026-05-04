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
    return jsonify(get_todos_lancamentos()), 200

@lancamentos_bp.route('/lancamentos/<int:id>', methods=['GET'])
@token_required
def obter_lancamento(id):
    res = get_lancamento_por_id(id)
    return jsonify(res) if res else (jsonify({'erro': 'Não encontrado'}), 404)

@lancamentos_bp.route('/lancamentos', methods=['POST'])
@token_required
def novo_lancamento():
    dados = request.get_json()
    if not dados or not dados.get('data'):
        return jsonify({'erro': 'Data obrigatória'}), 400
    return jsonify(criar_lancamento(dados)), 201

@lancamentos_bp.route('/lancamentos/<int:id>', methods=['PUT'])
@token_required
def editar_lancamento(id):
    dados = request.get_json()
    res = atualizar_lancamento(id, dados)
    return jsonify(res) if res else (jsonify({'erro': 'Não encontrado'}), 404)

@lancamentos_bp.route('/lancamentos/<int:id>', methods=['DELETE'])
@token_required
def remover_lancamento(id):
    return (jsonify({'mensagem': 'Removido'}), 200) if deletar_lancamento(id) else (jsonify({'erro': 'Não encontrado'}), 404)
