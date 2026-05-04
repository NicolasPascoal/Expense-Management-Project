from functools import wraps
from flask import request, jsonify

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        # Permite um token fixo para facilitar testes no Postman
        if token == 'token-de-teste':
            return f(*args, **kwargs)
            
        if not token:
            return jsonify({'erro': 'Token de autorização ausente!'}), 401
            
        # No futuro, aqui entrará a validação real do JWT (PyJWT)
        # return jsonify({'erro': 'Token inválido!'}), 401
            
        return f(*args, **kwargs)
    return decorated
