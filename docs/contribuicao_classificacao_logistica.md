# Classificação por Regressão Logística — Amanda

## Critérios e método

O alvo é a variação percentual nominal do PIB frente ao ano anterior: `100 * (PIB_t / PIB_t-1 - 1)`. As classes são forte retração (< -5%), retração (-5% inclusive até -1% exclusive), estabilidade (-1% a 1% inclusive), crescimento moderado (> 1% até 5% inclusive) e forte crescimento (> 5%). Essa convenção elimina sobreposição nos limites.

A Regressão Logística multiclasse usa as 17 variáveis numéricas defasadas e a UF da base de Peter. Não usa PIB, variação ou classe do próprio ano como entrada. O pipeline aplica imputação pela mediana, indicadores de ausência, padronização e codificação da UF; todos os ajustes são feitos apenas no treino. Os pesos das classes são balanceados, com regularização padrão e sem busca de hiperparâmetros no teste.

O treinamento inicial usa anos-alvo até 2022; a avaliação usa apenas 2023. Após essa avaliação, o pipeline é reajustado até 2023 para prever 2024. O notebook e o script executam o mesmo código e salvam as métricas, a matriz de confusão e as previsões.

## Resultados de 2023

Foram avaliados 1.668 municípios. O F1 macro foi **0,2434** e o F1 ponderado **0,6008**. A diferença revela a influência da classe majoritária: 1.327 municípios tiveram forte crescimento. O F1 por classe foi 0,3043 (forte retração), 0,0517 (retração), 0,0177 (estabilidade), 0,1282 (crescimento moderado) e 0,7151 (forte crescimento).

A classe forte crescimento apresentou o melhor F1: 793 acertos entre 1.327 casos reais. O modelo identificou 82 dos 109 casos de forte retração, mas também previu retração forte em muitos municípios de outras classes. Os acertos foram apenas 6 em retração, 1 em estabilidade e 15 em crescimento moderado. Os pesos balanceados aumentam a atenção às classes raras, mas não resolvem sua baixa separação. A matriz completa está em `outputs/matriz_confusao_logistica_2023.csv`.

Como referência simples, prever sempre forte crescimento teria F1 macro de aproximadamente 0,1772 e F1 ponderado de 0,7050. Assim, a logística melhora o equilíbrio entre classes medido pelo F1 macro, mas perde no F1 ponderado. Seu desempenho nas classes intermediárias é limitado.

## Previsões e limitações

O arquivo `outputs/classificacao_logistica_2024.csv` contém uma categoria prevista para cada um dos 1.668 municípios. Essas categorias não são valores observados nem uma estimativa direta do PIB.

O modelo tem fronteiras lineares, usa uma única estrutura para municípios diferentes e depende de indicadores históricos. Choques econômicos locais e mudanças na distribuição entre anos prejudicam a previsão. As classes intermediárias têm poucos exemplos, e pequenas alterações perto dos limites podem mudar o rótulo. O PIB é nominal, portanto crescimento não equivale a expansão real descontada a inflação.

O experimento respeita cortes por ano de referência, mas é retrospectivo: não reproduz as versões dos dados publicadas em cada data. A comparação futura com Random Forest Classifier deve usar os mesmos municípios, classes e divisão temporal, priorizando F1 macro e inspecionando as cinco classes. Ainda não há resultado desse classificador para comparar no repositório.

## Execução

Na raiz, com as dependências de `requirements.txt` instaladas: `python classificacao_logistica.py`. Alternativamente, executar todas as células de `notebooks/05_classificacao_logistica.ipynb`.
