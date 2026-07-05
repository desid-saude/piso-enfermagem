"""Ingestão do deflator INPC: planilha bruta (.xlsx) → prata/deflator.parquet."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .config import Settings


def _clean_names(colunas: list[str]) -> list[str]:
    """snake_case simples, no espírito do janitor::clean_names do R."""
    limpas = []
    for c in colunas:
        c = str(c).strip().lower()
        c = re.sub(r"[^\w]+", "_", c)
        limpas.append(c.strip("_"))
    return limpas


def build_deflator(settings: Settings) -> Path:
    """Lê o deflator em xlsx e grava como parquet na camada prata.

    Espera colunas ``ano``, ``mes`` e ``inpc`` (após limpeza dos nomes).
    """
    if settings.deflator_xlsx is None:
        raise SystemExit(
            "[deflator] Defina PISO_DEFLATOR_XLSX no seu .env apontando para a planilha do INPC."
        )
    origem = settings.require("PISO_DEFLATOR_XLSX", settings.deflator_xlsx)

    df = pd.read_excel(origem)
    df.columns = _clean_names(list(df.columns))

    faltando = {"ano", "mes", "inpc"} - set(df.columns)
    if faltando:
        raise SystemExit(
            f"[deflator] A planilha {origem} não tem as colunas {sorted(faltando)}.\n"
            f"          Colunas encontradas: {list(df.columns)}"
        )

    df = df[["ano", "mes", "inpc"]].copy()
    df["ano"] = df["ano"].astype("int64")
    df["mes"] = df["mes"].astype("int64")
    df["inpc"] = df["inpc"].astype("float64")

    destino = settings.deflator
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(destino, index=False)
    return destino
