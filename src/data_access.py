"""Camada de acesso para o frontend/banco/cloud. Troque a implementação aqui (CSV -> SQL/S3)
sem mexer nas páginas do dashboard."""
import pandas as pd
from pathlib import Path
from . import config as C


def _load_csv(name: str) -> pd.DataFrame:
    path = C.PROCESSED / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def gap_salarial() -> pd.DataFrame:
    return _load_csv("agg_gap_salarial.csv")


def funil_lideranca() -> pd.DataFrame:
    return _load_csv("agg_funil_lideranca.csv")


def perfil_mensal() -> pd.DataFrame:
    return _load_csv("agg_perfil_mensal.csv")


def movimentacoes() -> pd.DataFrame:
    """Base completa (pesada). Use só em notebooks/ETL, não no app."""
    path = C.PROCESSED / "movimentacoes"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)