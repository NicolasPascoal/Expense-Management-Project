from flask import Blueprint, request, jsonify, g
from app.controller.usuarios_controller import (
    get_todos_usuarios, criar_usuario, definir_projetos_usuario,
    desativar_usuario, reativar_usuario, alterar_papel, redefinir_senha, SENHA_MIN
)
from app.utils.auth_middleware import admin_required
from app.utils.auditoria import log_auditoria
from app.utils.permissions import PAPEIS_VALIDOS

usuarios_bp = Blueprint('usuarios', __name__)

USERNAME_MIN = 3  # mesmo mínimo do cadastro público


def _auditar(usuario_id, acao, detalhes=''):
    log_auditoria(g.user['empresa_id'], g.user['id'], 'usuario', usuario_id, acao, detalhes)


@usuarios_bp.route('/usuarios', methods=['GET'])
@admin_required
def listar_usuarios():
    return jsonify(get_todos_usuarios(g.user['empresa_id'])), 200

@usuarios_bp.route('/usuarios', methods=['POST'])
@admin_required
def novo_usuario():
    dados = request.get_json(silent=True) or {}
    username = (dados.get('username') or '').strip()
    password = dados.get('password')
    role = dados.get('role') or ('admin' if dados.get('is_admin') else 'prestador')

    if len(username) < USERNAME_MIN:
        return jsonify({'erro': f'Usuário precisa ter pelo menos {USERNAME_MIN} caracteres'}), 400
    if not isinstance(password, str) or len(password) < SENHA_MIN:
        return jsonify({'erro': f'A senha precisa ter pelo menos {SENHA_MIN} caracteres'}), 400
    if role not in PAPEIS_VALIDOS:
        return jsonify({'erro': 'Papel inválido'}), 400

    # is_admin derivado do papel — os dois campos nunca divergem
    res = criar_usuario(username, password, g.user['empresa_id'], role == 'admin', role)
    if 'erro' in res:
        return jsonify(res), 400
    _auditar(res['id'], 'criar', f'{username} ({role})')
    return jsonify(res), 201

@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])
@admin_required
def editar_usuario(id):
    dados = request.get_json(silent=True) or {}
    res, status_code = alterar_papel(id, dados.get('role'), g.user['empresa_id'], g.user['id'])
    if status_code == 200:
        _auditar(id, 'editar', f'papel -> {res["role"]}')
    return jsonify(res), status_code

@usuarios_bp.route('/usuarios/<int:id>/senha', methods=['PUT'])
@admin_required
def redefinir_senha_usuario(id):
    dados = request.get_json(silent=True) or {}
    res, status_code = redefinir_senha(id, dados.get('nova_senha'), g.user['empresa_id'])
    if status_code == 200:
        _auditar(id, 'editar', 'senha redefinida pelo admin')
    return jsonify(res), status_code

# DELETE mantido por compatibilidade, mas desativa em vez de apagar (apagar
# removia em cascata tarefas e requisições da pessoa).
@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@admin_required
def remover_usuario(id):
    res, status_code = desativar_usuario(id, g.user['empresa_id'], g.user['id'])
    if status_code == 200:
        _auditar(id, 'desativar')
    return jsonify(res), status_code

@usuarios_bp.route('/usuarios/<int:id>/reativar', methods=['POST'])
@admin_required
def reativar(id):
    res, status_code = reativar_usuario(id, g.user['empresa_id'])
    if status_code == 200:
        _auditar(id, 'reativar')
    return jsonify(res), status_code

@usuarios_bp.route('/usuarios/<int:id>/projetos', methods=['PUT'])
@admin_required
def atualizar_projetos_usuario(id):
    dados = request.get_json(silent=True) or {}
    res, status_code = definir_projetos_usuario(id, dados.get('projeto_ids'), g.user['empresa_id'])
    return jsonify(res), status_code
