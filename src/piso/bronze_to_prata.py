"""Bronze → Prata: CAGED bruto → subconjunto de enfermagem, limpo e tipado.

Replica a limpeza de ``codigo/01 - dados.R``: normaliza nomes de colunas, filtra os
CBOs de enfermagem, deriva ``ano``/``mes``/``data``, ``categoria``, ``piso`` e
``saldo_ajustado`` (a exclusão ``EXC`` inverte o sinal do saldo). Grava parquet
particionado por ano na camada prata.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from .config import Settings
from .constants import CATEGORIA_POR_CBO, CBOS_ENFERMAGEM, PISO_POR_CATEGORIA
from .db import connect, copy_to_parquet, count_rows, parquet_glob


def clean_name(nome: str) -> str:
    """snake_case sem acentos (equivalente ao janitor::clean_names do R)."""
    nfkd = unicodedata.normalize("NFKD", str(nome))
    sem_acento = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    s = re.sub(r"[^\w]+", "_", sem_acento.strip().lower())
    return s.strip("_")


def _rename_projection(con, source_sql: str) -> str:
    """Projeção que renomeia cada coluna original para o nome limpo."""
    colunas = con.execute(f"DESCRIBE SELECT * FROM {source_sql}").fetchall()
    return ", ".join(f'"{orig}" AS {clean_name(orig)}' for orig, *_ in colunas)


def _categoria_case() -> str:
    """CASE que mapeia cbo2002ocupacao → categoria, a partir de constants.py."""
    ramos = "\n".join(
        f"      WHEN cbo2002ocupacao = {cbo} THEN '{cat}'"
        for cbo, cat in CATEGORIA_POR_CBO.items()
    )
    return f"CASE\n{ramos}\n      ELSE NULL END"


def _piso_case() -> str:
    """CASE que mapeia categoria → piso salarial, a partir de constants.py."""
    ramos = "\n".join(
        f"      WHEN categoria = '{cat}' THEN {piso}"
        for cat, piso in PISO_POR_CATEGORIA.items()
    )
    return f"CASE\n{ramos}\n      ELSE NULL END"


def build_caged_prata(settings: Settings) -> Path:
    """Executa o passo bronze→prata do CAGED e retorna o diretório de saída."""
    origem = settings.require("PISO_BRONZE_CAGED", settings.bronze_caged)
    con = connect(settings.duckdb_threads)

    fonte = f"read_parquet('{parquet_glob(origem)}', union_by_name=true)"
    projecao = _rename_projection(con, fonte)
    cbos = ", ".join(str(c) for c in CBOS_ENFERMAGEM)

    # 1) normaliza nomes; 2) filtra enfermagem; 3) deriva colunas de negócio.
    limpo = f"SELECT {projecao} FROM {fonte}"
    query = f"""
    WITH limpo AS (
      {limpo}
    ),
    enfermagem AS (
      SELECT
        *,
        {_categoria_case()} AS categoria,
        CAST(substr(CAST(competenciamov AS VARCHAR), 1, 4) AS INTEGER) AS ano,
        CAST(substr(CAST(competenciamov AS VARCHAR), 5, 2) AS INTEGER) AS mes
      FROM limpo
      WHERE cbo2002ocupacao IN ({cbos})
    )
    SELECT
      *,
      make_date(ano, mes, 1) AS data,
      {_piso_case()} AS piso,
      CASE WHEN tipo = 'EXC' THEN -saldomovimentacao ELSE saldomovimentacao END AS saldo_ajustado
    FROM enfermagem
    """

    destino = settings.caged_prata_dir
    copy_to_parquet(con, query, destino, partition_by="ano")
    total = count_rows(con, f"read_parquet('{parquet_glob(destino)}', union_by_name=true)")
    print(f"[bronze→prata] {origem} → {destino}  ({total:,} linhas de enfermagem)")
    con.close()
    return destino
