import pytest

import extract.zapsign as zapsign


def _detail(token, answers):
    return {
        "token": token,
        "name": f"doc {token}",
        "status": "signed",
        "created_at": "2026-10-01T12:00:00Z",
        "folder_path": "/",
        "signers": [{"name": "Fulano", "signed_at": "2026-10-01T12:30:00Z"}],
        "answers": answers,
    }


@pytest.fixture
def fake_api(monkeypatch):
    """Substitui as chamadas HTTP por respostas em memória."""

    def install(pages, details):
        def get_docs_page(url):
            return pages[url]

        def get_doc_detail(token):
            return details[token]

        monkeypatch.setattr(zapsign, "get_docs_page", get_docs_page)
        monkeypatch.setattr(zapsign, "get_doc_detail", get_doc_detail)

    return install


def test_variavel_so_com_espacos_nao_cria_coluna_vazia(fake_api):
    first = f"{zapsign.BASE_URL}/docs/"
    fake_api(
        {first: {"results": [{"token": "a"}], "next": None}},
        {"a": _detail("a", [
            {"variable": "   ", "value": "Injetável/Inalatória"},
            {"variable": " Nome do Animal ", "value": "Rex"},
        ])},
    )

    df = zapsign.extract()

    assert "" not in df.columns
    assert not [c for c in df.columns if not str(c).strip()]
    assert df.loc[0, "resposta_sem_variavel"] == "Injetável/Inalatória"
    assert df.loc[0, "nome do animal"] == "Rex"


def test_variavel_nula_ou_vazia_vai_para_resposta_sem_variavel(fake_api):
    first = f"{zapsign.BASE_URL}/docs/"
    fake_api(
        {first: {"results": [{"token": "a"}, {"token": "b"}], "next": None}},
        {
            "a": _detail("a", [{"variable": None, "value": "x"}]),
            "b": _detail("b", [{"variable": "", "value": "y"}]),
        },
    )

    df = zapsign.extract().set_index("token")

    assert df.loc["a", "resposta_sem_variavel"] == "x"
    assert df.loc["b", "resposta_sem_variavel"] == "y"


def test_mantem_a_primeira_resposta_sem_variavel_nao_nula(fake_api):
    first = f"{zapsign.BASE_URL}/docs/"
    fake_api(
        {first: {"results": [{"token": "a"}], "next": None}},
        {"a": _detail("a", [
            {"variable": " ", "value": None},
            {"variable": "", "value": "primeira"},
            {"variable": None, "value": "segunda"},
        ])},
    )

    df = zapsign.extract()

    assert df.loc[0, "resposta_sem_variavel"] == "primeira"


def test_percorre_todas_as_paginas(fake_api):
    first = f"{zapsign.BASE_URL}/docs/"
    second = f"{zapsign.BASE_URL}/docs/?page=2"
    fake_api(
        {
            first: {"results": [{"token": "a"}], "next": second},
            second: {"results": [{"token": "b"}], "next": None},
        },
        {
            "a": _detail("a", [{"variable": "cidade", "value": "São Paulo"}]),
            "b": _detail("b", [{"variable": "cidade", "value": "Campinas"}]),
        },
    )

    df = zapsign.extract()

    assert sorted(df["token"]) == ["a", "b"]


def test_documento_com_erro_fica_fora_sem_interromper(fake_api, monkeypatch):
    first = f"{zapsign.BASE_URL}/docs/"
    fake_api(
        {first: {"results": [{"token": "a"}, {"token": "falha"}], "next": None}},
        {"a": _detail("a", [])},
    )

    df = zapsign.extract()

    assert list(df["token"]) == ["a"]
