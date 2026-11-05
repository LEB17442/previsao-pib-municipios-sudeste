# Previsão do PIB municipal do Sudeste

## Introdução

Este trabalho estima o Produto Interno Bruto (PIB) de 2024 dos municípios da Região Sudeste e busca prever a categoria de crescimento econômico de cada município em relação a 2023. A regressão estima o valor do PIB em milhares de reais correntes. A classificação trata a categoria de crescimento como um alvo separado. Esta seção descreve o primeiro modelo de regressão e sua avaliação temporal.

## Dados

A base inicial utiliza a série do [PIB dos Municípios do IBGE](https://ftp.ibge.gov.br/Pib_Municipios/2022_2023/base/) para o período de 2010 a 2023. O recorte inclui Espírito Santo, Minas Gerais, Rio de Janeiro e São Paulo. Foram obtidos 23.352 registros, correspondentes a 1.668 municípios em 14 anos, com uma linha por código IBGE do município e ano de referência. A coleta verificou a unicidade dessa chave e a presença de valores positivos de PIB.

Além do PIB total, a base registra o valor adicionado bruto da agropecuária, da indústria e dos serviços, em milhares de reais correntes. A publicação não apresenta essa abertura setorial para 2022 e 2023. A coleta mantém os valores ausentes nesses anos. As demais pesquisas do SIDRA indicadas no enunciado ainda serão avaliadas quanto à cobertura municipal e à disponibilidade nos cortes de previsão.

## Regressão linear

O modelo inicial estima o PIB de um município em determinado ano como uma função linear de seu PIB no ano anterior. A regressão por mínimos quadrados ajusta um intercepto e uma inclinação comuns aos municípios. Cada par de treino usa dois anos consecutivos do mesmo município.

Na avaliação, o ajuste usou pares cujo ano-alvo era no máximo 2022. O PIB de 2022 serviu de entrada para prever 2023, e os valores oficiais de 2023 foram usados para calcular as métricas. Em seguida, o modelo foi reajustado com pares até 2023 e usou o PIB de 2023 para gerar as previsões de 2024 para os 1.668 municípios.

## Resultado inicial

A segunda regressão acrescentou valor da produção agrícola, rebanho bovino e estimativa populacional com defasagem de dois anos. Os indicadores foram transformados por log(1 + valor), e cada ausência foi representada por um indicador binário. A população de 2022 está ausente na fonte, inclusive na previsão de 2024.

Nos mesmos 1.668 municípios em 2023, a versão ampliada obteve R² de 0,995463 e MAPE de 13,21%, contra 0,995504 e 17,94% para o PIB anterior. A redução de 4,72 pontos percentuais no MAPE motivou a seleção da versão ampliada. Após o reajuste até 2023, ela gerou 1.668 previsões positivas para 2024. Como 2023 orientou a seleção, suas métricas também refletem essa escolha.

O exercício usa cortes por ano de referência. Os valores oficiais de PIB de 2022 e 2023 foram divulgados em 2025, de modo que o experimento é retrospectivo. A defasagem dos demais indicadores reduz o risco de usar dados publicados após o corte, mas a base atual não arquiva as versões disponíveis em cada data.

Na previsão de 2023, o modelo obteve R² de 0,9955 e MAPE de 17,94%. O R² resume o ajuste em relação à dispersão dos valores oficiais e é influenciado pela diferença de escala entre as economias municipais. O MAPE atribui o mesmo peso a cada município e mostra que, em média, a previsão se desviou 17,94% do PIB observado em valor absoluto. O uso exclusivo do PIB defasado limita a capacidade do modelo de captar mudanças econômicas específicas de um município.
