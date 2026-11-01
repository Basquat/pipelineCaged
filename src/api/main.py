from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Literal, Optional
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError
from src.db import AGREGADOS, colaboradores as T, engine, ler, meta


@asynccontextmanager
async def lifespan(_):
    try:
        meta.create_all(engine)
    except OperationalError:
        pass
    yield


app = FastAPI(title="Trajetórias até a Liderança", lifespan=lifespan)


class Colaborador(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    sexo: Literal["Homem", "Mulher"]
    raca_cor: Literal["Branca", "Preta", "Parda", "Amarela", "Indígena"]
    cargo: str = Field(min_length=1, max_length=120)
    salario: float = Field(gt=0)
    data_admissao: date
    data_lideranca: Optional[date] = None

    @model_validator(mode="after")
    def datas(self):
        if self.data_lideranca and self.data_lideranca < self.data_admissao:
            raise ValueError("data_lideranca anterior à data_admissao")
        return self


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(Path(__file__).with_name("dashboard.html"))


@app.get("/cadastro", include_in_schema=False)
def cadastro():
    return FileResponse(Path(__file__).with_name("cadastro.html"))


@app.get("/api/agregados")
def agregados():
    return {t.name: ler(t.name).to_dict("records") for t in AGREGADOS}


@app.get("/healthz")
def healthz(response: Response):
    try:
        with engine.connect() as c:
            c.execute(text("select 1"))
        return {"status": "ok"}
    except Exception:
        response.status_code = 503
        return {"status": "indisponivel"}


@app.get("/colaboradores")
def listar():
    with engine.connect() as c:
        return [dict(r._mapping) for r in c.execute(select(T).order_by(T.c.id))]


@app.post("/colaboradores", status_code=201)
def criar(d: Colaborador):
    with engine.begin() as c:
        return {"id": c.execute(T.insert().values(**d.model_dump()).returning(T.c.id)).scalar_one()}


@app.put("/colaboradores/{id}")
def editar(id: int, d: Colaborador):
    with engine.begin() as c:
        if not c.execute(T.update().where(T.c.id == id).values(**d.model_dump())).rowcount:
            raise HTTPException(404)
    return {"id": id}


@app.delete("/colaboradores/{id}", status_code=204)
def excluir(id: int):
    with engine.begin() as c:
        if not c.execute(T.delete().where(T.c.id == id)).rowcount:
            raise HTTPException(404)
