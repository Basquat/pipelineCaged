"""Lê .7z/.txt brutos, limpa e grava parquet particionado por ano.

Uso: python -m src.clean
"""
import re
import unicodedata
from pathlib import Path
import pandas as pd
from . import config as C


def _norm(c: str) -> str:
    c = unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", c.lower())


def extrair(arq7z: Path, dest: Path = C.INTERIM) -> Path:
    import py7zr  # import tardio
    dest.mkdir(parents=True, exist_ok=True)
    with py7zr.SevenZipFile(arq7z) as z:
        z.extractall(dest)
        nome = z.getnames()[0]
    return dest / nome


def ler_txt(txt: Path, chunksize: int = 1_000_000):
    """Gera DataFrames já filtrados/renomeados (arquivos têm milhões de linhas)."""
    cab = pd.read_csv(txt, sep=";", encoding="latin-1", nrows=0).columns
    mapa = {c: C.COLS[_norm(c)] for c in cab if _norm(c) in C.COLS}
    for ch in pd.read_csv(txt, sep=";", encoding="latin-1", decimal=",",
                          usecols=list(mapa), dtype=str, chunksize=chunksize):
        yield ch.rename(columns=mapa)


def limpar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["salario"] = pd.to_numeric(df["salario"].str.replace(",", ".", regex=False), errors="coerce")
    for c in ("saldo", "idade", "horas_contratuais"):
        df[c] = pd.to_numeric(df[c].str.replace(",", ".", regex=False), errors="coerce")
    df["horas_contratuais"] = df["horas_contratuais"].astype("float32")
    df = df[df["sexo_cod"].isin(C.SEXO)]                     # só Homem/Mulher
    df = df[df["raca_cor_cod"].isin(C.RACA)]
    df["sexo"] = df["sexo_cod"].map(C.SEXO)
    df["raca_cor"] = df["raca_cor_cod"].map(C.RACA)
    df["uf"] = df["uf_cod"].map(C.UF)
    df["cbo"] = df["cbo"].str.zfill(6)
    df["cbo_grande_grupo"] = df["cbo"].str[0]
    df["grande_grupo_nome"] = df["cbo_grande_grupo"].map(C.GRANDE_GRUPO_CBO)
    df["lideranca"] = df["cbo_grande_grupo"].eq(C.LIDERANCA_GG)
    df["tipo_mov"] = df["saldo"].map({1: "Admissão", -1: "Desligamento"})
    df["ano"] = df["competencia"].str[:4].astype("int16")
    df["mes"] = df["competencia"].str[4:6].astype("int8")
    # salário inválido vira NaN (mantém a linha para contagens)
    df.loc[df["salario"] < C.SALARIO_MIN_VALIDO, "salario"] = pd.NA
    df["raca_cor_agrupada"] = df["raca_cor"].map(
        {"Branca": "Branca", "Amarela": "Amarela", "Preta": "Negra (preta+parda)",
         "Parda": "Negra (preta+parda)", "Indígena": "Indígena"}).fillna("Não informada")
    cols = ["ano", "mes", "competencia", "uf", "municipio_cod", "cnae_secao", "cbo",
            "cbo_grande_grupo", "grande_grupo_nome", "lideranca", "sexo", "raca_cor",
            "raca_cor_agrupada", "idade", "grau_instrucao_cod", "horas_contratuais",
            "tam_estab_cod", "tipo_mov", "tipo_mov_cod", "saldo", "salario", "fora_prazo"]
    return df[[c for c in cols if c in df.columns]]


def processar(raw: Path = C.RAW, out: Path = C.PROCESSED / "movimentacoes"):
    out.mkdir(parents=True, exist_ok=True)
    arqs = sorted(raw.glob("CAGEDMOV*.7z")) + sorted(raw.glob("CAGEDFOR*.7z"))
    for a in arqs:
        txt = extrair(a)
        partes = [limpar(ch) for ch in ler_txt(txt)]
        txt.unlink(missing_ok=True)
        if not partes:
            continue
        df = pd.concat(partes, ignore_index=True)
        df.to_parquet(out / f"{a.stem}.parquet", index=False)
        print(f"[ok] {a.stem}: {len(df):,} linhas")


if __name__ == "__main__":
    processar()
