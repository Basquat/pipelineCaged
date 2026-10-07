from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import date
from enum import Enum


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class GapSalarialResponse(BaseModel):
    ano: int
    uf: str
    grande_grupo_nome: str
    sexo: str
    raca_cor_agrupada: str
    n: int
    salario_medio: float
    salario_mediano: float


class FunilLiderancaResponse(BaseModel):
    ano: int
    uf: str
    sexo: str
    raca_cor_agrupada: str
    grande_grupo_nome: str
    admissoes: int
    pct_no_grupo_demografico: float


class PerfilMensalResponse(BaseModel):
    competencia: str
    uf: str
    sexo: str
    raca_cor_agrupada: str
    lideranca: bool
    saldo: int
    movs: int


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"


class PaginatedResponse(BaseModel):
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatsResponse(BaseModel):
    count: int
    salario_medio: Optional[float] = None
    salario_mediano: Optional[float] = None
    salario_min: Optional[float] = None
    salario_max: Optional[float] = None
    total_admissoes: Optional[int] = None
    total_desligamentos: Optional[int] = None
    saldo_total: Optional[int] = None
    ufs: List[str] = []
    anos: List[int] = []
    sexos: List[str] = []
    racas: List[str] = []
    grandes_grupos: List[str] = []


class FilterOptionsResponse(BaseModel):
    ufs: List[str]
    anos: List[int]
    sexos: List[str]
    racas: List[str]
    grandes_grupos: List[str]
    competencias: List[str]