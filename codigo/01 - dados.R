
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
               janitor,
               data.table,
               openxlsx)


#--- IMPORTAR NOVO CAGED ------------------------

#--- AUXILIARES ---
deflator = paste0(dados, "deflator.xlsx")


#--- NOVO CAGED ---
novo_caged = setNames(
  lapply(list.files(path       = paste0(dados, "/Novo Caged"),
                    pattern    = "\\.parquet$",
                    recursive  = TRUE,
                    full.names = TRUE
                  ), read_parquet),
             basename(dirname(list.files(path       = paste0(dados, "/Novo Caged"),
                                         pattern    = "\\.parquet$",
                                         recursive  = TRUE,
                                         full.names = TRUE))))



#--- TRATAR DADOS --------------------------

# AUXILIARES:
cbo = c(223505, 223510, 223515, 223520, 223525, 223530, 223535, 223540, 223545, 223550, 223555, 223560, 223565,     # enfermeiros;
        322205, 322210, 322215, 322220, 322245,                                                                     # técnico de enfermagem;
        322230, 322235, 322250,                                                                                     # auxiliar de enfermagem;
        515110,                                                                                                     # atendente de enfermagem;
        515115)                                                                                                     # parteira.

#--- NOVO CAGED ---
nc_clean = lapply(novo_caged, function(df) {

  df %>%
    clean_names() %>%
    filter(cbo2002ocupacao %in% cbo) %>%                                           # apenas enfermeiros
    mutate(
      ano = as.numeric(substr(competenciamov, 1, 4)),
      mes = as.numeric(substr(competenciamov, 5, 6)),
      data = as.Date(paste0(ano, "-", mes, "-01")),
      categoria = case_when(cbo2002ocupacao %in% c(223505, 223510, 223515, 223520, 223525, 223530,
                                                   223535, 223540, 223545, 223550, 223555, 223560,
                                                   223565)                                         ~ "enfermeiro",
                            cbo2002ocupacao %in% c(322205, 322210, 322215, 322220, 322245)         ~ "tecnico_enfermagem",
                            cbo2002ocupacao %in% c(322230, 322235, 322250, 515110)                 ~ "auxiliar_enfermagem",
                            cbo2002ocupacao == 515115                                              ~ "parteira",
                            TRUE ~ NA_character_),
      piso      = case_when(categoria == "enfermeiro" ~ 4750,
                            categoria == "tecnico_enfermagem" ~ 3325,
                            categoria %in% c("auxiliar_enfermagem", "parteira") ~ 2375,
                            TRUE ~ NA_real_),
      saldo_ajustado = if_else(tipo == "EXC", -saldomovimentacao, saldomovimentacao)) %>%
    left_join(deflator, by = c("ano","mes")) %>%
    mutate(
      salreal = salario * (deflator$inpc[deflator$ano == 2026 & deflator$mes == 1] / inpc)             # deflacionando para jan/26
    )

}) %>% rbindlist(fill = TRUE)



#--- EXPORTAR DADOS --------------------------
write_parquet(nc_clean, "output/caged_clean.parquet")


