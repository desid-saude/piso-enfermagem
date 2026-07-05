"""Definições de negócio da enfermagem — fonte única para Python e (futuramente) R.

Replica exatamente a lógica de ``codigo/01 - dados.R`` (linhas 59-85): os códigos
CBO 2002 das ocupações de enfermagem, o mapeamento para categoria e o piso salarial
instituído pela Lei nº 14.434/2022.
"""

from __future__ import annotations

# CBO 2002 → categoria de enfermagem
CATEGORIA_POR_CBO: dict[int, str] = {
    # Enfermeiros (2235-05 a 65)
    **{cbo: "enfermeiro" for cbo in (
        223505, 223510, 223515, 223520, 223525, 223530, 223535,
        223540, 223545, 223550, 223555, 223560, 223565,
    )},
    # Técnicos de enfermagem
    **{cbo: "tecnico_enfermagem" for cbo in (322205, 322210, 322215, 322220, 322245)},
    # Auxiliares de enfermagem (inclui atendente 515110)
    **{cbo: "auxiliar_enfermagem" for cbo in (322230, 322235, 322250, 515110)},
    # Parteira
    515115: "parteira",
}

CBOS_ENFERMAGEM: tuple[int, ...] = tuple(CATEGORIA_POR_CBO.keys())

# Piso salarial nacional por categoria (Lei nº 14.434/2022), em R$ nominais.
PISO_POR_CATEGORIA: dict[str, float] = {
    "enfermeiro": 4750.0,
    "tecnico_enfermagem": 3325.0,
    "auxiliar_enfermagem": 2375.0,
    "parteira": 2375.0,
}

# Mês/ano base para deflacionar os salários reais (janeiro de 2026).
ANO_BASE_DEFLATOR = 2026
MES_BASE_DEFLATOR = 1
