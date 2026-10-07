from fastapi import FastAPI, Depends, Query
from typing import List, Optional
import pandas as pd

from src.api.models import (
    GapSalarialResponse,
    FunilLiderancaResponse,
    PerfilMensalResponse,
    HealthResponse,
)
from src.api.dependencies import (
    get_gap_salarial,
    get_funil_lideranca,
    get_perfil_mensal,
)

app = FastAPI(
    title="Novo CAGED API",
    description="API para dados agregados do Novo CAGED - Gap Salarial e Funil de Liderança",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok")


@app.get("/gap-salarial", response_model=List[GapSalarialResponse])
def gap_salarial(
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    uf: Optional[str] = Query(None, description="Filtrar por UF (ex: SP, RJ)"),
    sexo: Optional[str] = Query(None, description="Filtrar por sexo (Homem, Mulher)"),
    raca: Optional[str] = Query(None, description="Filtrar por raça agrupada"),
    df: pd.DataFrame = Depends(get_gap_salarial),
):
    result = df.copy()
    if ano:
        result = result[result["ano"] == ano]
    if uf:
        result = result[result["uf"] == uf.upper()]
    if sexo:
        result = result[result["sexo"] == sexo]
    if raca:
        result = result[result["raca_cor_agrupada"] == raca]
    return result.to_dict(orient="records")


@app.get("/funil-lideranca", response_model=List[FunilLiderancaResponse])
def funil_lideranca(
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    uf: Optional[str] = Query(None, description="Filtrar por UF"),
    sexo: Optional[str] = Query(None, description="Filtrar por sexo"),
    raca: Optional[str] = Query(None, description="Filtrar por raça agrupada"),
    df: pd.DataFrame = Depends(get_funil_lideranca),
):
    result = df.copy()
    if ano:
        result = result[result["ano"] == ano]
    if uf:
        result = result[result["uf"] == uf.upper()]
    if sexo:
        result = result[result["sexo"] == sexo]
    if raca:
        result = result[result["raca_cor_agrupada"] == raca]
    return result.to_dict(orient="records")


@app.get("/perfil-mensal", response_model=List[PerfilMensalResponse])
def perfil_mensal(
    competencia: Optional[str] = Query(None, description="Filtrar por competência (YYYYMM)"),
    uf: Optional[str] = Query(None, description="Filtrar por UF"),
    sexo: Optional[str] = Query(None, description="Filtrar por sexo"),
    raca: Optional[str] = Query(None, description="Filtrar por raça agrupada"),
    lideranca: Optional[bool] = Query(None, description="Filtrar por liderança"),
    df: pd.DataFrame = Depends(get_perfil_mensal),
):
    result = df.copy()
    if competencia:
        result = result[result["competencia"] == competencia]
    if uf:
        result = result[result["uf"] == uf.upper()]
    if sexo:
        result = result[result["sexo"] == sexo]
    if raca:
        result = result[result["raca_cor_agrupada"] == raca]
    if lideranca is not None:
        result = result[result["lideranca"] == lideranca]
    return result.to_dict(orient="records")