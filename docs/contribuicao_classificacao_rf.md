# Random Forest Classifier e consolidação — Luma

## Método

O Random Forest Classifier usa as mesmas cinco classes, os limites e as entradas da Regressão Logística. A base tratada fornece 17 variáveis numéricas defasadas e a UF. A imputação pela mediana com indicadores de ausência e a codificação da UF são ajustadas apenas no treino.

A floresta tem 500 árvores, semente 42 e pesos balanced_subsample. A grade testa max_features em {sqrt, 0.5} e min_samples_leaf em {1, 5, 20, 50}, com treino até 2021 e validação em 2022 por F1 macro. Na reexecução final, a configuração selecionada foi sqrt e 50 observações por folha, com F1 macro de 0,2650 em 2022.

Com essa configuração, o modelo é reajustado até 2022 para avaliar 2023 e até 2023 para prever 2024.

## Resultados de 2023

O Random Forest obteve F1 macro de 0,2341, F1 ponderado de 0,6464 e acurácia de 0,6187. O F1 por classe foi 0,3473 em forte retração, 0,0410 em retração, zero em estabilidade e crescimento moderado, e 0,7820 em forte crescimento. Acertou 936 dos 1.327 casos de forte crescimento e 91 dos 109 de forte retração, com precisão de 0,219 nesta última classe.

| Modelo | F1 macro | F1 ponderado | Acurácia |
| --- | --- | --- | --- |
| Regressão Logística | **0,2434** | 0,6008 | 0,5378 |
| Random Forest Classifier | 0,2341 | 0,6464 | 0,6187 |
| Referência, sempre forte crescimento | 0,1772 | 0,7050 | 0,7956 |

A regra do maior F1 macro escolhe a Regressão Logística para as classes da entrega final. O Random Forest supera a logística nas métricas ponderadas pela frequência das classes, mas tem menor F1 macro. Ambos têm dificuldade com as classes intermediárias.

## Consolidação de 2024

O script consolidar_previsoes.py lê os resultados de todos os integrantes e escolhe a regressão pelo menor MAPE e a classificação pelo maior F1 macro em 2023. A entrega usa o Random Forest Regressor, com MAPE de 9,00%, e a Regressão Logística. A regressão linear selecionada obteve MAPE de 17,94%.

O arquivo final contém os 1.668 municípios, PIB previsto, variação, classe e resultados alternativos de cada modelo. O PIB regional previsto é de R$ 6,32 trilhões, frente a R$ 5,80 trilhões em 2023. A classificação selecionada prevê forte crescimento em 1.626 municípios e forte retração em 42. Não prevê as três classes intermediárias para 2024.

## Limitações e reprodução

A classe escolhida coincide com a classe implícita no PIB previsto em 95,0% dos municípios. A divergência decorre de tarefas e modelos separados. As previsões precisam ser avaliadas contra os valores oficiais do ano-alvo para determinar os erros. O PIB é nominal e a avaliação é retrospectiva por ano de referência.

A reexecução completa alterou a configuração selecionada em 2022 e os resultados anteriormente publicados do Random Forest Classifier. As outras etapas reproduziram seus CSVs. Não há registro completo do ambiente original para determinar a causa exata da diferença. Os resultados desta entrega foram gerados com Python 3.12.14 e as versões fixadas em requirements.txt.

Na raiz, execute python classificacao_rf.py e python consolidar_previsoes.py, ou todas as células de notebooks/06_classificacao_rf.ipynb.
