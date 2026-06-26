## Sobre o Projeto

Este repositório contém o código e os resultados da pesquisa **"Piso Salarial da Enfermagem: Efeitos sobre Emprego e Salários"**.

O estudo investiga os efeitos da **Lei nº 14.434/2022**, que instituiu o piso salarial nacional para os profissionais de enfermagem, sobre a dinâmica de emprego formal e a estrutura salarial da categoria. A análise utiliza microdados do **Novo CAGED** (Cadastro Geral de Empregados e Desempregados) para o período de janeiro de 2020 a 2026.

---

## Contexto e Motivação

A Lei nº 14.434, sancionada em agosto de 2022, estabeleceu pisos salariais nacionais diferenciados por categoria profissional:

| Categoria                           | Piso Salarial (R$) |
|-------------------------------------|--------------------|
| Enfermeiro                          | R$ 4.750,00        |
| Técnico de Enfermagem               | R$ 3.325,00        |
| Auxiliar de Enfermagem / Parteira   | R$ 2.375,00        |

A implementação da lei gerou intenso debate em torno de seus potenciais efeitos sobre o mercado de trabalho, especialmente no setor público e em municípios com menor capacidade fiscal. Este projeto busca oferecer evidências empíricas rigorosas sobre esses efeitos.

---

## Dados

### Novo CAGED (MTE/PDET)

- **Fonte**: Ministério do Trabalho e Emprego — PDET (FTP público)
- **Período**: Janeiro/2020 a Dezembro/2026
- **Cobertura**: Registros mensais de admissões, desligamentos e ajustes do mercado formal de trabalho
- **Tipos de arquivo**: MOV (movimentações), FOR (fora do prazo), EXC (exclusões)

Os dados são baixados automaticamente via FTP, descompactados do formato `.7z` e consolidados em arquivos `.parquet` por ano.

### Ocupações de Enfermagem (CBO 2002)

O projeto restringe a análise às seguintes ocupações:

| Código CBO     | Ocupação                         |
|----------------|----------------------------------|
| 2235-05 a 65   | Enfermeiros (13 subcategorias)   |
| 3222-05 a 45   | Técnicos de Enfermagem           |
| 3222-30 a 50   | Auxiliares de Enfermagem         |
| 5151-10        | Atendente de Enfermagem          |
| 5151-15        | Parteira Leiga                   |

### Deflator

Os salários nominais são deflacionados pelo **INPC** (Índice Nacional de Preços ao Consumidor/IBGE) para valores de **janeiro de 2026**.

---

## Metodologia

A pesquisa emprega uma estratégia de **Diferenças em Diferenças (DiD)** com tratamento contínuo, conforme o arcabouço de Callaway et al. (2025), aproveitando a variação na intensidade de exposição ao piso salarial entre municípios e categorias profissionais.

A **intensidade do tratamento** é mensurada pelo **Índice de Kaitz** — razão entre o piso salarial da categoria e o salário mediano local pré-tratamento — e por instrumentos do tipo **Bartik/shift-share** para isolar a variação exógena na exposição à política.

### Análises Descritivas

1. **Dinâmica do Emprego**
   - Evolução do saldo líquido de postos formais por categoria
   - Taxa de rotatividade mensal
   - Estoque de vínculos ativos (base: RAIS 2019 = 1.297.413 trabalhadores)

2. **Indicadores Salariais**
   - Distribuição dos salários reais (P10, P25, P50, P75, P90)
   - Proporção de trabalhadores com salário abaixo do piso
   - Índice de Kaitz por categoria e período

3. **Qualidade do Emprego** *(em desenvolvimento)*
   - Carga horária contratual
   - Natureza do vínculo (CLT, estatutário, temporário)

4. **Perfil Sociodemográfico** *(em desenvolvimento)*
   - Sexo, raça/cor, faixa etária, escolaridade
   - Distribuição regional (UF e município)

---

## Estrutura do Repositório

```
piso-enfermagem/
│
├── codigo/
│   ├── 00 - leitura.R      # Download, descompactação e consolidação do Novo CAGED
│   ├── 01 - dados.R        # Filtragem, tratamento e deflacionamento dos dados
│   ├── 02 - tabelas.R      # Geração das tabelas de análise
│   └── 03 - gráficos.R     # Geração dos gráficos
│
├── docs/
│   ├── artigos/            # Literatura de referência (PDFs)
│   └── dados/              # Dados auxiliares (deflator, etc.) — não versionados
│
├── output/
│   └── tabelas.xlsx        # Tabelas de resultados
│
└── README.Rmd              # Este arquivo
```

> **Nota:** Os microdados brutos do Novo CAGED (arquivos `.txt`, `.parquet` e `.7z`) **não estão incluídos** neste repositório devido ao volume (dezenas de GB). O script `00 - leitura.R` automatiza o download diretamente do FTP do MTE.

---

## Como Reproduzir

### Pré-requisitos

- **R** ≥ 4.2.0
- **7-Zip** instalado em `C:/Program Files/7-Zip/7z.exe` (para descompactação)
- Pacotes R (instalados automaticamente via `pacman`):
  - `tidyverse`, `data.table`, `arrow`, `curl`, `fs`
  - `openxlsx`, `janitor`

### Passos

Execute os scripts na ordem numérica:

```r
# 1. Baixar e consolidar os dados do Novo CAGED (processo lento — pode levar horas)
source("codigo/00 - leitura.R")

# 2. Tratar e filtrar os dados de enfermagem
source("codigo/01 - dados.R")

# 3. Gerar as tabelas descritivas
source("codigo/02 - tabelas.R")

# 4. Gerar os gráficos
source("codigo/03 - gráficos.R")
```

> O script `00` realiza o download de todos os meses disponíveis (2020–2026) e pode consumir tempo e espaço em disco consideráveis. Arquivos já baixados são automaticamente pulados.

---

## Referências

**Política analisada**

- Brasil. *Lei nº 14.434, de 4 de agosto de 2022*. Institui o Piso Salarial Nacional da Enfermagem.
- COFEN. *Cartilha do Piso da Enfermagem*, 2022.

**Metodologia econométrica**

- CALLAWAY, B.; GOODMAN-BACON, A.; SANT'ANNA, P. H. C. Difference-in-Differences with a Continuous Treatment. *Journal of Econometrics*, 2025.
- BORUSYAK, K.; HULL, P.; JARAVEL, X. A Practical Guide to Shift-Share Instruments. *Review of Economic Studies*, 2024.
- PINKHAM, A. et al. Bartik Instruments: What, When, Why, and How. *American Economic Review*, 2019.
- LUDUVICE, A. et al. Minimum Wage, Business Dynamism. 2024.

**Trabalhos relacionados**

- CARVALHO, G. C. D. *Análise de Impacto da Criação do Piso Salarial para Profissionais de Enfermagem*. TCC, 2024.

---

## Equipe

| Nome                  | Instituição                         |
|-----------------------|-------------------------------------|
| Theo Torres           | Ministério da Saúde                 |
| Guilherme Jardinetti  | Ministério da Saúde                 |
| Ivan Cecílio e Silva  | Ministério da Saúde                 |
| Felipe Duplat         | Ministério da Saúde                 |
