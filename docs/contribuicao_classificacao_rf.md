# Random Forest Classifier e consolidação — Luma

## Método

O Random Forest Classifier usa as mesmas cinco classes, a mesma regra de limites e as mesmas entradas da Regressão Logística: as 17 variáveis numéricas defasadas da base do Peter e a UF. As classes são importadas de `classificacao_logistica.py`, o que garante alvo idêntico nos dois classificadores. O pipeline imputa ausências pela mediana com indicadores de ausência e codifica a UF; a imputação é ajustada apenas nas linhas de treino. Árvores não precisam de padronização.

A floresta tem 500 árvores e `class_weight='balanced_subsample'`, que recalcula os pesos das classes em cada amostra bootstrap. Sem essa ponderação, o modelo tende a prever apenas *forte crescimento*. Dois hiperparâmetros foram escolhidos em uma grade pequena (`max_features` em {√p, 0,5} e `min_samples_leaf` em {1, 5, 20, 50}), treinando com anos-alvo até 2021 e validando em 2022 pelo F1 macro. A configuração escolhida foi `max_features='sqrt'` e `min_samples_leaf=5` (F1 macro de 0,2690 em 2022). Folhas com um único exemplo memorizam a classe majoritária e tiveram o pior F1 macro (0,19).

Com os hiperparâmetros fixados, o modelo foi treinado com anos-alvo até 2022 e avaliado em 2023. Depois da avaliação, foi reajustado até 2023 para prever 2024.

## Resultados de 2023

Nos 1.668 municípios, o F1 macro foi **0,2561** e o F1 ponderado **0,7058**, com acurácia de 0,731. O F1 por classe foi 0,4098 (forte retração), 0,0182 (retração), 0 (estabilidade), 0 (crescimento moderado) e 0,8527 (forte crescimento). O modelo acertou 1.143 dos 1.327 casos de forte crescimento e 75 dos 109 de forte retração, mas praticamente não prevê as classes intermediárias: 1 acerto em retração e nenhum em estabilidade ou crescimento moderado.

Entre as variáveis, o crescimento do PIB em t−1 tem a maior importância por impureza, seguido das participações setoriais, do PIB per capita e dos indicadores agropecuários.

## Comparação e classificador final

A regra de seleção, definida antes da comparação, foi o maior F1 macro em 2023, métrica principal por dar o mesmo peso às cinco classes. As métricas foram recalculadas a partir das previsões por município dos dois modelos, verificando que ambos foram avaliados nos mesmos municípios e rótulos.

| Modelo | F1 macro | F1 ponderado | Acurácia |
| --- | --- | --- | --- |
| Random Forest Classifier | **0,2561** | **0,7058** | 0,7308 |
| Regressão Logística | 0,2434 | 0,6008 | 0,5378 |
| Referência: sempre forte crescimento | 0,1772 | 0,7050 | 0,7956 |

**O Random Forest Classifier é o classificador do resultado final.** Ele supera a logística no F1 macro, no F1 ponderado e na acurácia, e tem F1 maior nas duas classes extremas. A vantagem é modesta: no F1 ponderado ele apenas empata com a referência ingênua, cuja acurácia é maior, e o ganho em F1 macro vem quase todo de forte retração. A logística é melhor nas três classes intermediárias, embora com F1 abaixo de 0,13 em todas. Nenhum dos dois modelos separa bem as variações próximas de zero.

## Consolidação de 2024

`consolidar_previsoes.py` lê os CSVs de cada integrante, sem reajustar modelos, e gera `outputs/previsoes_finais_2024.csv`. Para o PIB, a regra foi o menor MAPE em 2023: o Random Forest Regressor do Peter (MAPE 9,00%, R² 0,9985) supera a regressão linear da Lulu (13,21%, R² 0,9955) e a referência PIB₂₀₂₃ = PIB₂₀₂₂ (13,47%). O arquivo tem uma linha para cada um dos 1.668 municípios com o PIB previsto, a variação prevista, a classe prevista e, para auditoria, as previsões alternativas de cada modelo e a classe implícita na variação do PIB previsto.

O PIB total previsto do Sudeste em 2024 é de R$ 6,32 trilhões, contra R$ 5,80 trilhões oficiais em 2023 (+9,0%). O classificador põe 1.477 municípios em forte crescimento, 178 em forte retração, 9 em crescimento moderado, 3 em retração e 1 em estabilidade.

## Limitações

A classe prevista coincide com a classe implícita no PIB previsto em 89% dos municípios. A maior divergência são os 178 municípios em forte retração: o regressor prevê queda acima de 5% para apenas 9 municípios. Os pesos balanceados fazem o classificador superestimar a classe rara (precisão de 0,29 em 2023). PIB e classe são alvos de modelos diferentes; o CSV final mantém ambos para que a divergência seja visível. O PIB é nominal, e o experimento é retrospectivo por ano de referência, como nas demais seções.

## Execução

Na raiz: `python classificacao_rf.py` e depois `python consolidar_previsoes.py`, ou executar todas as células de `notebooks/06_classificacao_rf.ipynb`.
