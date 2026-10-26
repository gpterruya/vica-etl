import io

import pandas as pd
import pytest

import load.storage as storage_module
from transform.pipeline import transform


def _sample_df():
    return pd.DataFrame([
        {
            "token": "a",
            "created_at": "2026-10-01T12:00:00Z",
            "data de nascimento": "15/03/1990",
            "estado": "SP",
            "cidade": "São Paulo",
            "bairro": "Moema",
            "espécie": "Cachorro",
            "raça": "SRD",
            "porte": "Médio",
            "resposta_sem_variavel": "Injetável/Inalatória",
            "nome do animal": "Rex",
        },
        {
            "token": "b",
            "created_at": None,
            "data de nascimento": None,
            "estado": None,
            "cidade": None,
            "bairro": None,
            "espécie": None,
            "raça": None,
            "porte": None,
            "resposta_sem_variavel": None,
            "nome do animal": "Mia",
        },
    ])


def test_transform_preserva_linhas_e_colunas_de_entrada():
    df = transform(_sample_df())

    assert len(df) == 2
    assert {"idade_adotante", "faixa_etaria"} <= set(df.columns)
    assert not [c for c in df.columns if not str(c).strip()]
    assert df.set_index("token").loc["a", "resposta_sem_variavel"] == "Injetável/Inalatória"
    assert df.set_index("token").loc["a", "nome do animal"] == "Rex"


class _FakeBlob:
    def __init__(self, sink, name):
        self.sink = sink
        self.name = name

    def upload_from_string(self, content, content_type=None):
        self.sink[self.name] = (content, content_type)


class _FakeBucket:
    def __init__(self, sink):
        self.sink = sink

    def blob(self, name):
        return _FakeBlob(self.sink, name)


class _FakeClient:
    sink = {}

    def bucket(self, name):
        return _FakeBucket(self.sink)


@pytest.fixture
def fake_storage(monkeypatch):
    _FakeClient.sink = {}
    monkeypatch.setattr(storage_module.storage, "Client", _FakeClient)
    return _FakeClient.sink


def test_upload_csv_gera_csv_sem_cabecalho_vazio(fake_storage):
    df = transform(_sample_df())

    result = storage_module.upload_csv(df)

    content, content_type = fake_storage[storage_module.OUTPUT_FILE]
    assert result["rows"] == 2
    assert content.startswith("﻿")
    assert content_type.startswith("text/csv")

    parsed = pd.read_csv(io.StringIO(content), encoding="utf-8-sig")
    assert len(parsed) == 2
    assert "resposta_sem_variavel" in parsed.columns
    assert not [c for c in parsed.columns if str(c).lower().startswith("unnamed:")]
    assert not [c for c in parsed.columns if not str(c).strip()]
