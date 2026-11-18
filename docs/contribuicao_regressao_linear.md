# Previsão do PIB municipal do Sudeste

## Introdução

Este trabalho estima o Produto Interno Bruto (PIB) de 2024 dos municípios da Região Sudeste e busca prever a categoria de crescimento econômico de cada município em relação a 2023. A regressão estima o valor do PIB em milhares de reais correntes. A classificação trata a categoria de crescimento como um alvo separado. Esta seção descreve o primeiro modelo de regressão e sua avaliação temporal.

## Dados

A base inicial utiliza a série do [PIB dos Municípios do IBGE](https://ftp.ibge.gov.br/Pib_Municipios/2022_2023/base/) para o período de 2010 a 2023. O recorte inclui Espírito Santo, Minas Gerais, Rio de Janeiro e São Paulo. Foram obtidos 23.352 registros, correspondentes a 1.668 municípios em 14 anos, com uma linha por código IBGE do município e ano de referência. A coleta verificou a unicidade dessa chave e a presença de valores positivos de PIB.

Além do PIB total, a base registra o valor adicionado bruto da agropecuária, da indústria e dos serviços, em milhares de reais correntes. A publicação não apresenta essa abertura setorial para 2022 e 2023. A coleta mantém os valores ausentes nesses anos. As demais pesquisas do SIDRA indicadas no enunciado ainda serão avaliadas quanto à cobertura municipal e à disponibilidade nos cortes de previsão.

## Regressão linear

O modelo inicial estima o PIB de um município em determinado ano como uma função linear de seu PIB no ano anterior. A regressão por mínimos quadrados ajusta um intercepto e uma inclinação comuns aos municípios. Cada par de treino usa dois anos consecutivos do mesmo município.

Na avaliação, o ajuste usou pares cujo ano-alvo era no máximo 2022. O PIB de 2022 serviu de entrada para prever 2023, e os valores oficiais de 2023 foram usados para calcular as métricas. Em seguida, o modelo foi reajustado com pares até 2023 e usou o PIB de 2023 para gerar as previsões de 2024 para os 1.668 municípios.

## Resultado com a base tratada

O script passa a ler exclusivamente data/processed/base_modelagem.csv. Compara o PIB anterior em nível com uma regressão que acrescenta as variáveis compartilhadas do pré-processamento, incluindo UF. A imputação pela mediana e a padronização são ajustadas apenas no treino. O PIB anterior em nível também é padronizado na versão ampliada para evitar problemas numéricos.

Na validação em 2023, a regressão com PIB anterior obteve R² de 0,995504 e MAPE de 17,94%. A versão ampliada com a base tratada obteve R² de 0,995379 e MAPE de 28,06%. Pelo menor MAPE, foi selecionada a primeira versão, reajustada com dados até 2023. O CSV de previsões contém os 1.668 municípios.

Estes resultados substituem a comparação anterior com a base bruta, que usava outras variáveis e defasagens e obtinha MAPE de 13,21%. O Random Forest Regressor mantém o menor MAPE na comparação do grupo, com 9,00%. As métricas calculadas são publicadas em outputs/metricas_regressao_linear.csv e lidas pela consolidação.

O exercício é retrospectivo e os cortes são por ano de referência. A seleção usa 2023 como validação. Os dados atuais não preservam versões históricas por data de divulgação.
