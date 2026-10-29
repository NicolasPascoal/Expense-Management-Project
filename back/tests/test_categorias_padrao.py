"""
Toda obra nova nasce com as categorias padrão no banco. Antes só a primeira
obra do banco as recebia: nas demais, o formulário mostrava uma lista fixa do
frontend que "sumia" ao cadastrar a primeira categoria (bug reportado em
2026-10-29 — parecia que as outras tinham sido excluídas).
"""
import datetime
import importlib

import jwt
from flask import Flask
from sqlalchemy import text

from app.controller.auth_controller import SECRET_KEY
from app.controller.signup_controller import cadastrar_construtora
from app.controller.usuarios_controller import criar_usuario
from app.database.modelCategoria import CATEGORIAS_PADRAO
from app.models import Categoria, Projeto
from app.routes import projeto_routes

_app = Flask(__name__)

_migration = importlib.import_module("migrations.versions.f6d2b8c4e1a7_categorias_padrao_em_obras_sem_elas")


def _nomes_categorias(cursor, projeto_id):
    cursor.execute("SELECT nome FROM categorias WHERE projeto_id = ?", (projeto_id,))
    return sorted(linha[0] for linha in cursor.fetchall())


def test_nova_obra_nasce_com_categorias_padrao(db_session):
    cursor = db_session.cursor()
    cursor.execute("INSERT INTO empresas (nome) VALUES (?)", ("Empresa Cat",))
    empresa_id = cursor.lastrowid
    admin = criar_usuario("admin_cat", "senha123", empresa_id, is_admin=1, role="admin")
    token = jwt.encode({
        'id': admin["id"], 'username': admin["username"], 'is_admin': True,
        'role': "admin", 'empresa_id': empresa_id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
    }, SECRET_KEY, algorithm="HS256")

    with _app.test_request_context(
        "/projetos", method="POST", json={"nome": "Obra Nova", "colunas": []},
        headers={"Authorization": f"Bearer {token}"},
    ):
        resposta, status = projeto_routes.criar_projeto()
    assert status == 201

    assert _nomes_categorias(cursor, resposta.get_json()["id"]) == sorted(CATEGORIAS_PADRAO)


def test_signup_obra_inicial_nasce_com_categorias_padrao(orm_session):
    resultado, status = cadastrar_construtora("Construtora Cat", "admin_signup_cat", "senha123")
    assert status == 201

    projeto = orm_session.query(Projeto).filter_by(empresa_id=resultado["empresa_id"]).one()
    nomes = sorted(c.nome for c in orm_session.query(Categoria).filter_by(projeto_id=projeto.id))
    assert nomes == sorted(CATEGORIAS_PADRAO)


def test_migration_lista_congelada_bate_com_a_do_app():
    assert _migration.CATEGORIAS_PADRAO == CATEGORIAS_PADRAO


def test_migration_completa_so_obras_sem_categorias_padrao(orm_session, monkeypatch):
    # Simula a migration sem o contexto do Alembic: op.execute roda na sessão de teste.
    monkeypatch.setattr(_migration.op, "execute", lambda sql: orm_session.execute(text(sql)))

    empresa_id = orm_session.execute(text("INSERT INTO empresas (nome) VALUES ('Empresa Mig') RETURNING id")).scalar()

    def _obra(nome):
        return orm_session.execute(
            text("INSERT INTO projetos (nome, colunas, empresa_id) VALUES (:n, '[]', :e) RETURNING id"),
            {"n": nome, "e": empresa_id},
        ).scalar()

    vazia = _obra("Obra vazia")
    so_propria = _obra("Obra com categoria própria")  # o caso do bug reportado
    com_padrao = _obra("Obra que já tem padrão")
    orm_session.add_all([
        Categoria(nome="Pintura", projeto_id=so_propria),
        Categoria(nome="fundação", projeto_id=com_padrao),  # comparação ignora maiúsculas
    ])
    orm_session.flush()

    def _nomes(projeto_id):
        return sorted(c.nome for c in orm_session.query(Categoria).filter_by(projeto_id=projeto_id))

    _migration.upgrade()
    _migration.upgrade()  # idempotente: segunda execução não duplica

    assert _nomes(vazia) == sorted(CATEGORIAS_PADRAO)
    assert _nomes(so_propria) == sorted(CATEGORIAS_PADRAO + ["Pintura"])
    assert _nomes(com_padrao) == ["fundação"]
