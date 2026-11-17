"""Parte da Luma: Random Forest Classifier das categorias de crescimento do PIB.

Uso na raiz do projeto:
    python classificacao_rf.py

Protocolo temporal (o mesmo da Regressão Logística, mais uma etapa de validação):
1. Hiperparâmetros: treino com anos-alvo <= 2021 e validação em 2022 (F1 macro).
2. Teste: reajuste com anos-alvo <= 2022 e avaliação em 2023 (F1 e matriz de confusão).
3. Entrega: reajuste com anos-alvo <= 2023 e previsão das classes de 2024.

As classes e a regra de limites são importadas de `classificacao_logistica.py`
para garantir que os dois classificadores usem exatamente o mesmo alvo.
"""
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.pipeline import Pipeline

from classificacao_logistica import CLASSES, categorizar
from preprocessamento import FEATURES_CATEGORICAS, FEATURES_NUMERICAS, criar_preprocessador

ROOT = Path(__file__).resolve().parent
SAIDA = ROOT / 'outputs'
FEATURES = FEATURES_NUMERICAS + FEATURES_CATEGORICAS
SEED = 42
N_ARVORES = 500
# Grade pequena e fixada antes de olhar 2023; a escolha usa apenas a validação em 2022.
GRADE = [
    {'max_features': max_features, 'min_samples_leaf': min_samples_leaf}
    for max_features in ('sqrt', 0.5)
    for min_samples_leaf in (1, 5, 20, 50)
]


def criar_modelo(max_features='sqrt', min_samples_leaf=1):
    """Pipeline sem vazamento: a imputação é ajustada apenas nas linhas de treino.

    Árvores não precisam de padronização. `balanced_subsample` recalcula os pesos
    das classes em cada amostra bootstrap, compensando o domínio de forte crescimento.
    """
    return Pipeline([
        ('preprocessamento', criar_preprocessador(escalonar=False)),
        ('modelo', RandomForestClassifier(
            n_estimators=N_ARVORES,
            max_features=max_features,
            min_samples_leaf=min_samples_leaf,
            class_weight='balanced_subsample',
            random_state=SEED,
            n_jobs=-1,
        )),
    ])


def carregar_base():
    base = pd.read_csv(ROOT / 'data/processed/base_modelagem.csv')
    assert not base.duplicated(['codigo_municipio', 'ano']).any()
    base['classe'] = categorizar(base.variacao_pib_pct)
    return base


def escolher_hiperparametros(base):
    """Treina até 2021 e valida em 2022. Devolve a grade ordenada pelo F1 macro."""
    treino = base[(base.ano <= 2021) & base.classe.notna()]
    valid = base[(base.ano == 2022) & base.classe.notna()]
    linhas = []
    for params in GRADE:
        modelo = criar_modelo(**params).fit(treino[FEATURES], treino.classe)
        previsto = modelo.predict(valid[FEATURES])
        linhas.append({
            **params,
            'f1_macro_2022': f1_score(valid.classe, previsto, labels=CLASSES, average='macro', zero_division=0),
            'f1_ponderado_2022': f1_score(valid.classe, previsto, labels=CLASSES, average='weighted', zero_division=0),
        })
    # Ordenação estável: em empate, prevalece a ordem da grade (modelo mais simples primeiro).
    return pd.DataFrame(linhas).sort_values('f1_macro_2022', ascending=False, kind='stable').reset_index(drop=True)


def executar():
    base = carregar_base()
    treino = base[(base.ano <= 2022) & base.classe.notna()]
    teste = base[(base.ano == 2023) & base.classe.notna()]
    futuro = base[base.ano == 2024]
    assert len(treino) and len(teste) and len(futuro)
    assert set(teste.codigo_municipio) == set(futuro.codigo_municipio)

    grade = escolher_hiperparametros(base)
    melhor = grade.iloc[0]
    params = {
        'max_features': melhor.max_features if melhor.max_features == 'sqrt' else float(melhor.max_features),
        'min_samples_leaf': int(melhor.min_samples_leaf),
    }

    # Teste em 2023 com treino até 2022.
    modelo = criar_modelo(**params).fit(treino[FEATURES], treino.classe)
    previsto = modelo.predict(teste[FEATURES])
    rel = classification_report(teste.classe, previsto, labels=CLASSES, output_dict=True, zero_division=0)
    metricas = pd.DataFrame([{'ano': 2023, 'classe': c, **rel[c]} for c in CLASSES + ['macro avg', 'weighted avg']])
    matriz = pd.DataFrame(confusion_matrix(teste.classe, previsto, labels=CLASSES), index=CLASSES, columns=CLASSES)
    matriz.index.name = 'classe_real'
    importancias = pd.Series(
        modelo.named_steps['modelo'].feature_importances_,
        index=modelo.named_steps['preprocessamento'].get_feature_names_out(),
    ).sort_values(ascending=False)

    SAIDA.mkdir(exist_ok=True)
    grade.to_csv(SAIDA / 'validacao_rf_classificacao_2022.csv', index=False)
    metricas.to_csv(SAIDA / 'metricas_rf_classificacao.csv', index=False)
    matriz.to_csv(SAIDA / 'matriz_confusao_rf_2023.csv')
    avaliacao = teste[['codigo_municipio', 'municipio', 'uf', 'ano', 'variacao_pib_pct', 'classe']].copy()
    avaliacao['classe_prevista'] = previsto
    avaliacao.to_csv(SAIDA / 'classificacao_rf_2023.csv', index=False)

    # Reajuste com 2023 somente após finalizar a avaliação.
    historico = base[(base.ano <= 2023) & base.classe.notna()]
    modelo_final = criar_modelo(**params).fit(historico[FEATURES], historico.classe)
    previsoes = futuro[['codigo_municipio', 'municipio', 'uf', 'ano']].copy()
    previsoes['classe_prevista'] = modelo_final.predict(futuro[FEATURES])
    assert len(previsoes) == 1668 and previsoes.codigo_municipio.is_unique
    previsoes.to_csv(SAIDA / 'classificacao_rf_2024.csv', index=False)

    print('Validação 2022 (treino <= 2021):')
    print(grade.round(4).to_string(index=False))
    print(f'\nHiperparâmetros escolhidos: {params}\n')
    print(metricas.to_string(index=False))
    print(f'Previsões 2024: {len(previsoes)} municípios')
    return {
        'grade': grade, 'params': params, 'metricas': metricas, 'matriz': matriz,
        'importancias': importancias, 'previsoes': previsoes,
    }


if __name__ == '__main__':
    executar()
