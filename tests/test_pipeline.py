"""Testa a pipeline ponta a ponta com fixtures minúsculos em um tmpdir."""

from __future__ import annotations

import duckdb
import pandas as pd
import pytest

from piso.bronze_to_prata import clean_name
from piso.cli import build_all  # noqa: F401  (garante importabilidade do CLI)
from piso.config import Settings
from piso.deflator import build_deflator
from piso.bronze_to_prata import build_caged_prata
from piso.prata_to_ouro import build_caged_ouro


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    root = tmp_path / "piso_enfermagem"
    prata = root / "prata"
    ouro = root / "ouro"
    bronze_caged = tmp_path / "bronze" / "novo_caged"
    for d in (prata, ouro, bronze_caged):
        d.mkdir(parents=True)

    # --- CAGED bruto (com nomes acentuados, para exercitar clean_name) ---------
    caged = pd.DataFrame(
        {
            "competênciamov": [202301, 202301, 202301, 202601],
            "cbo2002Ocupação": [223505, 322205, 999999, 223505],  # 999999 não é enfermagem
            "salário": [5000.0, 3000.0, 8000.0, 6000.0],
            "saldoMovimentação": [1, -1, 1, 1],
            "tipo": ["MOV", "MOV", "MOV", "EXC"],  # última linha é exclusão
        }
    )
    caged.to_parquet(bronze_caged / "dados.parquet", index=False)

    # --- Deflator INPC ---------------------------------------------------------
    deflator = pd.DataFrame(
        {"ano": [2023, 2026], "mes": [1, 1], "inpc": [100.0, 120.0]}
    )
    deflator_xlsx = prata / "deflator.xlsx"
    deflator.to_excel(deflator_xlsx, index=False)

    monkeypatch.setenv("PISO_DATA_ROOT", str(root))
    monkeypatch.setenv("PISO_BRONZE_CAGED", str(bronze_caged))
    monkeypatch.setenv("PISO_DEFLATOR_XLSX", str(deflator_xlsx))
    # Evita que um .env do repositório interfira no teste.
    monkeypatch.chdir(tmp_path)

    return Settings()


def test_clean_name_remove_acentos_e_normaliza():
    assert clean_name("Competência Mov") == "competencia_mov"
    assert clean_name("cbo2002Ocupação") == "cbo2002ocupacao"


def test_pipeline_completa(ambiente):
    settings = ambiente
    build_deflator(settings)
    build_caged_prata(settings)
    ouro = build_caged_ouro(settings)

    df = duckdb.sql(f"SELECT * FROM read_parquet('{ouro}')").df()

    # A ocupação não-enfermagem foi filtrada: sobram 3 linhas.
    assert len(df) == 3
    assert set(df["categoria"]) == {"enfermeiro", "tecnico_enfermagem"}

    # Piso por categoria.
    enf = df[df["categoria"] == "enfermeiro"].iloc[0]
    assert enf["piso"] == 4750.0
    tec = df[df["categoria"] == "tecnico_enfermagem"].iloc[0]
    assert tec["piso"] == 3325.0

    # EXC inverte o sinal do saldo.
    exc = df[df["tipo"] == "EXC"].iloc[0]
    assert exc["saldo_ajustado"] == -1

    # Salário real deflacionado para jan/2026 (base inpc=120).
    #   linha 2023-01 (inpc=100): 5000 * 120/100 = 6000
    #   linha 2026-01 (inpc=120, base): 6000 * 120/120 = 6000
    jan23 = df[(df["ano"] == 2023) & (df["categoria"] == "enfermeiro")].iloc[0]
    assert jan23["salreal"] == pytest.approx(6000.0)
    jan26 = df[df["ano"] == 2026].iloc[0]
    assert jan26["salreal"] == pytest.approx(6000.0)
