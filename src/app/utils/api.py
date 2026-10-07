import httpx
import pandas as pd
import streamlit as st
from src.app.config import API_URL


@st.cache_data(ttl=300)
def fetch_gap_salarial(ano=None, uf=None, sexo=None, raca=None):
    params = {}
    if ano:
        params["ano"] = ano
    if uf:
        params["uf"] = uf
    if sexo:
        params["sexo"] = sexo
    if raca:
        params["raca"] = raca
    with httpx.Client(timeout=30.0) as client:
        r = client.get(f"{API_URL}/gap-salarial", params=params)
        r.raise_for_status()
        return pd.DataFrame(r.json())


@st.cache_data(ttl=300)
def fetch_funil_lideranca(ano=None, uf=None, sexo=None, raca=None):
    params = {}
    if ano:
        params["ano"] = ano
    if uf:
        params["uf"] = uf
    if sexo:
        params["sexo"] = sexo
    if raca:
        params["raca"] = raca
    with httpx.Client(timeout=30.0) as client:
        r = client.get(f"{API_URL}/funil-lideranca", params=params)
        r.raise_for_status()
        return pd.DataFrame(r.json())


@st.cache_data(ttl=300)
def fetch_perfil_mensal(competencia=None, uf=None, sexo=None, raca=None, lideranca=None):
    params = {}
    if competencia:
        params["competencia"] = competencia
    if uf:
        params["uf"] = uf
    if sexo:
        params["sexo"] = sexo
    if raca:
        params["raca"] = raca
    if lideranca is not None:
        params["lideranca"] = lideranca
    with httpx.Client(timeout=30.0) as client:
        r = client.get(f"{API_URL}/perfil-mensal", params=params)
        r.raise_for_status()
        return pd.DataFrame(r.json())