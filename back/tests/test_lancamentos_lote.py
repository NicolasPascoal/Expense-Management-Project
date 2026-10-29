"""
Lançamento com vários itens (nota com mais de um produto) —
docs/superpowers/specs/2026-10-29-lancamento-varios-itens-design.md.
Cada item vira um lançamento normal; o lote é gravado inteiro ou nada.
"""
import datetime

import jwt
import pytest
from flask import Flask

from app.controller import lancamentos_controller
from app.controller.auth_controller import SECRET_KEY
from app.controller.usuarios_controller import criar_usuario
from app.routes import lancamentos_routes

_app = Flask(__name__)

COMUNS = {"data": "29/10/2026", "categoria": "Material de construção", "fornecedor": "Depósito São José",
          "forma": "Pix", "conta": "", "obs": "NF 4521"}


def _item(descricao, quantidade, unitario):
    return {**COMUNS, "item": descricao, "quantidade": str(quantidade),
            "unitario": unitario, "valor": round(quantidade * unitario, 2)}


def _token_para(usuario):
    return jwt.encode({
        'id': usuario['id'], 'username': usuario['username'], 'is_admin': bool(usuario['is_admin']),
        'role': usuario['role'], 'empresa_id': usuario['empresa_id'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
    }, SECRET_KEY, algorithm="HS256")


def _enviar_lote(usuario, corpo):
    with _app.test_request_context(
        "/lancamentos/lote", method="POST", json=corpo,
        headers={"Authorization": f"Bearer {_token_para(usuario)}"},
    ):
        res = lancamentos_routes.novos_lancamentos_em_lote()
    resposta, status = res if isinstance(res, tuple) else (res, res.status_code)
    return resposta.get_json(), status


def _lancamentos_da_obra(cursor, projeto_id):
    cursor.execute("SELECT id FROM lancamentos_v2 WHERE projeto_id = ?", (projeto_id,))
    return cursor.fetchall()


@pytest.fixture
def cenario(db_session):
    cursor = db_session.cursor()
    cursor.execute("INSERT INTO empresas (nome) VALUES ('Empresa Lote A')")
    empresa_a = cursor.lastrowid
    cursor.execute("INSERT INTO empresas (nome) VALUES ('Empresa Lote B')")
    empresa_b = cursor.lastrowid
    obras = {}
    for nome, empresa in (("a1", empresa_a), ("a2", empresa_a), ("b1", empresa_b)):
        cursor.execute("INSERT INTO projetos (nome, colunas, empresa_id) VALUES (?, '[]', ?)", (nome, empresa))
        obras[nome] = cursor.lastrowid

    financeiro = criar_usuario("lote_financeiro", "senha123", empresa_a, is_admin=0, role="financeiro")
    cursor.execute("INSERT INTO usuario_projetos (usuario_id, projeto_id) VALUES (?, ?)", (financeiro["id"], obras["a1"]))
    return {
        "cursor": cursor,
        "obras": obras,
        "admin": criar_usuario("lote_admin", "senha123", empresa_a, is_admin=1, role="admin"),
        "financeiro": financeiro,
        "prestador": criar_usuario("lote_prestador", "senha123", empresa_a, is_admin=0, role="prestador"),
    }


def test_lote_cria_um_lancamento_por_item_com_campos_comuns(cenario):
    itens = [_item("Cimento CP-II 50kg", 10, 38.9), _item("Areia média m³", 2, 120.0), _item("Brita 1", 3, 95.5)]
    corpo, status = _enviar_lote(cenario["admin"], {"projeto_id": cenario["obras"]["a1"], "lancamentos": itens})

    assert status == 201
    assert [l["item"] for l in corpo] == ["Cimento CP-II 50kg", "Areia média m³", "Brita 1"]
    for lancamento in corpo:
        assert lancamento["projeto_id"] == cenario["obras"]["a1"]
        for campo, valor in COMUNS.items():
            assert lancamento[campo] == valor
    assert [l["valor"] for l in corpo] == [389.0, 240.0, 286.5]
    assert len(_lancamentos_da_obra(cenario["cursor"], cenario["obras"]["a1"])) == 3


def test_lote_registra_auditoria_por_item(cenario):
    corpo, status = _enviar_lote(cenario["admin"], {
        "projeto_id": cenario["obras"]["a1"], "lancamentos": [_item("Cimento", 1, 10.0), _item("Areia", 1, 20.0)],
    })
    assert status == 201

    cursor = cenario["cursor"]
    cursor.execute(
        "SELECT entidade_id, detalhes FROM auditoria WHERE entidade = 'lancamento' AND acao = 'criar' AND entidade_id IN (?, ?)",
        (corpo[0]["id"], corpo[1]["id"]),
    )
    detalhes = sorted(linha["detalhes"] for linha in cursor.fetchall())
    assert detalhes == ["Areia (nota com 2 itens)", "Cimento (nota com 2 itens)"]


def test_lote_em_obra_de_outra_empresa_nao_grava_nada(cenario):
    _, status = _enviar_lote(cenario["admin"], {"projeto_id": cenario["obras"]["b1"], "lancamentos": [_item("X", 1, 1.0)]})
    assert status == 400
    assert _lancamentos_da_obra(cenario["cursor"], cenario["obras"]["b1"]) == []


def test_lote_em_obra_nao_vinculada_ao_usuario_nao_grava_nada(cenario):
    _, status = _enviar_lote(cenario["financeiro"], {"projeto_id": cenario["obras"]["a2"], "lancamentos": [_item("X", 1, 1.0)]})
    assert status == 400
    assert _lancamentos_da_obra(cenario["cursor"], cenario["obras"]["a2"]) == []

    # na obra vinculada, o mesmo usuário consegue
    _, status = _enviar_lote(cenario["financeiro"], {"projeto_id": cenario["obras"]["a1"], "lancamentos": [_item("X", 1, 1.0)]})
    assert status == 201


def test_prestador_nao_lanca_em_lote(cenario):
    _, status = _enviar_lote(cenario["prestador"], {"projeto_id": cenario["obras"]["a1"], "lancamentos": [_item("X", 1, 1.0)]})
    assert status == 403


@pytest.mark.parametrize("lancamentos, mensagem", [
    (None, "Envie ao menos um lançamento"),
    ([], "Envie ao menos um lançamento"),
    ({"item": "X"}, "Envie ao menos um lançamento"),
    ([_item("X", 1, 1.0)] * 101, "Máximo de 100 lançamentos por vez"),
    ([_item("X", 1, 1.0), "texto"], "Lançamento inválido na posição 2"),
    ([_item("X", 1, 1.0), {**_item("Y", 1, 1.0), "requisicao_id": 7}], "Lançamento de requisição não pode ser criado em lote"),
])
def test_lote_invalido_nao_grava_nada(cenario, lancamentos, mensagem):
    corpo, status = _enviar_lote(cenario["admin"], {"projeto_id": cenario["obras"]["a1"], "lancamentos": lancamentos})
    assert status == 400
    assert corpo["erro"] == mensagem
    assert _lancamentos_da_obra(cenario["cursor"], cenario["obras"]["a1"]) == []


def test_lote_sem_projeto_id(cenario):
    corpo, status = _enviar_lote(cenario["admin"], {"lancamentos": [_item("X", 1, 1.0)]})
    assert status == 400
    assert corpo["erro"] == "projeto_id é obrigatório"


def test_lote_ignora_id_e_projeto_id_dentro_do_item(cenario):
    item = {**_item("X", 1, 1.0), "id": 999999, "projeto_id": cenario["obras"]["b1"]}
    corpo, status = _enviar_lote(cenario["admin"], {"projeto_id": cenario["obras"]["a1"], "lancamentos": [item]})
    assert status == 201
    assert corpo[0]["projeto_id"] == cenario["obras"]["a1"]
    assert corpo[0]["id"] != 999999
    assert _lancamentos_da_obra(cenario["cursor"], cenario["obras"]["b1"]) == []


def test_falha_no_meio_do_lote_desfaz_tudo(db_session, monkeypatch):
    """Erro no 2º INSERT: a função desfaz explicitamente o 1º antes de propagar."""
    chamadas = {"rollback": 0}
    rollback_real = db_session.rollback

    def rollback_contado():
        chamadas["rollback"] += 1
        rollback_real()
    monkeypatch.setattr(db_session, "rollback", rollback_contado)

    dumps_real = lancamentos_controller.json.dumps
    contador = {"n": 0}

    def dumps_que_falha_no_segundo(dados):
        contador["n"] += 1
        if contador["n"] == 2:
            raise RuntimeError("falha simulada no 2º item")
        return dumps_real(dados)
    monkeypatch.setattr(lancamentos_controller.json, "dumps", dumps_que_falha_no_segundo)

    cursor = db_session.cursor()
    cursor.execute("SELECT id FROM projetos ORDER BY id LIMIT 1")
    projeto_id = cursor.fetchone()["id"]
    cursor.execute("SELECT COUNT(*) AS n FROM lancamentos_v2")
    antes = cursor.fetchone()["n"]

    with pytest.raises(RuntimeError):
        lancamentos_controller.criar_lancamentos_em_lote(projeto_id, [_item("A", 1, 1.0), _item("B", 1, 1.0)], 1)

    assert chamadas["rollback"] == 1
    cursor = db_session.cursor()
    cursor.execute("SELECT COUNT(*) AS n FROM lancamentos_v2")
    assert cursor.fetchone()["n"] == antes
