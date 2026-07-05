"""Configuração da pipeline a partir de variáveis de ambiente.

Cada integrante copia ``.env.example`` para ``.env`` (não versionado) e ajusta os
caminhos para os dados no servidor. O mínimo necessário é definir ``PISO_DATA_ROOT``
e os diretórios de origem da bronze; ``prata`` e ``ouro`` são derivados da raiz
quando não informados explicitamente.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Caminhos e parâmetros da pipeline, lidos do ambiente / arquivo ``.env``."""

    model_config = SettingsConfigDict(
        env_prefix="PISO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Raiz do projeto de dados no servidor (ex.: /mnt/data/estudos/piso_enfermagem).
    data_root: Path = Field(default=Path("/mnt/data/estudos/piso_enfermagem"))

    # Camadas derivadas — se não setadas, são resolvidas a partir de data_root.
    prata: Path | None = None
    ouro: Path | None = None

    # Origens da bronze — vivem em outros diretórios do servidor.
    bronze_caged: Path = Field(default=Path("/mnt/data/bronze/novo_caged"))
    bronze_rais: Path = Field(default=Path("/mnt/data/bronze/rais"))

    # Deflator INPC (parquet gerado pelo passo `piso deflator`).
    deflator: Path | None = None

    # Origem do deflator (planilha bruta) usada pelo passo `piso deflator`.
    deflator_xlsx: Path | None = None

    duckdb_threads: int = 4

    def model_post_init(self, __context: object) -> None:  # noqa: D401
        if self.prata is None:
            self.prata = self.data_root / "prata"
        if self.ouro is None:
            self.ouro = self.data_root / "ouro"
        if self.deflator is None:
            self.deflator = self.prata / "deflator.parquet"

    # --- Caminhos de artefatos ------------------------------------------------
    @property
    def caged_prata_dir(self) -> Path:
        """Diretório particionado do CAGED de enfermagem na camada prata."""
        return self.prata / "caged_enfermagem"

    @property
    def caged_ouro_file(self) -> Path:
        """Base analítica final (equivalente ao output/caged_clean.parquet do R)."""
        return self.ouro / "caged_analitico.parquet"

    # --- Validações -----------------------------------------------------------
    def ensure_layers(self) -> None:
        """Garante que prata e ouro existem, com mensagem clara em português."""
        for nome, caminho in (("PISO_PRATA", self.prata), ("PISO_OURO", self.ouro)):
            if not caminho.exists():
                raise SystemExit(
                    f"[config] O diretório {nome}={caminho} não existe.\n"
                    f"          Ajuste a variável no seu arquivo .env ou crie a pasta no servidor."
                )

    def require(self, nome: str, caminho: Path) -> Path:
        """Valida que um caminho de origem existe antes de usá-lo."""
        if not caminho.exists():
            raise SystemExit(
                f"[config] {nome}={caminho} não encontrado.\n"
                f"          Confira o caminho no seu arquivo .env."
            )
        return caminho


def load_settings() -> Settings:
    """Carrega as configurações (lê .env + variáveis de ambiente)."""
    return Settings()
