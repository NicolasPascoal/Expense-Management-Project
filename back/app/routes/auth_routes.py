from flask import Blueprint, request, jsonify
from app.controller.auth_controller import login_usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
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
