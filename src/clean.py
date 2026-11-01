import re
import unicodedata
from pathlib import Path
import pandas as pd
from . import config as C


def _norm(c: str) -> str:
    c = unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", c.lower())


def extrair(arq7z: Path, dest: Path = C.INTERIM) -> Path:
    import py7zr
    dest.mkdir(parents=True, exist_ok=True)
    with py7zr.SevenZipFile(arq7z) as z:
        z.extractall(dest)
        nome = z.getnames()[0]
    return dest / nome


def ler_txt(txt: Path, chunksize: int = 1_000_000):
    cab = pd.read_csv(txt, sep=";", encoding="utf-8", nrows=0).columns
    mapa = {c: C.COLS[_norm(c)] for c in cab if _norm(c) in C.COLS}
    for ch in pd.read_csv(txt, sep=";", encoding="utf-8", decimal=",",
                          usecols=list(mapa), dtype=str, chunksize=chunksize):
        yield ch.rename(columns=mapa)


def limpar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["salario"] = pd.to_numeric(df["salario"].str.replace(",", ".", regex=False), errors="coerce")
    for c in ("saldo", "idade", "horas_contratuais"):
        df[c] = pd.to_numeric(df[c].str.replace(",", ".", regex=False), errors="coerce")
    df["horas_contratuais"] = df["horas_contratuais"].astype("float32")
    df = df[df["sexo_cod"].isin(C.SEXO)]
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
    df.loc[~df["salario"].between(C.SALARIO_MIN_VALIDO, C.SALARIO_MAX_VALIDO), "salario"] = pd.NA
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
        for i, ch in enumerate(ler_txt(txt)):
            limpar(ch).to_parquet(out / f"{a.stem}_{i}.parquet", index=False)
        txt.unlink(missing_ok=True)
        print(f"[ok] {a.stem}")


if __name__ == "__main__":
    processar()
