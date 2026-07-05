"""Conexão e helpers finos de DuckDB.

Toda a transformação é feita com DuckDB consultando parquet diretamente — sem banco
persistente. Assim tanto o Python quanto o R (via ``arrow``) leem os mesmos arquivos.
"""

from __future__ import annotations

from pathlib import Path

import duckdb


def connect(threads: int = 4) -> duckdb.DuckDBPyConnection:
    """Abre uma conexão DuckDB em memória, configurada para a pipeline."""
    con = duckdb.connect(database=":memory:")
    con.execute(f"PRAGMA threads={int(threads)}")
    return con


def parquet_glob(diretorio: Path) -> str:
    """Glob recursivo de parquets dentro de um diretório, para read_parquet."""
    return str(diretorio / "**" / "*.parquet")


def copy_to_parquet(
    con: duckdb.DuckDBPyConnection,
    query: str,
    destino: Path,
    partition_by: str | None = None,
) -> None:
    """Materializa o resultado de ``query`` em parquet no ``destino``.

    Se ``partition_by`` for informado, escreve um diretório particionado (Hive);
    caso contrário, escreve um único arquivo parquet.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    if partition_by:
        destino.mkdir(parents=True, exist_ok=True)
        con.execute(
            f"COPY ({query}) TO '{destino}' "
            f"(FORMAT PARQUET, PARTITION_BY ({partition_by}), OVERWRITE_OR_IGNORE)"
        )
    else:
        con.execute(f"COPY ({query}) TO '{destino}' (FORMAT PARQUET)")


def count_rows(con: duckdb.DuckDBPyConnection, source_sql: str) -> int:
    """Conta linhas de uma fonte SQL (ex.: read_parquet('...'))."""
    return con.execute(f"SELECT count(*) FROM {source_sql}").fetchone()[0]
