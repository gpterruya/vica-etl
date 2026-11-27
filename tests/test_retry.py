import pytest
import requests

import extract.zapsign as zapsign


class _FakeResponse:
    def __init__(self, status, payload=None):
        self.status_code = status
        self._payload = payload or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error", response=self)

    def json(self):
        return self._payload


@pytest.fixture
def fake_get(monkeypatch):
    """Simula requests.get devolvendo uma sequência de respostas/exceções."""

    def install(outcomes):
        calls = []

        def get(url, headers=None, timeout=None):
            calls.append(timeout)
            outcome = outcomes[len(calls) - 1]
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

        monkeypatch.setattr(zapsign.requests, "get", get)
        return calls

    return install


def _no_wait(fn):
    return fn.retry_with(sleep=lambda seconds: None)


def test_tenta_de_novo_em_503_ate_a_api_voltar(fake_get):
    calls = fake_get([
        _FakeResponse(503),
        _FakeResponse(503),
        _FakeResponse(502),
        _FakeResponse(200, {"results": [], "next": None}),
    ])

    data = _no_wait(zapsign.get_docs_page)("https://zapsign.invalid/docs/?page=51")

    assert data == {"results": [], "next": None}
    assert len(calls) == 4


def test_tenta_de_novo_em_falha_de_conexao_e_timeout(fake_get):
    calls = fake_get([
        requests.ConnectionError("conexão recusada"),
        requests.Timeout("tempo esgotado"),
        _FakeResponse(200, {"token": "a"}),
    ])

    data = _no_wait(zapsign.get_doc_detail)("a")

    assert data == {"token": "a"}
    assert len(calls) == 3


def test_erro_definitivo_nao_e_repetido(fake_get):
    calls = fake_get([_FakeResponse(401), _FakeResponse(200)])

    with pytest.raises(requests.HTTPError):
        _no_wait(zapsign.get_docs_page)("https://zapsign.invalid/docs/")

    assert len(calls) == 1


def test_desiste_depois_de_8_tentativas_com_o_erro_original(fake_get):
    calls = fake_get([_FakeResponse(503)] * 8)

    with pytest.raises(requests.HTTPError, match="503"):
        _no_wait(zapsign.get_docs_page)("https://zapsign.invalid/docs/")

    assert len(calls) == 8


def test_toda_chamada_tem_timeout(fake_get):
    calls = fake_get([_FakeResponse(200, {})])

    zapsign.get_doc_detail("a")

    assert calls == [zapsign.REQUEST_TIMEOUT]


def test_espera_cresce_ate_60_segundos():
    waits = []
    flaky = zapsign.get_docs_page.retry_with(sleep=waits.append)

    def always_503(url, headers=None, timeout=None):
        return _FakeResponse(503)

    original = zapsign.requests.get
    zapsign.requests.get = always_503
    try:
        with pytest.raises(requests.HTTPError):
            flaky("https://zapsign.invalid/docs/")
    finally:
        zapsign.requests.get = original

    assert waits == sorted(waits)
    assert waits[0] >= 2
    assert max(waits) == 60
    assert sum(waits) <= 240
