"""
PROXY_HOPS: atrás de proxy, o IP do cliente (usado pelo rate limit do login)
vem do X-Forwarded-For — senão todos os usuários compartilhariam o IP do
container do proxy e um único limite de tentativas.
"""
from flask import request

from app import create_app

# Produção: Caddy põe o IP do cliente; o nginx do frontend acrescenta o do Caddy.
XFF_PRODUCAO = "203.0.113.7, 172.18.0.5"


def _ip_visto(monkeypatch, proxy_hops, xff):
    if proxy_hops is None:
        monkeypatch.delenv("PROXY_HOPS", raising=False)
    else:
        monkeypatch.setenv("PROXY_HOPS", str(proxy_hops))
    app = create_app()
    app.add_url_rule("/_ip", "_ip", lambda: request.remote_addr)
    resposta = app.test_client().get(
        "/_ip", headers={"X-Forwarded-For": xff}, environ_base={"REMOTE_ADDR": "172.18.0.9"}
    )
    return resposta.get_data(as_text=True)


def test_com_dois_proxies_usa_ip_real_do_cliente(monkeypatch):
    assert _ip_visto(monkeypatch, 2, XFF_PRODUCAO) == "203.0.113.7"


def test_ip_forjado_pelo_cliente_e_ignorado(monkeypatch):
    # Cliente manda X-Forwarded-For falso; os proxies acrescentam os IPs reais.
    assert _ip_visto(monkeypatch, 2, "6.6.6.6, " + XFF_PRODUCAO) == "203.0.113.7"


def test_sem_proxy_configurado_nao_confia_no_cabecalho(monkeypatch):
    assert _ip_visto(monkeypatch, None, XFF_PRODUCAO) == "172.18.0.9"
