"""
Testes da Tarefa 7.5 do roadmap (lançamento gerado a partir de requisição).
Cobre: geração vincula a requisição ao lançamento; não gera duas vezes; só
para status de compra feita; só requisição da própria empresa; só quem
aprova requisições; respeita o acesso por obra (Tarefa 6.2); excluir o
lançamento libera a requisição para gerar de novo.
"""
import datetime

import jwt
import pytest
from flask import Flask

from app.controller.auth_controller import SECRET_KEY
from app.controller.usuarios_controller import criar_usuario
from app.controller import lancamentos_controller
from app.routes import lancamentos_routes

_app = Flask(__name__)


def _criar_empresa(cursor, nome):
    cursor.execute("INSERT INTO empresas (nome) VALUES (?)", (nome,))
    return cursor.lastrowid


def _criar_projeto(cursor, nome, empresa_id):
    cursor.execute("INSERT INTO projetos (nome, colunas, empresa_id) VALUES (?, ?, ?)", (nome, '[]', empresa_id))
    return cursor.lastrowid


def _criar_requisicao(cursor, usuario_id, status):
    cursor.execute(
        "INSERT INTO requisicoes_materiais (usuario_id, nome, funcao, material, status) VALUES (?, ?, ?, ?, ?)",
        (usuario_id, "Fulano", "Pedreiro", "10 sacos de cimento", status)
    )
    return cursor.lastrowid


def _token_para(usuario):
    payload = {
        'id': usuario['id'],
        'username': usuario['username'],
        'is_admin': bool(usuario['is_admin']),
        'role': usuario['role'],
        'empresa_id': usuario['empresa_id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def _gerar(usuario, body):
    with _app.test_request_context(
        "/lancamentos", method="POST", json=body,
        headers={"Authorization": f"Bearer {_token_para(usuario)}"},
    ):
        resposta, status = lancamentos_routes.novo_lancamento()
    return resposta.get_json(), status


def _lancamento_id_da_requisicao(cursor, requisicao_id):
    cursor.execute("SELECT lancamento_id FROM requisicoes_materiais WHERE id = ?", (requisicao_id,))
    return cursor.fetchone()["lancamento_id"]


@pytest.fixture
def cenario(db_session):
    """Empresa A com obras A1 e A2; gestor vinculado só à A1; financeiro
    vinculado à A1 (tem acesso financeiro, mas não aprova requisições);
    requisições de um prestador em cada status. Empresa B com uma requisição."""
    cursor = db_session.cursor()
    empresa_a = _criar_empresa(cursor, "Empresa Req A")
    empresa_b = _criar_empresa(cursor, "Empresa Req B")
    a1 = _criar_projeto(cursor, "Obra A1", empresa_a)
    a2 = _criar_projeto(cursor, "Obra A2", empresa_a)

    admin = criar_usuario("req_admin", "senha123", empresa_a, is_admin=1, role="admin")
    gestor = criar_usuario("req_gestor", "senha123", empresa_a, is_admin=0, role="gestor_obra")
    financeiro = criar_usuario("req_financeiro", "senha123", empresa_a, is_admin=0, role="financeiro")
    prestador = criar_usuario("req_prestador", "senha123", empresa_a, is_admin=0, role="prestador")
    prestador_b = criar_usuario("req_prestador_b", "senha123", empresa_b, is_admin=0, role="prestador")
    for usuario in (gestor, financeiro):
        cursor.execute("INSERT INTO usuario_projetos (usuario_id, projeto_id) VALUES (?, ?)", (usuario["id"], a1))

    return {
        "cursor": cursor, "a1": a1, "a2": a2,
        "admin": admin, "gestor": gestor, "financeiro": financeiro,
        "comprado": _criar_requisicao(cursor, prestador["id"], "Comprado"),
        "a_caminho": _criar_requisicao(cursor, prestador["id"], "A caminho"),
        "pendente": _criar_requisicao(cursor, prestador["id"], "Pendente"),
        "cancelado": _criar_requisicao(cursor, prestador["id"], "Cancelado"),
        "de_outra_empresa": _criar_requisicao(cursor, prestador_b["id"], "Comprado"),
    }


def test_gera_lancamento_vinculado_a_requisicao(cenario):
    corpo, status = _gerar(cenario["gestor"], {
        "projeto_id": cenario["a1"], "requisicao_id": cenario["comprado"],
        "item": "10 sacos de cimento", "valor": 350.0,
    })
    assert status == 201
    assert corpo["item"] == "10 sacos de cimento"
    assert "requisicao_id" not in corpo  # não vai para os dados dinâmicos
    assert _lancamento_id_da_requisicao(cenario["cursor"], cenario["comprado"]) == corpo["id"]

    cenario["cursor"].execute("SELECT detalhes FROM auditoria WHERE entidade = 'lancamento' AND entidade_id = ?", (corpo["id"],))
    assert "requisição #" in cenario["cursor"].fetchone()["detalhes"]


def test_status_a_caminho_tambem_gera(cenario):
    _, status = _gerar(cenario["admin"], {"projeto_id": cenario["a2"], "requisicao_id": cenario["a_caminho"], "item": "x"})
    assert status == 201


def test_nao_gera_duas_vezes_para_a_mesma_requisicao(cenario):
    body = {"projeto_id": cenario["a1"], "requisicao_id": cenario["comprado"], "item": "x"}
    _, status = _gerar(cenario["gestor"], body)
    assert status == 201
    _, status = _gerar(cenario["gestor"], body)
    assert status == 409


def test_status_pendente_ou_cancelado_nao_gera(cenario):
    for chave in ("pendente", "cancelado"):
        _, status = _gerar(cenario["gestor"], {"projeto_id": cenario["a1"], "requisicao_id": cenario[chave], "item": "x"})
        assert status == 400, chave
        assert _lancamento_id_da_requisicao(cenario["cursor"], cenario[chave]) is None


def test_requisicao_de_outra_empresa_nao_gera(cenario):
    _, status = _gerar(cenario["admin"], {"projeto_id": cenario["a1"], "requisicao_id": cenario["de_outra_empresa"], "item": "x"})
    assert status == 404
    assert _lancamento_id_da_requisicao(cenario["cursor"], cenario["de_outra_empresa"]) is None


def test_quem_nao_aprova_requisicoes_nao_gera(cenario):
    """Financeiro tem acesso financeiro à obra, mas não a permissão de requisições."""
    _, status = _gerar(cenario["financeiro"], {"projeto_id": cenario["a1"], "requisicao_id": cenario["comprado"], "item": "x"})
    assert status == 403
    assert _lancamento_id_da_requisicao(cenario["cursor"], cenario["comprado"]) is None


def test_respeita_acesso_por_obra(cenario):
    """Gestor não vinculado à A2 não gera lançamento nela (Tarefa 6.2)."""
    _, status = _gerar(cenario["gestor"], {"projeto_id": cenario["a2"], "requisicao_id": cenario["comprado"], "item": "x"})
    assert status == 400
    assert _lancamento_id_da_requisicao(cenario["cursor"], cenario["comprado"]) is None


def test_requisicao_id_invalido(cenario):
    for valor in ("1", True, 1.5):
        _, status = _gerar(cenario["gestor"], {"projeto_id": cenario["a1"], "requisicao_id": valor, "item": "x"})
        assert status == 400, valor


def test_excluir_lancamento_libera_requisicao(cenario):
    corpo, _ = _gerar(cenario["gestor"], {"projeto_id": cenario["a1"], "requisicao_id": cenario["comprado"], "item": "x"})
    empresa_id = cenario["gestor"]["empresa_id"]
    assert lancamentos_controller.deletar_lancamento(corpo["id"], empresa_id) is True
    assert _lancamento_id_da_requisicao(cenario["cursor"], cenario["comprado"]) is None

    _, status = _gerar(cenario["gestor"], {"projeto_id": cenario["a1"], "requisicao_id": cenario["comprado"], "item": "x"})
    assert status == 201


def test_lancamento_comum_continua_funcionando(cenario):
    corpo, status = _gerar(cenario["financeiro"], {"projeto_id": cenario["a1"], "item": "avulso"})
    assert status == 201
    assert corpo["item"] == "avulso"
