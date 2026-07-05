"""Interface de linha de comando da pipeline (Typer).

Uso típico no servidor::

    uv run piso deflator          # planilha INPC → prata/deflator.parquet
    uv run piso bronze-to-prata   # CAGED bruto → prata/caged_enfermagem/
    uv run piso prata-to-ouro     # prata + deflator → ouro/caged_analitico.parquet
    uv run piso build-all         # roda os três passos em ordem
"""

from __future__ import annotations

import typer

from .bronze_to_prata import build_caged_prata
from .config import load_settings
from .deflator import build_deflator
from .prata_to_ouro import build_caged_ouro

app = typer.Typer(
    add_completion=False,
    help="Pipeline de ingestão e tratamento de dados do Piso da Enfermagem.",
)


@app.command()
def deflator() -> None:
    """Ingere a planilha do INPC para prata/deflator.parquet."""
    settings = load_settings()
    settings.ensure_layers()
    destino = build_deflator(settings)
    typer.echo(f"[deflator] gravado em {destino}")


@app.command("bronze-to-prata")
def bronze_to_prata() -> None:
    """Trata o CAGED bruto e grava o subconjunto de enfermagem na prata."""
    settings = load_settings()
    settings.ensure_layers()
    build_caged_prata(settings)


@app.command("prata-to-ouro")
def prata_to_ouro() -> None:
    """Gera a base analítica deflacionada na camada ouro."""
    settings = load_settings()
    settings.ensure_layers()
    build_caged_ouro(settings)


@app.command("build-all")
def build_all() -> None:
    """Roda toda a pipeline: deflator → bronze→prata → prata→ouro."""
    settings = load_settings()
    settings.ensure_layers()
    build_deflator(settings)
    build_caged_prata(settings)
    build_caged_ouro(settings)
    typer.echo("[build-all] pipeline concluída.")


if __name__ == "__main__":
    app()
