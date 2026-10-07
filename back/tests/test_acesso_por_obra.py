"""
Testes da Tarefa 6.2 do roadmap (controle de acesso por obra).
Cobre: usuário não-admin só enxerga/age sobre obras às quais está vinculado
(usuario_projetos), mesmo dentro da própria empresa; admin continua vendo
todas; vínculo nunca aponta para obra/usuário de outra empresa; backfill
inicial preserva o acesso de quem já existia e roda uma única vez.
"""
import datetime

import jwt
import pytest
from flask import Flask

from app.controller.auth_controller import SECRET_KEY
from app.controller.usuarios_controller import criar_usuario
from app.controller import (
    lancamentos_controller, servicos_controller, orcamentos_controller, entradas_controller
)
from app.database.modelUsuarioProjetos import create_usuario_projetos_tables
from app.routes import (
    projeto_routes, lancamentos_routes, auditoria_routes, usuarios_routes, entradas_routes
)

_app = Flask(__name__)


def _criar_empresa(cursor, nome):
    cursor.execute("INSERT INTO empresas (nome) VALUES (?)", (nome,))
    return cursor.lastrowid


def _criar_projeto(cursor, nome, empresa_id):
    cursor.execute("INSERT INTO projetos (nome, colunas, empresa_id) VALUES (?, ?, ?)", (nome, '[]', empresa_id))
    return cursor.lastrowid


def _vincular(cursor, usuario_id, projeto_id):
    cursor.execute("INSERT INTO usuario_projetos (usuario_id, projeto_id) VALUES (?, ?)", (usuario_id, projeto_id))


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


def _chamar(rota, usuario, *args, path="/", method="GET", json=None):
    """Executa a função de rota num contexto de request autenticado e
    normaliza o retorno para (corpo_json, status) — algumas rotas devolvem só
    a Response, outras a tupla (Response, status)."""
    with _app.test_request_context(
        path, method=method, json=json,
        headers={"Authorization": f"Bearer {_token_para(usuario)}"},
    ):
        res = rota(*args)
    if isinstance(res, tuple):
        resposta, status = res
    else:
        resposta, status = res, res.status_code
    return resposta.get_json(), status


@pytest.fixture
def obras(db_session):
    """Empresa A com duas obras (A1, A2) e empresa B com uma (B1). Na A:
    admin (sem vínculo), gestor_obra e financeiro vinculados só à A1, e um
    prestador sem vínculo nenhum."""
    cursor = db_session.cursor()
    empresa_a = _criar_empresa(cursor, "Empresa Obras A")
    empresa_b = _criar_empresa(cursor, "Empresa Obras B")
    a1 = _criar_projeto(cursor, "Obra A1", empresa_a)
    a2 = _criar_projeto(cursor, "Obra A2", empresa_a)
    b1 = _criar_projeto(cursor, "Obra B1", empresa_b)

    admin = criar_usuario("obra_admin", "senha123", empresa_a, is_admin=1, role="admin")
    gestor = criar_usuario("obra_gestor", "senha123", empresa_a, is_admin=0, role="gestor_obra")
    financeiro = criar_usuario("obra_financeiro", "senha123", empresa_a, is_admin=0, role="financeiro")
    sem_vinculo = criar_usuario("obra_sem_vinculo", "senha123", empresa_a, is_admin=0, role="prestador")
    usuario_b = criar_usuario("obra_usuario_b", "senha123", empresa_b, is_admin=0, role="financeiro")

    _vincular(cursor, gestor["id"], a1)
    _vincular(cursor, financeiro["id"], a1)

    return {
        "empresa_a": empresa_a, "empresa_b": empresa_b,
        "a1": a1, "a2": a2, "b1": b1,
        "admin": admin, "gestor": gestor, "financeiro": financeiro,
        "sem_vinculo": sem_vinculo, "usuario_b": usuario_b,
    }


# ---------- lista de obras (critério de aceite do roadmap) ----------

def test_usuario_sem_vinculo_nao_ve_obras_da_propria_empresa(obras):
    corpo, status = _chamar(projeto_routes.listar_projetos, obras["sem_vinculo"])
    assert status == 200
    assert corpo == []


def test_gestor_ve_so_obras_vinculadas(obras):
    corpo, _ = _chamar(projeto_routes.listar_projetos, obras["gestor"])
    assert [p["id"] for p in corpo] == [obras["a1"]]


def test_admin_ve_todas_as_obras_da_empresa_sem_vinculo(obras):
    corpo, _ = _chamar(projeto_routes.listar_projetos, obras["admin"])
    ids = {p["id"] for p in corpo}
    assert {obras["a1"], obras["a2"]} <= ids
    assert obras["b1"] not in ids


# ---------- lançamentos via rota ----------

def test_gestor_lista_so_lancamentos_das_obras_vinculadas(obras):
    lancamentos_controller.criar_lancamento(obras["a1"], {"item": "da A1"}, obras["empresa_a"])
    lancamentos_controller.criar_lancamento(obras["a2"], {"item": "da A2"}, obras["empresa_a"])

    corpo, status = _chamar(lancamentos_routes.listar_lancamentos, obras["gestor"])
    assert status == 200
    assert [l["item"] for l in corpo] == ["da A1"]

    # Pedir explicitamente a obra não vinculada não contorna o filtro
    corpo, status = _chamar(lancamentos_routes.listar_lancamentos, obras["gestor"], path=f"/?projeto_id={obras['a2']}")
    assert status == 200
    assert corpo == []


def test_admin_lista_lancamentos_de_todas_as_obras(obras):
    lancamentos_controller.criar_lancamento(obras["a1"], {"item": "da A1"}, obras["empresa_a"])
    lancamentos_controller.criar_lancamento(obras["a2"], {"item": "da A2"}, obras["empresa_a"])

    corpo, _ = _chamar(lancamentos_routes.listar_lancamentos, obras["admin"])
    assert {l["item"] for l in corpo} == {"da A1", "da A2"}


def test_gestor_nao_cria_lancamento_em_obra_nao_vinculada(obras):
    corpo, status = _chamar(
        lancamentos_routes.novo_lancamento, obras["gestor"],
        method="POST", json={"projeto_id": obras["a2"], "item": "x"},
    )
    assert status == 400

    corpo, status = _chamar(
        lancamentos_routes.novo_lancamento, obras["gestor"],
        method="POST", json={"projeto_id": obras["a1"], "item": "x"},
    )
    assert status == 201


def test_gestor_nao_le_edita_nem_exclui_lancamento_de_obra_nao_vinculada(obras):
    alheio = lancamentos_controller.criar_lancamento(obras["a2"], {"item": "da A2"}, obras["empresa_a"])

    _, status = _chamar(lancamentos_routes.obter_lancamento, obras["gestor"], alheio["id"])
    assert status == 404
    _, status = _chamar(
        lancamentos_routes.editar_lancamento, obras["gestor"], alheio["id"],
        method="PUT", json={"item": "alterado"},
    )
    assert status == 404
    _, status = _chamar(lancamentos_routes.remover_lancamento, obras["gestor"], alheio["id"], method="DELETE")
    assert status == 404

    # Continua intacto para quem tem acesso
    assert lancamentos_controller.get_lancamento_por_id(alheio["id"], obras["empresa_a"])["item"] == "da A2"


def test_financeiro_tambem_e_restrito_por_obra(obras):
    """Decisão B da Tarefa 6.2: financeiro não é exceção — vê só as obras vinculadas."""
    lancamentos_controller.criar_lancamento(obras["a2"], {"item": "da A2"}, obras["empresa_a"])
    corpo, status = _chamar(lancamentos_routes.listar_lancamentos, obras["financeiro"])
    assert status == 200
    assert corpo == []


# ---------- demais módulos financeiros (nível de controller) ----------

def test_categorias_e_contas_filtram_por_vinculo(obras):
    gestor_id = obras["gestor"]["id"]
    cat_a2 = servicos_controller.criar_categoria("Cat A2", obras["a2"])
    conta_a2 = servicos_controller.criar_conta("Conta A2", obras["a2"])
    servicos_controller.criar_categoria("Cat A1", obras["a1"])

    cats = servicos_controller.get_todas_categorias(obras["empresa_a"], usuario_id=gestor_id)
    assert [c["nome"] for c in cats] == ["Cat A1"]
    assert servicos_controller.get_todas_contas(obras["empresa_a"], usuario_id=gestor_id) == []

    assert servicos_controller.deletar_categoria(cat_a2["id"], obras["empresa_a"], gestor_id) is False
    assert servicos_controller.deletar_conta(conta_a2["id"], obras["empresa_a"], gestor_id) is False
    # Sem restrição (admin) continua funcionando
    assert servicos_controller.deletar_categoria(cat_a2["id"], obras["empresa_a"]) is True


def test_orcamentos_filtram_por_vinculo(obras):
    gestor_id = obras["gestor"]["id"]
    cat_a2 = servicos_controller.criar_categoria("Cat A2", obras["a2"])
    orc = orcamentos_controller.upsert_orcamento(obras["a2"], cat_a2["id"], 1000)

    assert orcamentos_controller.get_orcamentos(obras["empresa_a"], usuario_id=gestor_id) == []
    assert orcamentos_controller.get_orcamentos(obras["empresa_a"], obras["a2"], gestor_id) == []
    assert orcamentos_controller.deletar_orcamento(orc["id"], obras["empresa_a"], gestor_id) is False


def test_entradas_filtram_por_vinculo(obras):
    gestor_id = obras["gestor"]["id"]
    entrada = entradas_controller.criar_entrada(obras["a2"], "Aporte A2", 5000, "2026-10-07")

    assert entradas_controller.get_entradas(obras["empresa_a"], usuario_id=gestor_id) == []
    assert entradas_controller.deletar_entrada(entrada["id"], obras["empresa_a"], gestor_id) is False

    _, status = _chamar(
        entradas_routes.nova_entrada, obras["gestor"],
        method="POST", json={"projeto_id": obras["a2"], "descricao": "x", "valor": 10},
    )
    assert status == 400


# ---------- auditoria ----------

def test_auditoria_so_para_admin(obras):
    _, status = _chamar(auditoria_routes.listar_auditoria, obras["financeiro"])
    assert status == 403
    _, status = _chamar(auditoria_routes.listar_auditoria, obras["gestor"])
    assert status == 403
    _, status = _chamar(auditoria_routes.listar_auditoria, obras["admin"])
    assert status == 200


# ---------- gestão de vínculos (admin) ----------

def test_listar_usuarios_inclui_projeto_ids(obras):
    corpo, status = _chamar(usuarios_routes.listar_usuarios, obras["admin"])
    assert status == 200
    por_nome = {u["username"]: u for u in corpo}
    assert por_nome["obra_gestor"]["projeto_ids"] == [obras["a1"]]
    assert por_nome["obra_sem_vinculo"]["projeto_ids"] == []


def test_admin_substitui_vinculos_do_usuario(obras):
    corpo, status = _chamar(
        usuarios_routes.atualizar_projetos_usuario, obras["admin"], obras["gestor"]["id"],
        method="PUT", json={"projeto_ids": [obras["a2"]]},
    )
    assert status == 200
    assert corpo["projeto_ids"] == [obras["a2"]]

    corpo, _ = _chamar(projeto_routes.listar_projetos, obras["gestor"])
    assert [p["id"] for p in corpo] == [obras["a2"]]


def test_admin_remove_todos_os_vinculos(obras):
    _, status = _chamar(
        usuarios_routes.atualizar_projetos_usuario, obras["admin"], obras["gestor"]["id"],
        method="PUT", json={"projeto_ids": []},
    )
    assert status == 200
    corpo, _ = _chamar(projeto_routes.listar_projetos, obras["gestor"])
    assert corpo == []


def test_nao_vincula_obra_de_outra_empresa(obras):
    _, status = _chamar(
        usuarios_routes.atualizar_projetos_usuario, obras["admin"], obras["gestor"]["id"],
        method="PUT", json={"projeto_ids": [obras["a1"], obras["b1"]]},
    )
    assert status == 400
    # Nada mudou (validação acontece antes de apagar os vínculos atuais)
    corpo, _ = _chamar(projeto_routes.listar_projetos, obras["gestor"])
    assert [p["id"] for p in corpo] == [obras["a1"]]


def test_nao_altera_vinculos_de_usuario_de_outra_empresa(obras):
    _, status = _chamar(
        usuarios_routes.atualizar_projetos_usuario, obras["admin"], obras["usuario_b"]["id"],
        method="PUT", json={"projeto_ids": [obras["a1"]]},
    )
    assert status == 404


def test_vinculos_payload_invalido_e_admin_alvo(obras):
    for payload in [{}, {"projeto_ids": "1"}, {"projeto_ids": [True]}, {"projeto_ids": ["1"]}]:
        _, status = _chamar(
            usuarios_routes.atualizar_projetos_usuario, obras["admin"], obras["gestor"]["id"],
            method="PUT", json=payload,
        )
        assert status == 400, payload

    _, status = _chamar(
        usuarios_routes.atualizar_projetos_usuario, obras["admin"], obras["admin"]["id"],
        method="PUT", json={"projeto_ids": [obras["a1"]]},
    )
    assert status == 400


def test_nao_admin_nao_gerencia_vinculos(obras):
    _, status = _chamar(
        usuarios_routes.atualizar_projetos_usuario, obras["gestor"], obras["gestor"]["id"],
        method="PUT", json={"projeto_ids": [obras["a1"], obras["a2"]]},
    )
    assert status == 403


# ---------- backfill inicial ----------

def test_backfill_vincula_nao_admins_a_todas_as_obras_da_empresa_uma_unica_vez(obras, db_session):
    """Simula o primeiro boot após o deploy: a tabela ainda não existe. DDL é
    transacional no Postgres, então o DROP é desfeito no rollback do teste."""
    cursor = db_session.cursor()
    cursor.execute("DROP TABLE usuario_projetos")
    create_usuario_projetos_tables(cursor)

    cursor.execute(
        "SELECT usuario_id, projeto_id FROM usuario_projetos WHERE usuario_id IN (?, ?, ?)",
        (obras["admin"]["id"], obras["sem_vinculo"]["id"], obras["usuario_b"]["id"])
    )
    vinculos = {(r["usuario_id"], r["projeto_id"]) for r in cursor.fetchall()}
    assert vinculos == {
        (obras["sem_vinculo"]["id"], obras["a1"]),
        (obras["sem_vinculo"]["id"], obras["a2"]),
        (obras["usuario_b"]["id"], obras["b1"]),
    }  # admin não recebe vínculo; ninguém é vinculado a obra de outra empresa

    # Vínculo removido pelo admin não volta no próximo boot
    cursor.execute("DELETE FROM usuario_projetos WHERE usuario_id = ?", (obras["sem_vinculo"]["id"],))
    create_usuario_projetos_tables(cursor)
    cursor.execute("SELECT COUNT(*) FROM usuario_projetos WHERE usuario_id = ?", (obras["sem_vinculo"]["id"],))
    assert cursor.fetchone()[0] == 0
