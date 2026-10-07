"""Testa limpeza + agregação sem precisar de 7z/parquet (lógica pura em pandas)."""
import pandas as pd
import numpy as np
from src import clean, aggregate, config as C


def _txt(tmp_path, n=5000):
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "competênciamov": "202401", "uf": rng.choice(list(C.UF), n),
        "seção": "G", "saldomovimentação": rng.choice([1, -1], n),
        "cbo2002ocupação": rng.choice(["142105", "211110", "513205", "782510", "41010"], n),
        "graudeinstrução": 7, "idade": rng.integers(18, 65, n), "horascontratuais": "44,00",
        "raçacor": rng.choice(["1", "2", "3", "4", "6", "9"], n),
        "sexo": rng.choice(["1", "3", "9"], n, p=[.55, .44, .01]),
        "tipomovimentação": "10",
        "salário": [f"{x:.2f}".replace(".", ",") for x in rng.lognormal(7.5, .6, n)],
        "tamestabjan": "5", "indicadordeforadoprazo": "0", "município": "292740"})
    p = tmp_path / "x.txt"
    df.to_csv(p, sep=";", index=False, encoding="latin-1")
    return p


def test_limpeza_e_agregacao(tmp_path):
    txt = _txt(tmp_path)
    df = pd.concat([clean.limpar(c) for c in clean.ler_txt(txt, chunksize=1000)])
    assert set(df["sexo"]) <= {"Homem", "Mulher"}
    assert df["salario"].dropna().min() >= 100
    assert df.loc[df.cbo_grande_grupo == "1", "lideranca"].all()
    assert df["cbo"].str.len().eq(6).all()          # '41010' -> '041010'
    g = aggregate.gap_salarial(df)
    assert {"salario_medio", "n"} <= set(g.columns)
    f = aggregate.funil_lideranca(df)
    soma = f.groupby(["ano", "uf", "sexo", "raca_cor_agrupada"])["pct_no_grupo_demografico"].sum()
    assert (soma.round(0) == 100).all()
