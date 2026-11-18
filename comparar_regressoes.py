"""Compara regressões lineares usando a base tratada e cortes temporais."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from preprocessamento import FEATURES_CATEGORICAS, FEATURES_NUMERICAS, criar_preprocessador

ROOT = Path(__file__).resolve().parent
FEATURES = FEATURES_NUMERICAS + FEATURES_CATEGORICAS + ["pib_lag1_mil_reais"]


def main():
    base = pd.read_csv(ROOT / "data/processed/base_modelagem.csv")
    assert not base.duplicated(["codigo_municipio", "ano"]).any()
    historico = base[base.pib_mil_reais.notna()]
    treino = historico[historico.ano <= 2022]
    teste = historico[historico.ano == 2023].sort_values("codigo_municipio")
    futuro = base[base.ano == 2024].sort_values("codigo_municipio")
    assert len(teste) == len(futuro) == 1668
    assert set(teste.codigo_municipio) == set(futuro.codigo_municipio)

    # O PIB anterior em nível permite estimar diretamente o nível do PIB.
    # As demais entradas e sua imputação são compartilhadas com o grupo.
    preprocessador = criar_preprocessador(escalonar=True)
    preprocessador.transformers.append(("pib_nivel", StandardScaler(), ["pib_lag1_mil_reais"]))
    modelos = {
        "PIB anterior": LinearRegression(),
        "PIB e indicadores": Pipeline([
            ("preprocessamento", preprocessador),
            ("modelo", LinearRegression()),
        ]),
    }
    entradas = {"PIB anterior": ["pib_lag1_mil_reais"], "PIB e indicadores": FEATURES}
    metricas = []
    for nome, modelo in modelos.items():
        modelo.fit(treino[entradas[nome]], treino.pib_mil_reais)
        previsto = modelo.predict(teste[entradas[nome]])
        metricas.append({
            "modelo": nome,
            "R2": r2_score(teste.pib_mil_reais, previsto),
            "MAPE_%": 100 * mean_absolute_percentage_error(teste.pib_mil_reais, previsto),
        })

    metricas = pd.DataFrame(metricas)
    escolhido = metricas.loc[metricas["MAPE_%"].idxmin(), "modelo"]
    metricas["selecionado"] = metricas.modelo == escolhido
    output = ROOT / "outputs"
    output.mkdir(exist_ok=True)
    metricas.to_csv(output / "metricas_regressao_linear.csv", index=False, float_format="%.9f")
    print(metricas.to_string(index=False))

    modelo = modelos[escolhido]
    modelo.fit(historico[entradas[escolhido]], historico.pib_mil_reais)
    previsto = modelo.predict(futuro[entradas[escolhido]])
    assert np.isfinite(previsto).all() and (previsto > 0).all()
    resultado = futuro[["codigo_municipio", "ano"]].copy()
    resultado["pib_previsto_mil_reais"] = previsto
    resultado.to_csv(output / "regressao_linear_2024_selecionada.csv", index=False, float_format="%.3f")


if __name__ == "__main__":
    main()
