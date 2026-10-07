"""Baixa os microdados do Novo CAGED do FTP do PDET (retomável).

Uso: python -m src.download --ini 2023-01 --fim 2024-12
"""
import argparse
import ftplib
from pathlib import Path
from .config import FTP_HOST, FTP_BASE, FILE_TYPES, RAW


def meses(ini: str, fim: str):
    a, m = map(int, ini.split("-")); a2, m2 = map(int, fim.split("-"))
    while (a, m) <= (a2, m2):
        yield a, m
        m += 1
        if m == 13:
            a, m = a + 1, 1


def baixar(ini: str, fim: str, tipos=FILE_TYPES, destino: Path = RAW):
    destino.mkdir(parents=True, exist_ok=True)
    ftp = ftplib.FTP(FTP_HOST, timeout=60)
    ftp.login()  # anônimo
    for ano, mes in meses(ini, fim):
        for t in tipos:
            nome = f"{t}{ano}{mes:02d}.7z"
            out = destino / nome
            if out.exists() and out.stat().st_size > 0:
                print(f"[skip] {nome}")
                continue
            caminho = f"{FTP_BASE}/{ano}/{ano}{mes:02d}/{nome}"
            try:
                with open(out, "wb") as f:
                    ftp.retrbinary(f"RETR {caminho}", f.write)
                print(f"[ok]   {nome}")
            except ftplib.error_perm as e:
                out.unlink(missing_ok=True)
                print(f"[n/d]  {nome} ({e})")  # mês ainda não publicado / sem arquivo
    ftp.quit()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ini", required=True, help="AAAA-MM")
    p.add_argument("--fim", required=True, help="AAAA-MM")
    a = p.parse_args()
    baixar(a.ini, a.fim)
