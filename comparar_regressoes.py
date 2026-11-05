"""Compara regressões lineares com cortes por ano de referência."""

import csv
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
INDICATORS = ("producao_agricola_mil_reais", "rebanho_bovino_cabecas", "populacao_estimada")


def features(previous_gdp, earlier):
    # A população e os indicadores econômicos têm escalas diferentes.
    # O indicador de ausência distingue lacunas dos valores iguais a zero.
    result = [1, previous_gdp]
    for column in INDICATORS:
        value = earlier.get(column, "")
        result.extend([np.log1p(float(value)) if value else 0, int(not value)])
    return result


def evaluate(actual, predictions):
    errors = actual - predictions
    return (
        1 - np.sum(errors**2) / np.sum((actual - actual.mean())**2),
        100 * np.mean(np.abs(errors / actual)),
    )


def main():
    source = ROOT / "data/raw/base_integrada_sidra.csv"
    with source.open(encoding="utf-8") as file:
        rows = {(row["codigo_municipio"], int(row["ano"])): row for row in csv.DictReader(file)}

    def gdp(row):
        return float(row["pib_mil_reais"])

    examples = [
        (year, features(gdp(rows[code, year - 1]), rows.get((code, year - 2), {})), gdp(row))
        for (code, year), row in rows.items()
        if (code, year - 1) in rows
    ]
    years, design, target = map(np.asarray, zip(*examples))
    scores = {}
    for name, columns in (("PIB anterior", 2), ("PIB e indicadores", design.shape[1])):
        train = years <= 2022
        test = years == 2023
        coefficients = np.linalg.lstsq(design[train, :columns], target[train], rcond=None)[0]
        r2, mape = evaluate(target[test], design[test, :columns] @ coefficients)
        print(f"{name}: R²={r2:.6f}, MAPE={mape:.4f}%")
        scores[columns] = mape

    columns = min(scores, key=scores.get)
    coefficients = np.linalg.lstsq(design[:, :columns], target, rcond=None)[0]
    predictions = [
        (code, 2024, round(float(np.asarray(features(gdp(row), rows.get((code, 2022), {})))[:columns]
                                 @ coefficients), 3))
        for (code, year), row in sorted(rows.items()) if year == 2023
    ]
    assert len(predictions) == 1668
    assert all(np.isfinite(value) and value > 0 for _, _, value in predictions)
    with (ROOT / "outputs/regressao_linear_2024_selecionada.csv").open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["codigo_municipio", "ano", "pib_previsto_mil_reais"])
        writer.writerows(predictions)
    print(f"Modelo selecionado pelo MAPE: {'PIB anterior' if columns == 2 else 'PIB e indicadores'}")


if __name__ == "__main__":
    main()
