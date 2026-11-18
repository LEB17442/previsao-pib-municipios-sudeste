# Dataset tratado e previsões de 2024

Todos os arquivos são CSV em UTF-8, com separador vírgula e ponto decimal. Valores monetários estão em milhares de reais correntes (PIB nominal). Para baixar, clone o repositório ou use **Code → Download ZIP** no GitHub; cada CSV também pode ser baixado individualmente pelo botão *Download raw file* da página do arquivo.

| Arquivo | Conteúdo |
| --- | --- |
| `data/raw/base_integrada_sidra.csv` | Base bruta integrada (IBGE e SIDRA), uma linha por município e ano, 2010–2023. Campos em `docs/dicionario_dados.md`. |
| `data/processed/base_modelagem.csv` | Base tratada usada no treinamento de todos os modelos (descrita abaixo). |
| `outputs/previsoes_finais_2024.csv` | **Entrega final**: PIB previsto e categoria de crescimento prevista para 2024 nos 1.668 municípios do Sudeste. |
| `outputs/regressao_linear_2024_selecionada.csv`, `outputs/regressao_rf_2024.csv` | PIB previsto para 2024 por cada modelo de regressão. |
| `outputs/classificacao_logistica_2024.csv`, `outputs/classificacao_rf_2024.csv` | Categoria prevista para 2024 por cada classificador. |
| `outputs/metricas_*.csv`, `outputs/matriz_confusao_*.csv`, `outputs/comparacao_*_2023.csv` | Métricas da avaliação de 2023 (R², MAPE, F1, matrizes de confusão) e comparação entre modelos. |

## Base tratada: `data/processed/base_modelagem.csv`

Uma linha por município e **ano-alvo** *t*, de 2011 a 2024 (23.352 linhas = 1.668 municípios × 14 anos). A chave é `codigo_municipio` + `ano`. Toda variável explicativa usa apenas informação de anos ≤ *t*−1, de modo que nenhuma linha carrega dado do próprio ano ou futuro. A linha de 2024 (`conjunto = previsao`) tem os alvos vazios e recebe as variáveis usadas na previsão.

Imputação, padronização e codificação da UF **não** estão aplicadas no CSV: ficam no `Pipeline` de `preprocessamento.criar_preprocessador()` e são ajustadas apenas nas linhas de treino de cada corte, para não usar estatísticas de anos futuros.

### Identificação

| Coluna | Descrição |
| --- | --- |
| `codigo_municipio` | Código IBGE de sete dígitos |
| `municipio` | Nome do município |
| `uf` | Sigla do estado (ES, MG, RJ, SP); variável categórica usada nos modelos (*one-hot*) |
| `ano` | Ano-alvo *t* |
| `conjunto` | `historico` (2011–2023, alvo conhecido) ou `previsao` (2024) |

### Variáveis explicativas (17 numéricas + UF)

| Coluna | Descrição |
| --- | --- |
| `log_pib_lag1`, `log_pib_lag2` | log do PIB em *t*−1 e *t*−2 |
| `cresc_pib_lag1`, `cresc_pib_lag2` | Crescimento logarítmico do PIB em *t*−1 e *t*−2 |
| `cresc_pib_mediana_uf_lag1` | Mediana estadual de `cresc_pib_lag1` no ano *t* (choque macro conhecido em *t*−1) |
| `part_agro_ult`, `part_industria_ult`, `part_servicos_ult` | Participação do VAB setorial no PIB, último valor observado até *t*−1 |
| `defasagem_vab` | Anos entre *t* e o último VAB setorial observado (o VAB falta em 2022 e 2023) |
| `log_populacao_ult` | log da população estimada, último valor observado até *t*−1 |
| `defasagem_populacao` | Anos entre *t* e a última estimativa de população (falta em 2010, 2022 e 2023) |
| `log_pib_per_capita_lag1` | `log_pib_lag1 − log_populacao_ult` |
| `log_producao_agricola_lag1` | log(1 + valor da produção agrícola) em *t*−1 (PAM) |
| `cresc_producao_agricola_lag1` | Variação de `log_producao_agricola` entre *t*−2 e *t*−1 |
| `log_rebanho_bovino_lag1` | log(1 + efetivo bovino) em *t*−1 (PPM) |
| `sem_producao_agricola_lag1`, `sem_rebanho_bovino_lag1` | 1 se o indicador agropecuário está ausente em *t*−1 |

### Variáveis auxiliares e alvos

| Coluna | Descrição |
| --- | --- |
| `pib_lag1_mil_reais` | PIB oficial em *t*−1; base para reconstruir o PIB previsto e a variação |
| `pib_mil_reais` | **Alvo da regressão**: PIB nominal do ano *t* |
| `log_razao_pib` | log(PIB<sub>t</sub> / PIB<sub>t−1</sub>); alvo do Random Forest Regressor, que reconstrói o PIB como PIB<sub>t−1</sub> · e<sup>ŷ</sup> |
| `variacao_pib_pct` | 100 × (PIB<sub>t</sub> / PIB<sub>t−1</sub> − 1); **base do alvo da classificação** |

**Alvo da classificação** (calculado em `classificacao_logistica.categorizar`, não gravado no CSV), com `x = variacao_pib_pct`:

| Classe | Faixa |
| --- | --- |
| forte retração | x < −5 |
| retração | −5 ≤ x < −1 |
| estabilidade | −1 ≤ x ≤ 1 |
| crescimento moderado | 1 < x ≤ 5 |
| forte crescimento | x > 5 |

## Previsões finais: `outputs/previsoes_finais_2024.csv`

Uma linha para cada um dos 1.668 municípios. Gerado por `consolidar_previsoes.py`, que escolhe a regressão pelo menor MAPE de 2023 (Random Forest Regressor) e a classificação pelo maior F1 macro de 2023 (Regressão Logística).

| Coluna | Descrição |
| --- | --- |
| `codigo_municipio`, `municipio`, `uf`, `ano` | Identificação (ano = 2024) |
| `pib_2023_oficial_mil_reais` | PIB oficial de 2023 |
| `pib_previsto_2024_mil_reais` | **PIB previsto para 2024** pelo modelo de regressão selecionado |
| `variacao_prevista_pct` | Variação implícita entre o PIB previsto de 2024 e o oficial de 2023 (%) |
| `classe_prevista_2024` | **Categoria de crescimento prevista para 2024** pelo classificador selecionado |
| `modelo_regressao`, `modelo_classificacao` | Modelos que geraram as duas colunas acima |
| `pib_previsto_linear_mil_reais`, `pib_previsto_rf_mil_reais` | PIB previsto por cada modelo de regressão |
| `classe_logistica`, `classe_rf` | Categoria prevista por cada classificador |
| `classe_implicita_regressao` | Categoria correspondente a `variacao_prevista_pct`; serve para checar a coerência entre PIB e classe (coincidem em 95,0% dos municípios) |
