"""Prata → Ouro: base analítica final com salário real deflacionado.

Junta o CAGED de enfermagem (prata) ao deflator INPC e calcula ``salreal``,
deflacionando os salários nominais para o mês-base (jan/2026), como em
``codigo/01 - dados.R`` (linhas 87-90). O resultado, ``caged_analitico.parquet``,
é a base que a análise em R (pasta ``codigo/``) passa a consumir.
"""

from __future__ import annotations

from pathlib import Path

from .config import Settings
from .constants import ANO_BASE_DEFLATOR, MES_BASE_DEFLATOR
from .db import connect, copy_to_parquet, count_rows, parquet_glob


def build_caged_ouro(settings: Settings) -> Path:
    """Executa o passo prata→ouro e retorna o arquivo da base analítica."""
    prata = settings.require("PISO_PRATA/caged_enfermagem", settings.caged_prata_dir)
    deflator = settings.require("PISO_DEFLATOR", settings.deflator)
    con = connect(settings.duckdb_threads)

    caged = f"read_parquet('{parquet_glob(prata)}', union_by_name=true)"
    defl = f"read_parquet('{deflator}')"

    query = f"""
    WITH base AS (
      SELECT (SELECT inpc FROM {defl}
              WHERE ano = {ANO_BASE_DEFLATOR} AND mes = {MES_BASE_DEFLATOR}) AS inpc_base
    )
    SELECT
      c.*,
      c.salario * (base.inpc_base / d.inpc) AS salreal
    FROM {caged} AS c
    LEFT JOIN {defl} AS d ON c.ano = d.ano AND c.mes = d.mes
    CROSS JOIN base
    """

    destino = settings.caged_ouro_file
    copy_to_parquet(con, query, destino)
    total = count_rows(con, f"read_parquet('{destino}')")
    print(f"[prata→ouro] {prata} + deflator → {destino}  ({total:,} linhas)")
    con.close()
    return destino
