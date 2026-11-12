"""Parte da Amanda: python classificacao_logistica.py."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from preprocessamento import FEATURES_NUMERICAS, FEATURES_CATEGORICAS, criar_preprocessador

ROOT = Path(__file__).resolve().parent
CLASSES = ['forte retração', 'retração', 'estabilidade', 'crescimento moderado', 'forte crescimento']
FEATURES = FEATURES_NUMERICAS + FEATURES_CATEGORICAS


def categorizar(x):
    """x<-5; -5<=x<-1; -1<=x<=1; 1<x<=5; x>5 (em %)."""
    return pd.Series(np.select([x < -5, x < -1, x <= 1, x <= 5, x > 5], CLASSES, default=''), index=x.index).replace('', pd.NA)


def executar():
    base = pd.read_csv(ROOT / 'data/processed/base_modelagem.csv')
    assert not base.duplicated(['codigo_municipio', 'ano']).any()
    base['classe'] = categorizar(base.variacao_pib_pct)
    treino = base[(base.ano <= 2022) & base.classe.notna()]
    teste = base[(base.ano == 2023) & base.classe.notna()]
    futuro = base[base.ano == 2024]
    assert len(treino) and len(teste) and len(futuro)
    assert set(teste.codigo_municipio) == set(futuro.codigo_municipio)
    # Imputação e escala aprendidas apenas no treino. As entradas são defasadas.
    modelo = Pipeline([
        ('preprocessamento', criar_preprocessador(escalonar=True)),
        ('modelo', LogisticRegression(max_iter=2000, class_weight='balanced', random_state=42)),
    ])
    modelo.fit(treino[FEATURES], treino.classe)
    previsto = modelo.predict(teste[FEATURES])
    rel = classification_report(teste.classe, previsto, labels=CLASSES, output_dict=True, zero_division=0)
    metricas = pd.DataFrame([{'ano': 2023, 'classe': c, **rel[c]} for c in CLASSES + ['macro avg', 'weighted avg']])
    matriz = pd.DataFrame(confusion_matrix(teste.classe, previsto, labels=CLASSES), index=CLASSES, columns=CLASSES)
    matriz.index.name = 'classe_real'
    saida = ROOT / 'outputs'
    saida.mkdir(exist_ok=True)
    metricas.to_csv(saida / 'metricas_logistica.csv', index=False)
    matriz.to_csv(saida / 'matriz_confusao_logistica_2023.csv')
    avaliacao = teste[['codigo_municipio', 'municipio', 'uf', 'ano', 'variacao_pib_pct', 'classe']].copy()
    avaliacao['classe_prevista'] = previsto
    avaliacao.to_csv(saida / 'classificacao_logistica_2023.csv', index=False)
    # Reajuste com 2023 somente após finalizar a avaliação.
    historico = base[(base.ano <= 2023) & base.classe.notna()]
    modelo.fit(historico[FEATURES], historico.classe)
    previsoes = futuro[['codigo_municipio', 'municipio', 'uf', 'ano']].copy()
    previsoes['classe_prevista'] = modelo.predict(futuro[FEATURES])
    previsoes.to_csv(saida / 'classificacao_logistica_2024.csv', index=False)
    print(metricas.to_string(index=False))
    print(f'Previsões 2024: {len(previsoes)} municípios')
    return metricas, matriz, previsoes


if __name__ == '__main__':
    executar()
