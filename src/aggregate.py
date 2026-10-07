"""Gera tabelas agregadas (leves) para o dashboard a partir do parquet limpo.

Uso: python -m src.aggregate
Saídas em data/processed/: agg_gap_salarial.csv, agg_funil_lideranca.csv, agg_perfil_mensal.csv
"""
import pandas as pd
from . import config as C


def carregar(pasta=C.PROCESSED / "movimentacoes") -> pd.DataFrame:
    return pd.read_parquet(pasta)


def gap_salarial(df: pd.DataFrame) -> pd.DataFrame:
    """Salário de ADMISSÃO (único com salário confiável no Novo CAGED) por sexo×raça×grupo."""
    adm = df[(df["saldo"] == 1) & df["salario"].notna()]
    g = adm.groupby(["ano", "uf", "grande_grupo_nome", "sexo", "raca_cor_agrupada"], observed=True)
    out = g["salario"].agg(n="count", salario_medio="mean", salario_mediano="median").reset_index()
    return out.round(2)


def funil_lideranca(df: pd.DataFrame) -> pd.DataFrame:
    """Participação em cada grande grupo CBO (admissões) e % em liderança, por grupo demográfico."""
    adm = df[df["saldo"] == 1]
    g = adm.groupby(["ano", "uf", "sexo", "raca_cor_agrupada", "grande_grupo_nome"], observed=True)
    out = g.size().rename("admissoes").reset_index()
    tot = out.groupby(["ano", "uf", "sexo", "raca_cor_agrupada"])["admissoes"].transform("sum")
    out["pct_no_grupo_demografico"] = (out["admissoes"] / tot * 100).round(3)
    return out


def perfil_mensal(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["competencia", "uf", "sexo", "raca_cor_agrupada", "lideranca"], observed=True)
    return g.agg(saldo=("saldo", "sum"), movs=("saldo", "size")).reset_index()


def main():
    df = carregar()
    gap_salarial(df).to_csv(C.PROCESSED / "agg_gap_salarial.csv", index=False)
    funil_lideranca(df).to_csv(C.PROCESSED / "agg_funil_lideranca.csv", index=False)
    perfil_mensal(df).to_csv(C.PROCESSED / "agg_perfil_mensal.csv", index=False)
    print("[ok] agregados gerados em", C.PROCESSED)


if __name__ == "__main__":
    main()
