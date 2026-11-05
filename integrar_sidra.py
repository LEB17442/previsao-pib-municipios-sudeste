"""Integra indicadores municipais do SIDRA à base inicial de PIB."""

import csv
import json
from collections import Counter
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "pam": (5457, 215, "/c782/0", "producao_agricola_mil_reais"),
    "ppm": (3939, 105, "/c79/2670", "rebanho_bovino_cabecas"),
    "pop": (6579, 9324, "", "populacao_estimada"),
}


def load_indicator(source, table, variable, category):
    values = {}
    for state in (31, 32, 33, 35):
        cache = ROOT / "data" / "sidra" / f"{source}-{state}.json"
        if cache.exists():
            records = json.loads(cache.read_text(encoding="utf-8"))
        else:
            url = (
                f"https://apisidra.ibge.gov.br/values/t/{table}/n6/in%20n3%20{state}"
                f"/v/{variable}/p/2010-2023{category}/h/n"
            )
            with urlopen(url, timeout=120) as response:
                records = json.load(response)
        for record in records:
            key = record["D1C"], record["D3C"]
            if key in values:
                raise ValueError(f"Chave duplicada em {source}: {key}")
            value = record["V"]
            # O SIDRA usa hífen para zero e símbolos distintos para dados ausentes.
            values[key] = "0" if value == "-" else "" if value in {"...", "..", "X"} else value
    return values


def main():
    indicators = {
        column: load_indicator(source, table, variable, category)
        for source, (table, variable, category, column) in SOURCES.items()
    }
    raw = ROOT / "data" / "raw"
    with (raw / "base_integrada.csv").open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        fields = [*reader.fieldnames, *indicators]
        rows = list(reader)

    coverage = Counter()
    keys = set()
    for row in rows:
        key = row["codigo_municipio"], row["ano"]
        if key in keys:
            raise ValueError(f"Chave duplicada na base de PIB: {key}")
        keys.add(key)
        for column, values in indicators.items():
            row[column] = values.get(key, "")
            if row[column] != "":
                float(row[column])
                coverage[row["ano"], column] += 1

    output = raw / "base_integrada_sidra.csv"
    with output.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} registros e {len({code for code, _ in keys})} municípios")
    print("Ano,", ",".join(indicators))
    for year in sorted({year for _, year in keys}):
        print(year, *(coverage[year, column] for column in indicators), sep=",")


if __name__ == "__main__":
    main()
