"""Consolidação das previsões de 2024 (responsável: Luma).

Uso na raiz do projeto, depois de gerar os resultados de cada modelo:
    python consolidar_previsoes.py

Não reajusta nenhum modelo: apenas lê os CSVs publicados por cada integrante,
compara os modelos pelas métricas de 2023 e monta `outputs/previsoes_finais_2024.csv`.

Regras de seleção (definidas antes de comparar os resultados):
- Regressão: menor MAPE em 2023 (o MAPE dá o mesmo peso a cada município;
  o R² fica acima de 0,99 em todos os modelos e quase não discrimina).
- Classificação: maior F1 macro em 2023, métrica principal combinada com a Amanda
  por dar o mesmo peso às cinco classes desbalanceadas.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

from classificacao_logistica import CLASSES, categorizar

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
N_MUNICIPIOS = 1668

# A regressão linear (Lulu) não publica CSV de métricas; os valores abaixo são os
# impressos por `comparar_regressoes.py` e registrados em docs/contribuicao_regressao_linear.md.
METRICAS_LINEAR_2023 = {'R2': 0.995463, 'MAPE_%': 13.21}

CLASSIFICADORES = {
    'Regressão Logística': OUT / 'classificacao_logistica_2023.csv',
    'Random Forest Classifier': OUT / 'classificacao_rf_2023.csv',
}
PREVISOES_CLASSE_2024 = {
    'Regressão Logística': OUT / 'classificacao_logistica_2024.csv',
    'Random Forest Classifier': OUT / 'classificacao_rf_2024.csv',
}
PREVISOES_PIB_2024 = {
    'Regressão Linear': OUT / 'regressao_linear_2024_selecionada.csv',
    'Random Forest Regressor': OUT / 'regressao_rf_2024.csv',
}


def _metricas_classificacao(real, previsto):
    f1_classes = f1_score(real, previsto, labels=CLASSES, average=None, zero_division=0)
    return {
        'f1_macro': f1_score(real, previsto, labels=CLASSES, average='macro', zero_division=0),
        'f1_ponderado': f1_score(real, previsto, labels=CLASSES, average='weighted', zero_division=0),
        'acuracia': accuracy_score(real, previsto),
        **{f'f1_{c}': v for c, v in zip(CLASSES, f1_classes)},
    }


def comparar_classificadores():
    """Recalcula as métricas de 2023 a partir das previsões por município de cada modelo."""
    linhas, referencia = [], None
    for nome, caminho in CLASSIFICADORES.items():
        df = pd.read_csv(caminho)
        assert len(df) == N_MUNICIPIOS and df.codigo_municipio.is_unique, caminho
        if referencia is None:
            referencia = df[['codigo_municipio', 'classe']]
        # Os dois modelos precisam ter sido avaliados nos mesmos municípios com os mesmos rótulos reais.
        pd.testing.assert_frame_equal(
            referencia.sort_values('codigo_municipio').reset_index(drop=True),
            df[['codigo_municipio', 'classe']].sort_values('codigo_municipio').reset_index(drop=True),
        )
        linhas.append({'modelo': nome, **_metricas_classificacao(df.classe, df.classe_prevista)})
    # Referência ingênua: prever sempre a classe majoritária do treino.
    linhas.append({'modelo': 'Referência (sempre forte crescimento)',
                   **_metricas_classificacao(referencia.classe, ['forte crescimento'] * len(referencia))})
    return pd.DataFrame(linhas)


def comparar_regressoes():
    rf = pd.read_csv(OUT / 'metricas_rf_regressao.csv').set_index('modelo')
    linhas = [
        {'modelo': 'Regressão Linear', **METRICAS_LINEAR_2023},
        {'modelo': 'Random Forest Regressor', 'R2': rf.loc['Random Forest', 'R2'], 'MAPE_%': rf.loc['Random Forest', 'MAPE_%']},
    ]
    ingenuo = rf.index[rf.index.str.startswith('Ingênuo')][0]
    linhas.append({'modelo': 'Referência (PIB_2023 = PIB_2022)', 'R2': rf.loc[ingenuo, 'R2'], 'MAPE_%': rf.loc[ingenuo, 'MAPE_%']})
    return pd.DataFrame(linhas)


def consolidar():
    comp_cls = comparar_classificadores()
    comp_reg = comparar_regressoes()
    modelos_cls = comp_cls[comp_cls.modelo.isin(CLASSIFICADORES)]
    modelos_reg = comp_reg[comp_reg.modelo.isin(PREVISOES_PIB_2024)]
    cls_escolhido = modelos_cls.loc[modelos_cls.f1_macro.idxmax(), 'modelo']
    reg_escolhido = modelos_reg.loc[modelos_reg['MAPE_%'].idxmin(), 'modelo']

    base = pd.read_csv(ROOT / 'data/processed/base_modelagem.csv')
    final = base.loc[base.ano == 2024, ['codigo_municipio', 'municipio', 'uf', 'ano', 'pib_lag1_mil_reais']]
    final = final.rename(columns={'pib_lag1_mil_reais': 'pib_2023_oficial_mil_reais'})

    colunas_pib = {}
    for nome, caminho in PREVISOES_PIB_2024.items():
        df = pd.read_csv(caminho)
        assert len(df) == N_MUNICIPIOS and df.codigo_municipio.is_unique and (df.ano == 2024).all(), caminho
        col = 'pib_previsto_rf_mil_reais' if 'Random' in nome else 'pib_previsto_linear_mil_reais'
        colunas_pib[nome] = col
        final = final.merge(df[['codigo_municipio', 'pib_previsto_mil_reais']].rename(columns={'pib_previsto_mil_reais': col}),
                            on='codigo_municipio', how='left', validate='one_to_one')
    colunas_cls = {}
    for nome, caminho in PREVISOES_CLASSE_2024.items():
        df = pd.read_csv(caminho)
        assert len(df) == N_MUNICIPIOS and df.codigo_municipio.is_unique, caminho
        col = 'classe_rf' if 'Random' in nome else 'classe_logistica'
        colunas_cls[nome] = col
        final = final.merge(df[['codigo_municipio', 'classe_prevista']].rename(columns={'classe_prevista': col}),
                            on='codigo_municipio', how='left', validate='one_to_one')

    final['pib_previsto_2024_mil_reais'] = final[colunas_pib[reg_escolhido]]
    final['modelo_regressao'] = reg_escolhido
    final['variacao_prevista_pct'] = 100 * (final.pib_previsto_2024_mil_reais / final.pib_2023_oficial_mil_reais - 1)
    final['classe_prevista_2024'] = final[colunas_cls[cls_escolhido]]
    final['modelo_classificacao'] = cls_escolhido
    # Categoria implícita na variação do PIB previsto: serve só para checar coerência entre as duas tarefas.
    final['classe_implicita_regressao'] = categorizar(final.variacao_prevista_pct)

    assert len(final) == N_MUNICIPIOS and final.codigo_municipio.is_unique
    assert final.notna().all().all(), final.columns[final.isna().any()].tolist()
    assert np.isfinite(final.pib_previsto_2024_mil_reais).all() and (final.pib_previsto_2024_mil_reais > 0).all()
    assert final.classe_prevista_2024.isin(CLASSES).all()

    colunas = ['codigo_municipio', 'municipio', 'uf', 'ano', 'pib_2023_oficial_mil_reais',
               'pib_previsto_2024_mil_reais', 'variacao_prevista_pct', 'classe_prevista_2024',
               'modelo_regressao', 'modelo_classificacao', 'pib_previsto_linear_mil_reais',
               'pib_previsto_rf_mil_reais', 'classe_logistica', 'classe_rf', 'classe_implicita_regressao']
    final = final[colunas].sort_values('codigo_municipio').reset_index(drop=True)
    final.to_csv(OUT / 'previsoes_finais_2024.csv', index=False, encoding='utf-8', float_format='%.3f')
    comp_cls.to_csv(OUT / 'comparacao_classificacao_2023.csv', index=False, float_format='%.6f')
    comp_reg.to_csv(OUT / 'comparacao_regressao_2023.csv', index=False, float_format='%.6f')

    concordancia = (final.classe_prevista_2024 == final.classe_implicita_regressao).mean()
    print(comp_reg.round(4).to_string(index=False))
    print(f'Regressão escolhida: {reg_escolhido}\n')
    print(comp_cls[['modelo', 'f1_macro', 'f1_ponderado', 'acuracia']].round(4).to_string(index=False))
    print(f'Classificação escolhida: {cls_escolhido}\n')
    print(f'Concordância classe prevista x classe implícita no PIB previsto: {concordancia:.1%}')
    print(f'previsoes_finais_2024.csv: {len(final)} municípios')
    return {'final': final, 'comparacao_classificacao': comp_cls, 'comparacao_regressao': comp_reg,
            'classificador': cls_escolhido, 'regressor': reg_escolhido, 'concordancia': concordancia}


if __name__ == '__main__':
    consolidar()
