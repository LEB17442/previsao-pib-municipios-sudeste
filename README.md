# Previsão do PIB dos municípios do Sudeste

Projeto de Aprendizado de Máquina para prever o PIB municipal e a categoria de crescimento em 2024 nos estados de Espírito Santo, Minas Gerais, Rio de Janeiro e São Paulo.

## Entregas

| Entrega | Onde está |
| --- | --- |
| Relatório técnico final em PDF | `relatorio/relatorio_final.pdf` |
| **Previsões de 2024** (PIB e categoria de crescimento, 1.668 municípios) | `outputs/previsoes_finais_2024.csv` |
| Dataset tratado usado no treinamento | `data/processed/base_modelagem.csv` |
| Descrição das variáveis, dos alvos e das previsões; instruções de download | `docs/dados_tratados_e_previsoes.md` |
| Fontes e campos da base bruta | `docs/dicionario_dados.md` |
| Notebooks, na ordem de execução | `notebooks/01_coleta.ipynb` a `notebooks/06_classificacao_rf.ipynb` |
| Métricas de 2023 e comparação dos modelos | `outputs/metricas_*.csv`, `outputs/comparacao_*_2023.csv` |

| Abordagem | Modelos | Métricas (teste em 2023) |
| --- | --- | --- |
| Regressão | Regressão Linear (`03`), Random Forest Regressor (`04`) | R² e MAPE |
| Classificação | Regressão Logística (`05`), Random Forest Classifier (`06`) | F1-score e matriz de confusão |

Todos os modelos treinam com dados até 2022, são avaliados contra o PIB oficial de 2023 e depois são reajustados com dados até 2023 para prever 2024.

## Ambiente inicial

Na raiz do projeto, execute no PowerShell com Python 3.12 (versão verificada: 3.12.14):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyter lab
```

No macOS ou Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m jupyter lab
```

Os arquivos usados na entrega já estão no repositório e são regenerados pelos notebooks. O arquivo outputs/regressao_linear_2024.csv preserva o experimento linear inicial, anterior à seleção documentada.

## Coleta e integração

1. Execute todas as células de `notebooks/01_coleta.ipynb` para baixar o PIB do IBGE e gerar `data/raw/base_integrada.csv`.
2. Na raiz, execute `.\.venv\Scripts\python.exe integrar_sidra.py`. Use o arquivo gerado `data/raw/base_integrada_sidra.csv` como entrada do pré-processamento. Consulte `docs/dicionario_dados.md` para as fontes, unidades e lacunas.
3. Execute todas as células de `notebooks/02_eda_preprocessamento.ipynb` (ou `python preprocessamento.py`) para a análise exploratória e para gerar `data/processed/base_modelagem.csv`, a base tratada usada por todos os modelos.
4. Execute todas as células de `notebooks/03_regressao_linear.ipynb`. O notebook chama `comparar_regressoes.py`, publica as métricas em `outputs/metricas_regressao_linear.csv`, usadas automaticamente na consolidação, e gera `outputs/regressao_linear_2024_selecionada.csv`, arquivo da regressão linear para a consolidação do grupo.
5. Execute todas as células de `notebooks/04_random_forest_regressao.ipynb` para escolher os hiperparâmetros (validação em 2022), avaliar em 2023 e gerar `outputs/regressao_rf_2024.csv` e `outputs/metricas_rf_regressao.csv`.

## Validação temporal

O ajuste para a validação usa anos-alvo até 2022. A comparação com o PIB oficial de 2023 usa R² e MAPE. A regressão com menor MAPE é reajustada com dados até 2023 e produz uma previsão para cada um dos 1.668 municípios. Os cortes são por ano de referência e a análise é retrospectiva.

## Classificação — Amanda

Após preparar `data/processed/base_modelagem.csv`, execute na raiz:

```bash
python classificacao_logistica.py
```

Ou execute `notebooks/05_classificacao_logistica.ipynb`. A avaliação usa treino até 2022 e teste em 2023; o ajuste final até 2023 gera `outputs/classificacao_logistica_2024.csv`. F1 por classe, macro e ponderado ficam em `outputs/metricas_logistica.csv`, e a matriz em `outputs/matriz_confusao_logistica_2023.csv`. Critérios e análise: `docs/contribuicao_classificacao_logistica.md`.

## Random Forest Classifier e consolidação — Luma

Depois de gerar os resultados dos demais modelos, execute na raiz:

```bash
python classificacao_rf.py
python consolidar_previsoes.py
```

Ou execute `notebooks/06_classificacao_rf.ipynb` (cerca de 2 minutos). O classificador usa as mesmas classes e entradas da Regressão Logística; os hiperparâmetros são escolhidos treinando até 2021 e validando em 2022, o teste usa treino até 2022 e avaliação em 2023, e o ajuste final até 2023 gera `outputs/classificacao_rf_2024.csv`. Métricas em `outputs/metricas_rf_classificacao.csv` e matriz em `outputs/matriz_confusao_rf_2023.csv`.

`consolidar_previsoes.py` não reajusta modelos: lê os CSVs de todos, escolhe a regressão pelo menor MAPE de 2023 e a classificação pelo maior F1 macro de 2023 (`outputs/comparacao_*_2023.csv`) e gera `outputs/previsoes_finais_2024.csv`, com PIB previsto e classe prevista dos 1.668 municípios. Análise: `docs/contribuicao_classificacao_rf.md`.

## Relatório

O relatório técnico final é editado no Overleaf e entregue em PDF em `relatorio/relatorio_final.pdf`. As figuras usadas nele estão em `outputs/figuras/`.

## Verificação da entrega

Os seis notebooks e a consolidação foram executados em sequência com Python 3.12.14 e as versões fixadas em requirements.txt. A reexecução selecionou o Random Forest Regressor pelo MAPE de 9,00% e a Regressão Logística pelo F1 macro de 0,2434, contra 0,2341 do Random Forest Classifier. Os resultados anteriores do classificador Random Forest foram substituídos pelos resultados reproduzidos nessa execução.
