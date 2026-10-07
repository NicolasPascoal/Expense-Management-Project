import datetime
import jwt
import os
from functools import wraps
from flask import request, jsonify, g

from app.database.db import get_db_connection
from app.utils.permissions import tem_permissao

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "FATAL: A variavel de ambiente JWT_SECRET_KEY nao esta definida no .env! "
        "Gere uma chave segura e adicione ao seu arquivo .env antes de iniciar o servidor."
    )

def _autenticar():
    """
    Ponto único de autenticação (Tarefa 1.3): decodifica o token do header e
    popula g.user com o payload completo (id, username, is_admin, role, empresa_id).
    Retorna uma resposta de erro pronta, ou None se autenticado com sucesso.
    Todo decorator de autorização parte daqui — nunca decodificar token em outro lugar.
    """
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'erro': 'Token de autorização ausente!'}), 401

    try:
        # Remove o prefixo 'Bearer ' se existir
        if token.startswith('Bearer '):
            token = token.split(" ", 1)[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({'erro': 'Token expirado!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'erro': 'Token inválido!'}), 401

    # Revogação imediata (pacote "usuários e acesso"): o token sozinho não
    # basta — usuário apagado ou desativado perde o acesso na hora, e papel/
    # admin/empresa vêm do banco, então uma mudança de papel vale já na
    # próxima requisição (antes valia o que estava no token por até 24h).
    usuario = _usuario_do_banco(payload.get('id'))
    if usuario is None or not usuario['ativo']:
        return jsonify({'erro': 'Sessão inválida. Faça login novamente.'}), 401
    if _emitido_antes_da_troca_de_senha(payload, usuario['senha_alterada_em']):
        return jsonify({'erro': 'Sua senha foi alterada. Faça login novamente.'}), 401

    g.user = {
        **payload,
        'username': usuario['username'],
        'is_admin': bool(usuario['is_admin']),
        'role': usuario['role'],
        'empresa_id': usuario['empresa_id'],
    }
    return None


def _usuario_do_banco(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, is_admin, role, empresa_id, ativo, senha_alterada_em FROM usuarios WHERE id = ?",
        (usuario_id,)
    )
    usuario = cursor.fetchone()
    conn.close()
    return usuario


def _emitido_antes_da_troca_de_senha(payload, senha_alterada_em):
    """senha_alterada_em é gravado em UTC, truncado no segundo (mesma
    resolução do `iat` do JWT). Token sem `iat` (emitido antes desta
    mudança) conta como anterior a qualquer troca de senha."""
    if senha_alterada_em is None:
        return False
    alterada = senha_alterada_em.replace(tzinfo=datetime.timezone.utc).timestamp()
    iat = payload.get('iat')
    return iat is None or iat < alterada

def token_required(f):
    """Exige usuário autenticado; popula g.user com o payload completo do token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        erro = _autenticar()
        if erro:
            return erro
        return f(*args, **kwargs)
    return decorated

def non_prestador_required(f):
    """Exige a permissão 'acesso_financeiro' (Tarefa 6.1) — usar depois de
    @token_required, que já populou g.user. Nome mantido por compatibilidade
    com as rotas existentes (lançamentos/categorias/contas/orçamentos/
    entradas/auditoria); o que mudou foi a checagem interna: antes era
    "libera tudo exceto role='prestador'" (allow-all-except), agora é uma
    lista de permissão positiva — um papel novo/desconhecido não passa mais
    por acidente (era o bug documentado do role='user')."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not tem_permissao(g.user, 'acesso_financeiro'):
            return jsonify({'erro': 'Acesso negado para este papel de usuário.'}), 403
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Exige usuário autenticado E admin; popula g.user com o payload completo do token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        erro = _autenticar()
        if erro:
            return erro
        if not g.user.get('is_admin'):
            return jsonify({'erro': 'Acesso negado. Apenas administradores!'}), 403
        return f(*args, **kwargs)
    return decorated

def permissao_required(nome_permissao):
    """Exige usuário autenticado com a permissão indicada (Tarefa 6.1) —
    is_admin sempre passa. Usar como @permissao_required('nome_da_permissao')."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            erro = _autenticar()
            if erro:
                return erro
            if not tem_permissao(g.user, nome_permissao):
                return jsonify({'erro': 'Acesso negado para este papel de usuário.'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
