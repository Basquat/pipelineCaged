import os
import tempfile

os.environ["AIVEN_DB_URL"] = f"sqlite:///{tempfile.mkdtemp()}/t.db"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from src.api import main

REG = {"nome": "Ana", "sexo": "Mulher", "raca_cor": "Preta", "cargo": "Gerente",
       "salario": 9500.5, "data_admissao": "2020-03-01", "data_lideranca": "2024-06-01"}


def test_crud_e_healthz(monkeypatch):
    with TestClient(main.app) as c:
        assert c.get("/healthz").status_code == 200
        id = c.post("/colaboradores", json=REG).json()["id"]
        assert c.get("/colaboradores").json() == [{"id": id, **REG}]
        assert c.put(f"/colaboradores/{id}", json={**REG, "cargo": "Diretora", "salario": 15000}).status_code == 200
        assert c.get("/colaboradores").json()[0]["cargo"] == "Diretora"
        assert c.post("/colaboradores", json={**REG, "data_lideranca": "2019-01-01"}).status_code == 422
        assert c.post("/colaboradores", json={**REG, "sexo": "X"}).status_code == 422
        assert c.delete(f"/colaboradores/{id}").status_code == 204
        assert c.get("/colaboradores").json() == []
        monkeypatch.setattr(main, "engine", create_engine("postgresql+psycopg://x:x@127.0.0.1:1/x"))
        assert c.get("/healthz").status_code == 503
