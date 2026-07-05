"""Pipeline de ingestão e tratamento de dados do estudo do Piso da Enfermagem.

Arquitetura medalhão (bronze → prata → ouro) sobre parquet, consultada com DuckDB.
A análise (tabelas e gráficos) permanece em R, na pasta ``codigo/``, e consome a
camada ouro produzida aqui.
"""

__version__ = "0.1.0"
