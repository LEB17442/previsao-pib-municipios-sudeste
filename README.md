# Previsão do PIB dos municípios do Sudeste

Projeto de Aprendizado de Máquina para prever o PIB municipal e a categoria de crescimento em 2024 nos estados de Espírito Santo, Minas Gerais, Rio de Janeiro e São Paulo.

## Ambiente inicial

Na raiz do projeto, execute no PowerShell com Python 3.10 ou superior:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyter lab
```

## Coleta e integração

1. Execute todas as células de `notebooks/01_coleta.ipynb` para baixar o PIB do IBGE e gerar `data/raw/base_integrada.csv`.
2. Na raiz, execute `.\.venv\Scripts\python.exe integrar_sidra.py`. Use o arquivo gerado `data/raw/base_integrada_sidra.csv` como entrada do pré-processamento. Consulte `docs/dicionario_dados.md` para as fontes, unidades e lacunas.
3. Execute todas as células de `notebooks/03_regressao_linear.ipynb`. O notebook chama `comparar_regressoes.py`, mostra as métricas e gera `outputs/regressao_linear_2024_selecionada.csv`, arquivo da regressão linear para a consolidação do grupo.

## Validação temporal

O ajuste para a validação usa anos-alvo até 2022. A comparação com o PIB oficial de 2023 usa R² e MAPE. A regressão com menor MAPE é reajustada com dados até 2023 e produz uma previsão para cada um dos 1.668 municípios. Os cortes são por ano de referência e a análise é retrospectiva.
