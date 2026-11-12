"""Pré-processamento da base do PIB municipal do Sudeste (responsável: Peter).

Gera `data/processed/base_modelagem.csv`: uma linha por município e ano-alvo
(2011 a 2024). Todas as variáveis explicativas de um ano-alvo t usam apenas
informação de anos <= t-1, de modo que nenhuma linha carrega dado futuro.

Uso na raiz do projeto:
    .venv/Scripts/python.exe preprocessamento.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent
ENTRADA = ROOT / "data/raw/base_integrada_sidra.csv"
SAIDA = ROOT / "data/processed/base_modelagem.csv"

ANO_PREVISAO = 2024
SETORES = ("agro", "industria", "servicos")
UFS = ("ES", "MG", "RJ", "SP")

# Variáveis numéricas explicativas publicadas na base tratada.
FEATURES_NUMERICAS = [
    "log_pib_lag1",
    "log_pib_lag2",
    "cresc_pib_lag1",
    "cresc_pib_lag2",
    "cresc_pib_mediana_uf_lag1",
    "part_agro_ult",
    "part_industria_ult",
    "part_servicos_ult",
    "defasagem_vab",
    "log_populacao_ult",
    "defasagem_populacao",
    "log_pib_per_capita_lag1",
    "log_producao_agricola_lag1",
    "cresc_producao_agricola_lag1",
    "log_rebanho_bovino_lag1",
    "sem_producao_agricola_lag1",
    "sem_rebanho_bovino_lag1",
]
FEATURES_CATEGORICAS = ["uf"]


def carregar_bruto(caminho=ENTRADA):
    """Lê a base integrada de Lulu com tipos explícitos."""
    df = pd.read_csv(caminho, dtype={"codigo_municipio": "int64", "uf": "string"}, encoding="utf-8")
    return df.sort_values(["codigo_municipio", "ano"]).reset_index(drop=True)


def auditar(df):
    """Checagens de qualidade usadas na EDA; devolve um dicionário de contagens."""
    chave = ["codigo_municipio", "ano"]
    anos = sorted(df["ano"].unique())
    por_municipio = df.groupby("codigo_municipio")["ano"].nunique()
    vab = df[[f"vab_{s}_mil_reais" for s in SETORES]]
    return {
        "linhas": len(df),
        "municipios": df["codigo_municipio"].nunique(),
        "municipios_por_uf": df.groupby("uf")["codigo_municipio"].nunique().to_dict(),
        "anos": f"{anos[0]}-{anos[-1]}",
        "duplicatas_chave": int(df.duplicated(chave).sum()),
        "municipios_com_serie_incompleta": int((por_municipio < len(anos)).sum()),
        "pib_nao_positivo": int((df["pib_mil_reais"] <= 0).sum()),
        "vab_negativo": int((vab < 0).any(axis=1).sum()),
        "vab_soma_maior_que_pib": int((vab.sum(axis=1) > df["pib_mil_reais"] * 1.0001).sum()),
        "codigos_fora_do_sudeste": int((~df["codigo_municipio"].astype(str).str[:2].isin(["31", "32", "33", "35"])).sum()),
    }


def _ultimo_valor_passado(df, coluna):
    """Último valor observado em anos <= t-1 e quantos anos ele tem de defasagem.

    O deslocamento de um ano antes do preenchimento garante que o ano-alvo t
    nunca enxergue o próprio valor nem valores posteriores.
    """
    grupo = df.groupby("codigo_municipio")
    anterior = grupo[coluna].shift(1)
    ano_obs = df["ano"].where(df[coluna].notna())
    ano_obs_anterior = ano_obs.groupby(df["codigo_municipio"]).shift(1)
    valor = anterior.groupby(df["codigo_municipio"]).ffill()
    ano_ult = ano_obs_anterior.groupby(df["codigo_municipio"]).ffill()
    return valor, df["ano"] - ano_ult


def construir_base(df):
    """Monta a base de modelagem com uma linha por município e ano-alvo."""
    # Linha vazia do ano seguinte ao último observado (2024) para receber as defasagens.
    ano_previsao = int(df["ano"].max()) + 1
    ultimo = df[df["ano"] == ano_previsao - 1][["codigo_municipio", "municipio", "uf"]].copy()
    ultimo["ano"] = ano_previsao
    df = pd.concat([df, ultimo], ignore_index=True).sort_values(["codigo_municipio", "ano"])
    df = df.reset_index(drop=True)
    g = df.groupby("codigo_municipio")

    pib = df["pib_mil_reais"]
    log_pib = np.log(pib)
    out = df[["codigo_municipio", "municipio", "uf", "ano", "pib_mil_reais"]].copy()
    out["pib_lag1_mil_reais"] = g["pib_mil_reais"].shift(1)
    out["log_pib_lag1"] = log_pib.groupby(df["codigo_municipio"]).shift(1)
    out["log_pib_lag2"] = log_pib.groupby(df["codigo_municipio"]).shift(2)
    out["log_pib_lag3"] = log_pib.groupby(df["codigo_municipio"]).shift(3)
    out["cresc_pib_lag1"] = out["log_pib_lag1"] - out["log_pib_lag2"]
    out["cresc_pib_lag2"] = out["log_pib_lag2"] - out["log_pib_lag3"]
    # Mediana estadual do crescimento em t-1: choque macro conhecido no ano anterior.
    out["cresc_pib_mediana_uf_lag1"] = out.groupby(["uf", "ano"])["cresc_pib_lag1"].transform("median")

    # Estrutura setorial: última participação conhecida (2022 e 2023 não têm VAB).
    for setor in SETORES:
        part = df[f"vab_{setor}_mil_reais"] / pib
        df[f"_part_{setor}"] = part
        out[f"part_{setor}_ult"], defasagem = _ultimo_valor_passado(df, f"_part_{setor}")
    out["defasagem_vab"] = defasagem

    # População: estimativas só existem de 2011 a 2021.
    df["_log_pop"] = np.log(df["populacao_estimada"])
    out["log_populacao_ult"], out["defasagem_populacao"] = _ultimo_valor_passado(df, "_log_pop")
    out["log_pib_per_capita_lag1"] = out["log_pib_lag1"] - out["log_populacao_ult"]

    # Indicadores agropecuários do ano anterior; ausência vira indicador binário.
    agri = np.log1p(df["producao_agricola_mil_reais"])
    rebanho = np.log1p(df["rebanho_bovino_cabecas"])
    out["log_producao_agricola_lag1"] = agri.groupby(df["codigo_municipio"]).shift(1)
    out["cresc_producao_agricola_lag1"] = out["log_producao_agricola_lag1"] - agri.groupby(df["codigo_municipio"]).shift(2)
    out["log_rebanho_bovino_lag1"] = rebanho.groupby(df["codigo_municipio"]).shift(1)
    out["sem_producao_agricola_lag1"] = out["log_producao_agricola_lag1"].isna().astype(int)
    out["sem_rebanho_bovino_lag1"] = out["log_rebanho_bovino_lag1"].isna().astype(int)

    # Alvos: nível do PIB (regressão) e variação percentual (base das classes).
    out["variacao_pib_pct"] = 100 * (pib / out["pib_lag1_mil_reais"] - 1)
    out["log_razao_pib"] = log_pib - out["log_pib_lag1"]

    out = out[out["ano"] > df["ano"].min()].drop(columns="log_pib_lag3")
    out["conjunto"] = np.where(out["ano"] == ano_previsao, "previsao", "historico")
    return out.reset_index(drop=True)


def criar_preprocessador(escalonar=False):
    """Pipeline sem vazamento: imputação (e escala, se pedida) ajustadas só no treino.

    Use dentro de um sklearn.Pipeline com o modelo, chamando fit apenas nas
    linhas de treino. Modelos lineares/logísticos devem usar escalonar=True;
    árvores não precisam de escala.
    """
    passos = [("imputacao", SimpleImputer(strategy="median", add_indicator=True))]
    if escalonar:
        passos.append(("escala", StandardScaler()))
    return ColumnTransformer(
        [
            ("num", Pipeline(passos), FEATURES_NUMERICAS),
            ("uf", OneHotEncoder(categories=[list(UFS)], handle_unknown="ignore"), FEATURES_CATEGORICAS),
        ],
        verbose_feature_names_out=False,
    )


def main():
    bruto = carregar_bruto()
    for chave, valor in auditar(bruto).items():
        print(f"{chave}: {valor}")
    base = construir_base(bruto)
    assert base.duplicated(["codigo_municipio", "ano"]).sum() == 0
    assert (base[base["ano"] == ANO_PREVISAO]["codigo_municipio"].nunique()) == 1668
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    base.to_csv(SAIDA, index=False, encoding="utf-8", float_format="%.6f")
    print(f"Base salva em {SAIDA.relative_to(ROOT)}: {base.shape[0]} linhas, {base.shape[1]} colunas")


if __name__ == "__main__":
    main()
