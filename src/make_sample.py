"""Gera um .7z SINTÉTICO no layout oficial para testar o pipeline offline."""
import numpy as np, pandas as pd
from pathlib import Path
from . import config as C


def gerar(ano=2024, mes=1, n=5000, raw: Path = C.RAW, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "competênciamov": f"{ano}{mes:02d}", "região": "3",
        "uf": rng.choice(list(C.UF), n), "município": "292740",
        "seção": rng.choice(list("ACGHIQ"), n), "subclasse": "4711301",
        "saldomovimentação": rng.choice([1, -1], n),
        "cbo2002ocupação": rng.choice(["142105", "211110", "513205", "782510", "411010"], n),
        "categoria": "101", "graudeinstrução": rng.integers(1, 10, n),
        "idade": rng.integers(18, 65, n), "horascontratuais": "44,00",
        "raçacor": rng.choice(["1", "2", "3", "4", "6", "9"], n),
        "sexo": rng.choice(["1", "3", "9"], n, p=[.55, .44, .01]),
        "tipoempregador": "0", "tipoestabelecimento": "1", "tipomovimentação": "10",
        "tipodedeficiência": "0", "indtrabintermitente": "0", "indtrabparcial": "0",
        "salário": [f"{x:.2f}".replace(".", ",") for x in rng.lognormal(7.5, .4, n)],
        "tamestabjan": "5", "indicadoraprendiz": "0", "origemdainformação": "1",
        "competênciadec": f"{ano}{mes:02d}", "indicadordeforadoprazo": "0",
        "unidadesaláriocódigo": "5", "valorsaláriofixo": "0,00",
    })
    raw.mkdir(parents=True, exist_ok=True)
    txt = raw / f"CAGEDMOV{ano}{mes:02d}.txt"
    df.to_csv(txt, sep=";", index=False, encoding="latin-1")
    import py7zr
    with py7zr.SevenZipFile(raw / f"CAGEDMOV{ano}{mes:02d}.7z", "w") as z:
        z.write(txt, txt.name)
    txt.unlink()


if __name__ == "__main__":
    gerar()
