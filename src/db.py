import os
import pandas as pd
from sqlalchemy import (Boolean, Column, Date, Float, Integer, MetaData, Numeric, SmallInteger,
                        String, Table, create_engine)
from . import config as C

URL = os.getenv("AIVEN_DB_URL", f"sqlite:///{C.ROOT / 'data' / 'local.db'}")
URL = URL.replace("postgres://", "postgresql://", 1).replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(URL, pool_pre_ping=True)
meta = MetaData()


def _dim(*extra):
    return [Column("uf", String(2), primary_key=True), Column("sexo", String(10), primary_key=True),
            Column("raca_cor_agrupada", String(30), primary_key=True), *extra]


colaboradores = Table(
    "colaboradores", meta,
    Column("id", Integer, primary_key=True),
    Column("nome", String(120), nullable=False),
    Column("sexo", String(10), nullable=False),
    Column("raca_cor", String(20), nullable=False),
    Column("cargo", String(120), nullable=False),
    Column("salario", Numeric(12, 2), nullable=False),
    Column("data_admissao", Date, nullable=False),
    Column("data_lideranca", Date),
)
AGREGADOS = [
    Table("agg_gap_salarial", meta, Column("ano", SmallInteger, primary_key=True),
          *_dim(Column("grande_grupo_nome", String(60), primary_key=True)),
          Column("n", Integer), Column("salario_medio", Numeric(12, 2)), Column("salario_mediano", Numeric(12, 2))),
    Table("agg_funil_lideranca", meta, Column("ano", SmallInteger, primary_key=True),
          *_dim(Column("grande_grupo_nome", String(60), primary_key=True)),
          Column("admissoes", Integer), Column("pct_no_grupo_demografico", Float)),
    Table("agg_perfil_mensal", meta, Column("competencia", String(6), primary_key=True),
          *_dim(Column("lideranca", Boolean, primary_key=True)),
          Column("saldo", Integer), Column("movs", Integer)),
]


def ler(tabela: str) -> pd.DataFrame:
    return pd.read_sql_table(tabela, engine)


def carregar():
    meta.create_all(engine)
    with engine.begin() as c:
        for t in AGREGADOS:
            c.execute(t.delete())
            df = pd.read_csv(C.PROCESSED / f"{t.name}.csv", dtype={"competencia": str})
            df.to_sql(t.name, c, if_exists="append", index=False, chunksize=5000)
            print(f"[ok] {t.name}: {len(df):,} linhas")


if __name__ == "__main__":
    carregar()
