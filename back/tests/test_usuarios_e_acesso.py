"""
Testes do pacote "usuários e acesso" (preparação para instalar no servidor
de um cliente). Cobre: revogação imediata (desativado/apagado/papel mudado
valem na hora); troca e redefinição de senha invalidando sessões antigas;
desativar em vez de apagar; proteção contra a empresa ficar sem admin;
validação ao criar usuário; seed do admin inicial sem admin/admin; cadastro
público desligável.
"""
import datetime
import logging
import time

import jwt
import pytest
from flask import Flask
from werkzeug.security import check_password_hash

from app.controller.auth_controller import SECRET_KEY, login_usuario
from app.controller import usuarios_controller
from app.controller.usuarios_controller import criar_usuario
from app.database.modelUsuarios import create_usuarios_tables
from app.routes import auth_routes, usuarios_routes, signup_routes, lancamentos_routes

_app = Flask(__name__)


def _token(usuario, iat=None, **sobrescrever):
    payload = {
        'id': usuario['id'],
        'username': usuario['username'],
        'is_admin': bool(usuario['is_admin']),
        'role': usuario['role'],
        'empresa_id': usuario['empresa_id'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
    }
    if iat is not None:
        payload['iat'] = iat
    payload.update(sobrescrever)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def _chamar(rota, token, *args, method="GET", json=None):
    with _app.test_request_context("/", method=method, json=json, headers={"Authorization": f"Bearer {token}"}):
        res = rota(*args)
    resposta, status = res if isinstance(res, tuple) else (res, res.status_code)
    return resposta.get_json(), status


@pytest.fixture
def empresa(db_session):
    cursor = db_session.cursor()
    cursor.execute("INSERT INTO empresas (nome) VALUES (?)", ("Empresa Acesso",))
    empresa_id = cursor.lastrowid
    cursor.execute("INSERT INTO empresas (nome) VALUES (?)", ("Outra Empresa",))
    outra_id = cursor.lastrowid
    return {
        "cursor": cursor,
        "id": empresa_id,
        "admin": criar_usuario("acesso_admin", "senha123", empresa_id, is_admin=1, role="admin"),
        "admin2": criar_usuario("acesso_admin2", "senha123", empresa_id, is_admin=1, role="admin"),
        "prestador": criar_usuario("acesso_prestador", "senha123", empresa_id, is_admin=0, role="prestador"),
        "de_fora": criar_usuario("acesso_de_fora", "senha123", outra_id, is_admin=0, role="prestador"),
    }


# ---------- revogação imediata na autenticação ----------

def test_usuario_desativado_perde_acesso_na_hora(empresa):
    token = _token(empresa["prestador"])
    empresa["cursor"].execute("UPDATE usuarios SET ativo = FALSE WHERE id = ?", (empresa["prestador"]["id"],))
    _, status = _chamar(lancamentos_routes.listar_lancamentos, token)
    assert status == 401


def test_usuario_apagado_perde_acesso_na_hora(empresa):
    token = _token(empresa["prestador"])
    empresa["cursor"].execute("DELETE FROM usuarios WHERE id = ?", (empresa["prestador"]["id"],))
    _, status = _chamar(lancamentos_routes.listar_lancamentos, token)
    assert status == 401


def test_papel_vem_do_banco_e_nao_do_token(empresa):
    """Token diz admin, banco diz prestador: vale o banco."""
    token = _token(empresa["prestador"], is_admin=True, role="admin")
    _, status = _chamar(usuarios_routes.listar_usuarios, token)
    assert status == 403


def test_rebaixado_perde_admin_na_hora(empresa):
    token = _token(empresa["admin2"])
    _, status = _chamar(usuarios_routes.editar_usuario, _token(empresa["admin"]), empresa["admin2"]["id"],
                        method="PUT", json={"role": "financeiro"})
    assert status == 200
    _, status = _chamar(usuarios_routes.listar_usuarios, token)
    assert status == 403


# ---------- senha ----------

def test_trocar_propria_senha(empresa):
    antigo = _token(empresa["prestador"], iat=int(time.time()) - 60)
    corpo, status = _chamar(auth_routes.trocar_minha_senha, antigo, method="PUT",
                            json={"senha_atual": "senha123", "nova_senha": "novaSenha9"})
    assert status == 200
    assert corpo["token"]

    # Token anterior deixa de valer; o devolvido continua logado
    _, status = _chamar(lancamentos_routes.listar_lancamentos, antigo)
    assert status == 401
    _, status = _chamar(auth_routes.trocar_minha_senha, corpo["token"], method="PUT",
                        json={"senha_atual": "errada", "nova_senha": "outra123"})
    assert status == 400  # chegou na regra (autenticou), recusou pela senha atual
    assert login_usuario("acesso_prestador", "novaSenha9") is not None
    assert login_usuario("acesso_prestador", "senha123") is None


def test_trocar_propria_senha_validacoes(empresa):
    token = _token(empresa["prestador"])
    _, status = _chamar(auth_routes.trocar_minha_senha, token, method="PUT",
                        json={"senha_atual": "errada", "nova_senha": "novaSenha9"})
    assert status == 400
    _, status = _chamar(auth_routes.trocar_minha_senha, token, method="PUT",
                        json={"senha_atual": "senha123", "nova_senha": "123"})
    assert status == 400


def test_token_sem_iat_cai_depois_de_troca_de_senha(empresa):
    """Tokens emitidos antes desta mudança não têm iat — contam como anteriores."""
    token = _token(empresa["prestador"])
    usuarios_controller.redefinir_senha(empresa["prestador"]["id"], "novaSenha9", empresa["id"])
    _, status = _chamar(lancamentos_routes.listar_lancamentos, token)
    assert status == 401


def test_admin_redefine_senha_e_encerra_sessoes(empresa):
    sessao_prestador = _token(empresa["prestador"], iat=int(time.time()) - 60)
    _, status = _chamar(usuarios_routes.redefinir_senha_usuario, _token(empresa["admin"]),
                        empresa["prestador"]["id"], method="PUT", json={"nova_senha": "resetada1"})
    assert status == 200
    _, status = _chamar(lancamentos_routes.listar_lancamentos, sessao_prestador)
    assert status == 401
    assert login_usuario("acesso_prestador", "resetada1") is not None


def test_redefinir_senha_validacoes(empresa):
    admin = _token(empresa["admin"])
    _, status = _chamar(usuarios_routes.redefinir_senha_usuario, admin, empresa["prestador"]["id"],
                        method="PUT", json={"nova_senha": "123"})
    assert status == 400
    _, status = _chamar(usuarios_routes.redefinir_senha_usuario, admin, empresa["de_fora"]["id"],
                        method="PUT", json={"nova_senha": "resetada1"})
    assert status == 404
    _, status = _chamar(usuarios_routes.redefinir_senha_usuario, _token(empresa["prestador"]),
                        empresa["admin"]["id"], method="PUT", json={"nova_senha": "resetada1"})
    assert status == 403


# ---------- desativar em vez de apagar ----------

def test_desativar_preserva_historico_e_bloqueia_login(empresa):
    cursor = empresa["cursor"]
    pid = empresa["prestador"]["id"]
    cursor.execute("INSERT INTO requisicoes_materiais (usuario_id, nome, funcao, material) VALUES (?, ?, ?, ?)",
                   (pid, "Fulano", "Pedreiro", "Cimento"))
    cursor.execute("INSERT INTO tarefas (titulo, prestador_id) VALUES (?, ?)", ("Tarefa X", pid))

    _, status = _chamar(usuarios_routes.remover_usuario, _token(empresa["admin"]), pid, method="DELETE")
    assert status == 200

    cursor.execute("SELECT COUNT(*) FROM requisicoes_materiais WHERE usuario_id = ?", (pid,))
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT COUNT(*) FROM tarefas WHERE prestador_id = ?", (pid,))
    assert cursor.fetchone()[0] == 1
    assert login_usuario("acesso_prestador", "senha123") is None

    corpo, _ = _chamar(usuarios_routes.listar_usuarios, _token(empresa["admin"]))
    assert {u["username"]: u["ativo"] for u in corpo}["acesso_prestador"] is False


def test_reativar(empresa):
    pid = empresa["prestador"]["id"]
    admin = _token(empresa["admin"])
    _chamar(usuarios_routes.remover_usuario, admin, pid, method="DELETE")
    _, status = _chamar(usuarios_routes.reativar, admin, pid, method="POST")
    assert status == 200
    assert login_usuario("acesso_prestador", "senha123") is not None


def test_nao_desativa_a_si_mesmo_nem_de_outra_empresa(empresa):
    admin = _token(empresa["admin"])
    _, status = _chamar(usuarios_routes.remover_usuario, admin, empresa["admin"]["id"], method="DELETE")
    assert status == 400
    _, status = _chamar(usuarios_routes.remover_usuario, admin, empresa["de_fora"]["id"], method="DELETE")
    assert status == 404


# ---------- empresa nunca fica sem admin ----------

def test_nao_desativa_o_ultimo_admin(empresa):
    _chamar(usuarios_routes.remover_usuario, _token(empresa["admin"]), empresa["admin2"]["id"], method="DELETE")
    # admin é agora o único admin ativo; outro solicitante tenta desativá-lo
    _, status = usuarios_controller.desativar_usuario(empresa["admin"]["id"], empresa["id"], solicitante_id=-1)
    assert status == 400


def test_nao_rebaixa_o_ultimo_admin(empresa):
    _chamar(usuarios_routes.remover_usuario, _token(empresa["admin"]), empresa["admin2"]["id"], method="DELETE")
    _, status = usuarios_controller.alterar_papel(empresa["admin"]["id"], "financeiro", empresa["id"], solicitante_id=-1)
    assert status == 400


def test_nao_tira_o_proprio_admin(empresa):
    _, status = _chamar(usuarios_routes.editar_usuario, _token(empresa["admin"]), empresa["admin"]["id"],
                        method="PUT", json={"role": "gestor_obra"})
    assert status == 400


# ---------- editar papel ----------

def test_editar_papel(empresa):
    admin = _token(empresa["admin"])
    corpo, status = _chamar(usuarios_routes.editar_usuario, admin, empresa["prestador"]["id"],
                            method="PUT", json={"role": "admin"})
    assert status == 200 and corpo["is_admin"] is True

    _, status = _chamar(usuarios_routes.editar_usuario, admin, empresa["prestador"]["id"],
                        method="PUT", json={"role": "chefe"})
    assert status == 400
    _, status = _chamar(usuarios_routes.editar_usuario, admin, empresa["de_fora"]["id"],
                        method="PUT", json={"role": "financeiro"})
    assert status == 404
    # Token emitido quando ainda era prestador (diz is_admin False), mas o
    # banco agora diz admin — vale o banco: autorizado
    _, status = _chamar(usuarios_routes.editar_usuario, _token(empresa["prestador"]),
                        empresa["admin2"]["id"], method="PUT", json={"role": "prestador"})
    assert status == 200


# ---------- criar usuário ----------

def test_criar_usuario_valida_e_deriva_is_admin(empresa):
    admin = _token(empresa["admin"])
    for body in [
        {"username": "ab", "password": "senha123", "role": "prestador"},
        {"username": "novo_user", "password": "123", "role": "prestador"},
        {"username": "novo_user", "password": "senha123", "role": "chefe"},
    ]:
        _, status = _chamar(usuarios_routes.novo_usuario, admin, method="POST", json=body)
        assert status == 400, body

    corpo, status = _chamar(usuarios_routes.novo_usuario, admin, method="POST",
                            json={"username": "novo_user", "password": "senha123", "role": "financeiro", "is_admin": True})
    assert status == 201
    assert corpo["is_admin"] is False and corpo["role"] == "financeiro"


# ---------- seed do admin inicial ----------

def _recriar_seed(cursor):
    # Simula banco vazio dentro da transação do teste (desfeito no rollback)
    cursor.execute("DELETE FROM usuarios")
    create_usuarios_tables(cursor)
    cursor.execute("SELECT username, password, is_admin, role FROM usuarios")
    return cursor.fetchall()


def test_seed_admin_usa_variaveis_de_ambiente(db_session, monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "dono")
    monkeypatch.setenv("ADMIN_PASSWORD", "SenhaForte1")
    [admin] = _recriar_seed(db_session.cursor())
    assert admin["username"] == "dono" and admin["role"] == "admin" and admin["is_admin"] == 1
    assert check_password_hash(admin["password"], "SenhaForte1")


def test_seed_admin_sem_variaveis_gera_senha_aleatoria_no_log(db_session, monkeypatch, caplog):
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    with caplog.at_level(logging.WARNING, logger="gabaro.seed"):
        [admin] = _recriar_seed(db_session.cursor())
    assert admin["username"] == "admin"
    assert not check_password_hash(admin["password"], "admin")
    senha_logada = caplog.records[-1].args[1]
    assert check_password_hash(admin["password"], senha_logada)


# ---------- cadastro público ----------

def test_cadastro_publico_desligado_por_padrao(monkeypatch):
    monkeypatch.delenv("SIGNUP_ENABLED", raising=False)
    with _app.test_request_context("/"):
        resposta, _ = signup_routes.config_publica()
    assert resposta.get_json() == {"cadastro_publico": False}
    assert signup_routes.cadastro_publico_habilitado() is False


def test_cadastro_publico_ligado_por_variavel(monkeypatch):
    monkeypatch.setenv("SIGNUP_ENABLED", "true")
    assert signup_routes.cadastro_publico_habilitado() is True
