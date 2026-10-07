"""Camada de acesso para o frontend/banco/cloud. Troque a implementação aqui (CSV -> SQL/S3)
sem mexer nas páginas do dashboard."""
import pandas as pd
from . import config as C


def gap_salarial() -> pd.DataFrame:
    return pd.read_csv(C.PROCESSED / "agg_gap_salarial.csv")


def funil_lideranca() -> pd.DataFrame:
    return pd.read_csv(C.PROCESSED / "agg_funil_lideranca.csv")


def perfil_mensal() -> pd.DataFrame:
    return pd.read_csv(C.PROCESSED / "agg_perfil_mensal.csv")


def movimentacoes() -> pd.DataFrame:
    """Base completa (pesada). Use só em notebooks/ETL, não no app."""
    return pd.read_parquet(C.PROCESSED / "movimentacoes")
