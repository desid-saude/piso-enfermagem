
######################################################################################################
# FUNDAÇÃO DE APOIO À PESQUISA DO DISTRITO FEDERAL (FAPDF)                                           #
# SELEÇÃO DE PROPOSTAS DE PESQUISA CIENTÍFICA, TECNOLÓGICA E INOVAÇÃO                                #
# EDITAL 06/2026                                                                                     #
#                                                                                                    #
#----------------------------------------------------------------------------------------------------#
# DESCRIÇÃO DA ATIVIDADE:                                                                            #
#                                                                                                    #
# Análise exploratória dos dados do Novo Caged para a área de enfermagem.                            #
#                                                                                                    #
#----------------------------------------------------------------------------------------------------#
# Autores: Theo Torres, Guilherme Jardinetti, Felipe Duplat                                          #
# Data: 03/2026                                                                                      #
# Versão: 1.0                                                                                        #
#----------------------------------------------------------------------------------------------------#

#--- DEFINIR DIRETÓRIO ---

# Diretório raiz:
setwd(file.path("C:/Users", Sys.info()[["user"]], "OneDrive - Ministério da Saúde/- Atividades/Projetos/piso-enfermagem"))

# Pasta de dados:
dados = file.path("C:/Users", Sys.info()[["user"]], "OneDrive - Ministério da Saúde/Bases de dados//")


#--- CARREGAR OS PACOTES ---
if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse,
               arrow,
               openxlsx)


#--- CARREGAR DADOS ------------------------
nc_clean = read_parquet("output/caged_clean.parquet")



#--- GERAR TABELAS -------------------------

#--- DINÂMICA DE EMPREGOS --- estoque de enfermeiros ativos em dez/2019 era de 1.297.413 (fonte: RAIS/MTE)
estoque_ini = 1297413

# Rotatividade:
tab1.1 = nc_clean %>%
  summarise(admissoes     = sum(saldo_ajustado == 1,  na.rm = TRUE),
            desligamentos = sum(saldo_ajustado == -1, na.rm = TRUE),
            saldo         = sum(saldo_ajustado,       na.rm = TRUE),
            .by = c(data, categoria)) %>%
  arrange(data) %>%
  mutate(estoque      = estoque_ini + cumsum(saldo),
         rotatividade = (admissoes + desligamentos) / (2 * estoque) * 100)

# Evolução por tipo de estabelecimento:
tab1.2 = nc_clean %>%
  summarise()


#--- INDICADORES SALARIAIS ---

# Tendência central:
tab2.1 = nc_clean %>%
  summarise(
    media   = mean(salreal, na.rm = TRUE),
    p10     = quantile(salreal, 0.10, na.rm = TRUE),
    p25     = quantile(salreal, 0.25, na.rm = TRUE),
    p50     = quantile(salreal, 0.50, na.rm = TRUE), # mediana
    p75     = quantile(salreal, 0.75, na.rm = TRUE),
    p90     = quantile(salreal, 0.90, na.rm = TRUE),
    .by = data
  ) %>%
  arrange(data)

# Abaixo do piso:
tab2.2 = nc_clean %>%
  summarise(share  = mean(salreal < piso, na.rm = TRUE) * 100, ## ou sal / piso
            median = median(salreal, na.rm = TRUE),
            .by = c(data, categoria)) %>%
  arrange(data)

# Índice de Kaitz:
tab2.3 = nc_clean %>%
  summarise(
    mediana = median(salreal, na.rm = TRUE),
    piso = first(piso),
    kaitz = piso / mediana,
    .by = c(data, categoria)
  )


#--- QUALIDADE DO EMPREGO ---

# horas de trabalho
# natureza do vínculo


#--- PERFIL ---

# idade, escolaridade, raça, sexo, uf, mun



#--- EXPORTAR TABELAS -------------------------
tabs = ls(pattern = "^tab")
write.xlsx(mget(tabs[sapply(tabs, \(x) is.data.frame(get(x)))]), "output/tabelas.xlsx", overwrite = TRUE)


