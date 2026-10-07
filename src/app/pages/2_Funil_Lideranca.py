import streamlit as st
import plotly.express as px
from src.app.utils.api import fetch_funil_lideranca

st.set_page_config(page_title="Funil Liderança", layout="wide")
st.header("🎯 Funil de Liderança — Admissões em Cargos de Liderança")
st.caption("Participação (% das admissões) em cada grande grupo CBO, com destaque para liderança (Grande Grupo 1)")

with st.sidebar:
    st.header("Filtros")
    df_raw = fetch_funil_lideranca()
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

df = fetch_funil_lideranca(
    ano=ano,
    uf=None if uf == "Todas" else uf,
    sexo=None if sexo == "Todos" else sexo,
    raca=None if raca == "Todas" else raca,
)

if df.empty:
    st.info("Nenhum dado para os filtros selecionados.")
    st.stop()

lideranca_df = df[df["grande_grupo_nome"] == "Dirigentes e gerentes"].copy()

st.subheader("Participação em Liderança (Grande Grupo 1) por grupo demográfico")
if not lideranca_df.empty:
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            lideranca_df.sort_values("pct_no_grupo_demografico", ascending=True),
            x="pct_no_grupo_demografico",
            y="raca_cor_agrupada",
            color="sexo",
            orientation="h",
            labels={"pct_no_grupo_demografico": "% das admissões em liderança", "raca_cor_agrupada": "Raça"},
            barmode="group",
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.bar(
            lideranca_df.sort_values("admissoes", ascending=True),
            x="admissoes",
            y="raca_cor_agrupada",
            color="sexo",
            orientation="h",
            labels={"admissoes": "Nº admissões em liderança", "raca_cor_agrupada": "Raça"},
            barmode="group",
        )
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Sem admissões em liderança para os filtros atuais.")

st.divider()

st.subheader("Distribuição completa das admissões por grande grupo CBO")
fig3 = px.bar(
    df,
    x="grande_grupo_nome",
    y="pct_no_grupo_demografico",
    color="sexo",
    facet_col="raca_cor_agrupada",
    labels={"pct_no_grupo_demografico": "% das admissões no grupo demográfico", "grande_grupo_nome": "Grande grupo CBO"},
    category_orders={"grande_grupo_nome": sorted(df["grande_grupo_nome"].unique())},
)
fig3.update_xaxes(tickangle=45)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Tabela completa")
st.dataframe(
    df.sort_values(["grande_grupo_nome", "sexo", "raca_cor_agrupada"]),
    use_container_width=True,
    hide_index=True,
)