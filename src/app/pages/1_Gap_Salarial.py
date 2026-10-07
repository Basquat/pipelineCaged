import streamlit as st
import plotly.express as px
from src.app.utils.api import fetch_gap_salarial

st.set_page_config(page_title="Gap Salarial", layout="wide")
st.header("💰 Gap Salarial — Salário de Admissão")
st.caption("Salário médio e mediano de admissões (saldo = +1) por grande grupo CBO, sexo e raça")

with st.sidebar:
    st.header("Filtros")
    df_raw = fetch_gap_salarial()
    if df_raw.empty:
        st.warning("Sem dados. Rode o pipeline: `make aggregate`")
        st.stop()

    anos = sorted(df_raw["ano"].unique(), reverse=True)
    ano = st.selectbox("Ano", anos, index=0)

    ufs = ["Todas"] + sorted(df_raw[df_raw["ano"] == ano]["uf"].unique())
    uf = st.selectbox("UF", ufs)

    sexos = ["Todos"] + sorted(df_raw["sexo"].unique())
    sexo = st.selectbox("Sexo", sexos)

    racas = ["Todas"] + sorted(df_raw["raca_cor_agrupada"].unique())
    raca = st.selectbox("Raça agrupada", racas)

df = fetch_gap_salarial(
    ano=ano,
    uf=None if uf == "Todas" else uf,
    sexo=None if sexo == "Todos" else sexo,
    raca=None if raca == "Todas" else raca,
)

if df.empty:
    st.info("Nenhum dado para os filtros selecionados.")
    st.stop()

st.subheader("Tabela")
st.dataframe(
    df.sort_values(["grande_grupo_nome", "sexo", "raca_cor_agrupada"]),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Salário médio por grande grupo CBO")
fig = px.bar(
    df.groupby("grande_grupo_nome", as_index=False)["salario_medio"].mean(),
    x="grande_grupo_nome",
    y="salario_medio",
    color="grande_grupo_nome",
    labels={"salario_medio": "Salário médio (R$)", "grande_grupo_nome": "Grande grupo CBO"},
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Gap: Salário médio Homens vs Mulheres por grande grupo")
gap_df = df.pivot_table(
    index="grande_grupo_nome",
    columns="sexo",
    values="salario_medio",
    aggfunc="mean",
).reset_index()
if "Homem" in gap_df.columns and "Mulher" in gap_df.columns:
    gap_df["gap"] = gap_df["Homem"] - gap_df["Mulher"]
    fig2 = px.bar(
        gap_df,
        x="grande_grupo_nome",
        y="gap",
        labels={"gap": "Gap (Homem - Mulher) R$", "grande_grupo_nome": "Grande grupo CBO"},
        color="gap",
        color_continuous_scale="RdBu_r",
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Detalhe por raça")
fig3 = px.box(
    df,
    x="grande_grupo_nome",
    y="salario_medio",
    color="raca_cor_agrupada",
    points="all",
    labels={"salario_medio": "Salário médio (R$)", "grande_grupo_nome": "Grande grupo CBO"},
)
st.plotly_chart(fig3, use_container_width=True)