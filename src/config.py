"""Configuração central do pipeline Novo CAGED."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"

FTP_HOST = "ftp.mtps.gov.br"
FTP_BASE = "/pdet/microdados/NOVO CAGED"   # /{ano}/{ano}{mes}/CAGEDMOV{ano}{mes}.7z
# CAGEDMOV = movimentações no prazo | CAGEDFOR = fora do prazo | CAGEDEXC = excluídas
FILE_TYPES = ["CAGEDMOV", "CAGEDFOR"]      # EXC é usado para remover registros (ver clean.py)

# Colunas originais (após normalização sem acento/minúscula) -> nomes finais
COLS = {
    "competenciamov": "competencia",
    "uf": "uf_cod",
    "municipio": "municipio_cod",
    "secao": "cnae_secao",
    "saldomovimentacao": "saldo",
    "cbo2002ocupacao": "cbo",
    "graudeinstrucao": "grau_instrucao_cod",
    "idade": "idade",
    "horascontratuais": "horas_contratuais",
    "racacor": "raca_cor_cod",
    "sexo": "sexo_cod",
    "tipomovimentacao": "tipo_mov_cod",
    "salario": "salario",
    "tamestabjan": "tam_estab_cod",
    "indicadordeforadoprazo": "fora_prazo",
}

SEXO = {"1": "Homem", "3": "Mulher"}  # 9 = não identificado (descartado nas análises)
RACA = {"1": "Branca", "2": "Preta", "3": "Parda", "4": "Amarela",
        "5": "Indígena", "6": "Não informada", "9": "Não identificada"}
GRANDE_GRUPO_CBO = {
    "0": "Forças Armadas", "1": "Dirigentes e gerentes",
    "2": "Profissionais das ciências e artes", "3": "Técnicos de nível médio",
    "4": "Serviços administrativos", "5": "Serviços e comércio",
    "6": "Agropecuária", "7": "Produção industrial (bens e serviços)",
    "8": "Produção industrial (processos contínuos)", "9": "Manutenção e reparação",
}
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
      "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL",
      "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
# Liderança = Grande Grupo 1 da CBO-2002 (dirigentes e gerentes)
LIDERANCA_GG = "1"
SALARIO_MIN_VALIDO = 100.0  # descarta salários irreais (erro de digitação/centavos)
