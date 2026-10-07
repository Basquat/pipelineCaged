from typing import Generator
import pandas as pd
from src.data_access import (
    gap_salarial as ds_gap,
    funil_lideranca as ds_funil,
    perfil_mensal as ds_perfil,
)


def get_gap_salarial() -> pd.DataFrame:
    return ds_gap()


def get_funil_lideranca() -> pd.DataFrame:
    return ds_funil()


def get_perfil_mensal() -> pd.DataFrame:
    return ds_perfil()