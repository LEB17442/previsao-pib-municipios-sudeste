# Previsão do PIB dos municípios do Sudeste

Projeto de Aprendizado de Máquina para prever o PIB municipal e a categoria de crescimento em 2024 nos estados de Espírito Santo, Minas Gerais, Rio de Janeiro e São Paulo.

## Ambiente inicial

Na raiz do projeto, execute no PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyter lab
```

## Coleta e integração

A base integrada terá uma linha por município e ano, identificada pelo código IBGE de sete dígitos e pelo ano de referência. O notebook `notebooks/01_coleta.ipynb` será responsável por gerar `data/raw/base_integrada.csv`. As tabelas de origem, as unidades e a cobertura das variáveis serão registradas em `docs/dicionario_dados.md`.

## Validação temporal

Depois de executar o notebook de coleta, rode `python integrar_sidra.py` na raiz do projeto. O script gera `data/raw/base_integrada_sidra.csv` e mostra a cobertura anual dos indicadores. Use esse CSV como entrada para a etapa de limpeza.

Para avaliar a regressão, use o histórico até 2022 para prever o PIB de 2023 e compare as previsões com os valores oficiais usando R² e MAPE. Após a avaliação, reajuste o modelo com o histórico até 2023 para prever 2024. Em cada etapa, use apenas variáveis disponíveis no respectivo corte.
