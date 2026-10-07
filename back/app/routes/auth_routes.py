from flask import Blueprint, request, jsonify, g
from flask_limiter.util import get_remote_address
from app.controller.auth_controller import login_usuario
from app.controller.usuarios_controller import alterar_propria_senha
from app.extensions import limiter
from app.utils.auth_middleware import token_required

auth_bp = Blueprint('auth', __name__)


def _username_da_requisicao():
    dados = request.get_json(silent=True) or {}
    username = (dados.get('username') or '').strip().lower()
    # Sem username no corpo, cai para o IP — evita que todas as requisições
    # malformadas compartilhem um único balde de rate limit vazio.
    return username or get_remote_address()


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")  # por IP: barra varredura vinda de um único endereço
@limiter.limit("5 per minute;20 per hour", key_func=_username_da_requisicao)  # por conta
def login():
    dados = request.get_json()
    username = dados.get('username')
    password = dados.get('password')

    if not username or not password:
        return jsonify({'erro': 'Usuário e senha são obrigatórios'}), 400

    resultado = login_usuario(username, password)
    
    if resultado:
        return jsonify(resultado), 200
    
    return jsonify({'erro': 'Usuário ou senha inválidos'}), 401


@auth_bp.route('/me/senha', methods=['PUT'])
@limiter.limit("10 per hour")  # a senha atual é conferida aqui — mesma lógica do login
@token_required
def trocar_minha_senha():
    dados = request.get_json(silent=True) or {}
    nova_senha = dados.get('nova_senha')
    res, status_code = alterar_propria_senha(g.user['id'], dados.get('senha_atual'), nova_senha)
    if status_code != 200:
        return jsonify(res), status_code
    # A troca invalida os tokens anteriores, inclusive o desta requisição —
    # devolve um novo (mesmo formato do POST /login) para a pessoa seguir logada.
    return jsonify(login_usuario(g.user['username'], nova_senha)), 200
