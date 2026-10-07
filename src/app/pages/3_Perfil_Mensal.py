import streamlit as st
import plotly.express as px
import pandas as pd
from src.app.utils.api import fetch_perfil_mensal

st.set_page_config(page_title="Perfil Mensal", layout="wide")
st.header("📈 Perfil Mensal — Saldo e Volume de Movimentações")
st.caption("Saldo (admissões - desligamentos) e total de movimentações por competência, UF, sexo, raça e liderança")

with st.sidebar:
    st.header("Filtros")
    df_raw = fetch_perfil_mensal()
    if df_raw.empty:
        st.warning("Sem dados. Rode o pipeline: `make aggregate`")
        st.stop()

    ufs = ["Todas"] + sorted(df_raw["uf"].unique())
    uf = st.selectbox("UF", ufs)

    sexos = ["Todos"] + sorted(df_raw["sexo"].unique())
    sexo = st.selectbox("Sexo", sexos)

    racas = ["Todas"] + sorted(df_raw["raca_cor_agrupada"].unique())
    raca = st.selectbox("Raça agrupada", racas)

    lideranca_opts = {"Todas": None, "Sim (Liderança)": True, "Não": False}
    lideranca_label = st.selectbox("Liderança", list(lideranca_opts.keys()))
    lideranca = lideranca_opts[lideranca_label]

    competencias = sorted(df_raw["competencia"].unique())
    comp_min, comp_max = st.select_slider(
        "Competência (intervalo)",
        options=competencias,
        value=(competencias[0], competencias[-1]),
    )

df = fetch_perfil_mensal(
    uf=None if uf == "Todas" else uf,
    sexo=None if sexo == "Todos" else sexo,
    raca=None if raca == "Todas" else raca,
    lideranca=lideranca,
)
df = df[(df["competencia"] >= comp_min) & (df["competencia"] <= comp_max)]

if df.empty:
    st.info("Nenhum dado para os filtros selecionados.")
    st.stop()

st.subheader("Saldo mensal (Admissões - Desligamentos)")
saldo_mensal = df.groupby("competencia", as_index=False)["saldo"].sum()
fig = px.line(
    saldo_mensal,
    x="competencia",
    y="saldo",
    markers=True,
    labels={"saldo": "Saldo", "competencia": "Competência"},
)
fig.add_hline(y=0, line_dash="dash", line_color="gray")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Volume de movimentações mensais")
movs_mensal = df.groupby("competencia", as_index=False)["movs"].sum()
fig2 = px.bar(
    movs_mensal,
    x="competencia",
    y="movs",
    labels={"movs": "Total de movimentações", "competencia": "Competência"},
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Saldo por sexo e raça (últimas 12 competências)")
recent = df[df["competencia"] >= sorted(df["competencia"].unique())[-12]]
fig3 = px.line(
    recent.groupby(["competencia", "sexo", "raca_cor_agrupada"], as_index=False)["saldo"].sum(),
    x="competencia",
    y="saldo",
    color="sexo",
    line_dash="raca_cor_agrupada",
    markers=True,
    labels={"saldo": "Saldo", "competencia": "Competência"},
)
fig3.add_hline(y=0, line_dash="dash", line_color="gray")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Tabela (últimas 20 competências)")
st.dataframe(
    df.sort_values("competencia", ascending=False).head(20),
    use_container_width=True,
    hide_index=True,
)