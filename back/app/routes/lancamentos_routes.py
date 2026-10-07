from flask import Blueprint, request, jsonify, g
from app.controller.lancamentos_controller import (
    get_todos_lancamentos, get_lancamento_por_id, criar_lancamento,
    atualizar_lancamento, deletar_lancamento, criar_lancamento_de_requisicao
)
from app.utils.auth_middleware import token_required, non_prestador_required
from app.utils.tenant import usuario_acessa_projeto, usuario_restrito
from app.utils.auditoria import log_auditoria
from app.utils.permissions import tem_permissao

lancamentos_bp = Blueprint('lancamentos', __name__)

@lancamentos_bp.route('/lancamentos', methods=['GET'])
@token_required
@non_prestador_required
def listar_lancamentos():
    projeto_id = request.args.get('projeto_id')
    return jsonify(get_todos_lancamentos(g.user['empresa_id'], projeto_id, usuario_restrito(g.user))), 200

@lancamentos_bp.route('/lancamentos/<int:id>', methods=['GET'])
@token_required
@non_prestador_required
def obter_lancamento(id):
    res = get_lancamento_por_id(id, g.user['empresa_id'], usuario_restrito(g.user))
    return jsonify(res) if res else (jsonify({'erro': 'Não encontrado'}), 404)

@lancamentos_bp.route('/lancamentos', methods=['POST'])
@token_required
@non_prestador_required
def novo_lancamento():
    dados = request.get_json()
    projeto_id = dados.get('projeto_id')

    if not projeto_id:
        return jsonify({'erro': 'projeto_id é obrigatório'}), 400

    if not usuario_acessa_projeto(g.user, projeto_id):
        return jsonify({'erro': 'projeto_id inválido'}), 400

    # Removemos projeto_id/requisicao_id do corpo para salvar apenas os dados dinâmicos no JSON
    payload = {k: v for k, v in dados.items() if k not in ['projeto_id', 'requisicao_id']}
    detalhes = payload.get('item') or payload.get('categoria') or ''

    # Tarefa 7.5: lançamento gerado a partir de uma requisição de material
    requisicao_id = dados.get('requisicao_id')
    if requisicao_id is not None:
        if not tem_permissao(g.user, 'aprovar_requisicoes'):
            return jsonify({'erro': 'Acesso negado para este papel de usuário.'}), 403
        if not isinstance(requisicao_id, int) or isinstance(requisicao_id, bool):
            return jsonify({'erro': 'requisicao_id inválido'}), 400
        novo, status_code = criar_lancamento_de_requisicao(projeto_id, payload, g.user['empresa_id'], requisicao_id)
        if status_code != 201:
            return jsonify(novo), status_code
        detalhes = f'{detalhes} (requisição #{requisicao_id})'
    else:
        novo = criar_lancamento(projeto_id, payload, g.user['empresa_id'])

    log_auditoria(g.user['empresa_id'], g.user['id'], 'lancamento', novo['id'], 'criar', detalhes)
    return jsonify(novo), 201

@lancamentos_bp.route('/lancamentos/<int:id>', methods=['PUT'])
@token_required
@non_prestador_required
def editar_lancamento(id):
    dados = request.get_json()
    # No PUT, geralmente mantemos o projeto_id original, mas limpamos o payload
    payload = {k: v for k, v in dados.items() if k not in ['id', 'projeto_id', 'requisicao_id']}
    res = atualizar_lancamento(id, payload, g.user['empresa_id'], usuario_restrito(g.user))
    if not res:
        return jsonify({'erro': 'Não encontrado'}), 404
    log_auditoria(g.user['empresa_id'], g.user['id'], 'lancamento', id, 'editar', payload.get('item') or payload.get('categoria') or '')
    return jsonify(res)

@lancamentos_bp.route('/lancamentos/<int:id>', methods=['DELETE'])
@token_required
@non_prestador_required
def remover_lancamento(id):
    if not deletar_lancamento(id, g.user['empresa_id'], usuario_restrito(g.user)):
        return jsonify({'erro': 'Não encontrado'}), 404
    log_auditoria(g.user['empresa_id'], g.user['id'], 'lancamento', id, 'excluir', '')
    return jsonify({'mensagem': 'Removido'}), 200
