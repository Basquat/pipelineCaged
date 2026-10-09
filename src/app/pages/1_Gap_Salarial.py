import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.app.utils.api import fetch_gap_salarial
from src.app.utils.ui import (
    load_custom_css, render_metric_card, render_section_header, 
    render_kpi_row, format_currency, format_number
)

st.set_page_config(page_title="Gap Salarial", layout="wide", page_icon="💰")

load_custom_css()

st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="margin: 0; background: linear-gradient(90deg, #00B450, #2ED573); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💰 Gap Salarial — Salário de Admissão</h1>
    <p style="color: #A0A0A0; margin-top: 8px;">Salário médio e mediano de admissões (saldo = +1) por grande grupo CBO, sexo e raça</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎛️ Filtros")
    df_raw = fetch_gap_salarial()
    if df_raw.empty:
        st.warning("Sem dados. Rode o pipeline: `make aggregate`")
        st.stop()

    anos = sorted(df_raw["ano"].unique(), reverse=True)
    ano = st.selectbox("📅 Ano", anos, index=0)

    ufs = ["Todas"] + sorted(df_raw[df_raw["ano"] == ano]["uf"].unique())
    uf = st.selectbox("🗺️ UF", ufs)

    sexos = ["Todos"] + sorted(df_raw["sexo"].unique())
    sexo = st.selectbox("👥 Sexo", sexos)

    racas = ["Todas"] + sorted(df_raw["raca_cor_agrupada"].unique())
    raca = st.selectbox("🌍 Raça agrupada", racas)

df = fetch_gap_salarial(
    ano=ano,
    uf=None if uf == "Todas" else uf,
    sexo=None if sexo == "Todos" else sexo,
    raca=None if raca == "Todas" else raca,
)

if df.empty:
    st.info("Nenhum dado para os filtros selecionados.")
    st.stop()

salario_medio_geral = df["salario_medio"].mean()
salario_mediano_geral = df["salario_mediano"].mean()
total_admissoes = df["admissoes"].sum()
num_grupos = df["grande_grupo_nome"].nunique()

gap_df = df.pivot_table(
    index="grande_grupo_nome",
    columns="sexo",
    values="salario_medio",
    aggfunc="mean",
).reset_index()
gap_medio = 0
if "Homem" in gap_df.columns and "Mulher" in gap_df.columns:
    gap_df["gap"] = gap_df["Homem"] - gap_df["Mulher"]
    gap_medio = gap_df["gap"].mean()

render_section_header("Indicadores Principais", "📈")
render_kpi_row([
    ("Salário Médio Geral", format_currency(salario_medio_geral), None, True, "💵"),
    ("Salário Mediano Geral", format_currency(salario_mediano_geral), None, True, "📊"),
    ("Gap Médio (H-M)", format_currency(gap_medio), f"{gap_medio/salario_medio_geral*100:.1f}% da média", gap_medio <= 0, "⚖️"),
    ("Total Admissões", format_number(total_admissoes), f"{num_grupos} grupos CBO", True, "👥"),
])

render_section_header("Salário Médio por Grande Grupo CBO", "📊")

fig = px.bar(
    df.groupby("grande_grupo_nome", as_index=False)["salario_medio"].mean().sort_values("salario_medio", ascending=True),
    x="salario_medio",
    y="grande_grupo_nome",
    orientation="h",
    labels={"salario_medio": "Salário médio (R$)", "grande_grupo_nome": "Grande grupo CBO"},
    color="salario_medio",
    color_continuous_scale=[[0, "#0E1117"], [0.5, "#00B450"], [1, "#2ED573"]],
    text="salario_medio",
)
fig.update_traces(
    texttemplate='R$ %{x:,.0f}',
    textposition='outside',
    textfont=dict(color='#E0E0E0', size=11),
    hovertemplate='<b>%{y}</b><br>Salário médio: R$ %{x:,.2f}<extra></extra>',
)
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#E0E0E0', family='sans-serif'),
    xaxis=dict(gridcolor='#2D3139', zerolinecolor='#2D3139'),
    yaxis=dict(gridcolor='#2D3139', categoryorder='total ascending'),
    coloraxis_showscale=False,
    margin=dict(l=10, r=60, t=20, b=40),
    height=500,
)
st.plotly_chart(fig, use_container_width=True)

render_section_header("Gap Salarial: Homens vs Mulheres por Grande Grupo", "⚖️")

if "Homem" in gap_df.columns and "Mulher" in gap_df.columns:
    gap_df["gap"] = gap_df["Homem"] - gap_df["Mulher"]
    gap_df = gap_df.sort_values("gap", ascending=True)
    
    colors = ['#FF4757' if x > 0 else '#00B450' for x in gap_df["gap"]]
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=gap_df["grande_grupo_nome"],
        x=gap_df["gap"],
        orientation='h',
        marker_color=colors,
        text=gap_df["gap"].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside',
        textfont=dict(color='#E0E0E0', size=11),
        hovertemplate='<b>%{y}</b><br>Gap (H-M): R$ %{x:,.2f}<extra></extra>',
    ))
    fig2.add_vline(x=0, line_dash="dash", line_color="#707070", line_width=1)
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0', family='sans-serif'),
        xaxis=dict(title="Gap (Homem - Mulher) R$", gridcolor='#2D3139', zerolinecolor='#2D3139'),
        yaxis=dict(gridcolor='#2D3139', categoryorder='total ascending'),
        margin=dict(l=10, r=60, t=20, b=40),
        height=500,
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background: #1A1D24; border: 1px solid #2D3139; border-radius: 10px; padding: 16px;">
            <h4 style="color: #FF4757; margin: 0 0 8px 0;">🔴 Gap Positivo</h4>
            <p style="margin: 0; color: #A0A0A0;">Homens ganham mais que mulheres</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: #1A1D24; border: 1px solid #2D3139; border-radius: 10px; padding: 16px;">
            <h4 style="color: #00B450; margin: 0 0 8px 0;">🟢 Gap Negativo</h4>
            <p style="margin: 0; color: #A0A0A0;">Mulheres ganham mais que homens</p>
        </div>
        """, unsafe_allow_html=True)

render_section_header("Distribuição Salarial por Raça", "🌍")

fig3 = px.box(
    df,
    x="grande_grupo_nome",
    y="salario_medio",
    color="raca_cor_agrupada",
    points="outliers",
    labels={"salario_medio": "Salário médio (R$)", "grande_grupo_nome": "Grande grupo CBO", "raca_cor_agrupada": "Raça"},
    color_discrete_sequence=['#00B450', '#2ED573', '#FF9F1C', '#1E90FF', '#FF4757', '#A0A0A0'],
)
fig3.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#E0E0E0', family='sans-serif'),
    xaxis=dict(tickangle=45, gridcolor='#2D3139'),
    yaxis=dict(gridcolor='#2D3139'),
    legend=dict(bgcolor='rgba(26,29,36,0.9)', bordercolor='#2D3139'),
    margin=dict(l=10, r=10, t=20, b=80),
    height=500,
)
st.plotly_chart(fig3, use_container_width=True)

render_section_header("Tabela Detalhada", "📋")

st.dataframe(
    df.sort_values(["grande_grupo_nome", "sexo", "raca_cor_agrupada"]).style.format({
        "salario_medio": "R$ {:,.2f}",
        "salario_mediano": "R$ {:,.2f}",
        "admissoes": "{:,.0f}",
    }).background_gradient(subset=["salario_medio"], cmap="Greens"),
    use_container_width=True,
    hide_index=True,
    height=400,
)

st.markdown("""
<div class="footer">
    Fonte: MTE/PDET — Microdados do Novo CAGED | Pipeline: download → clean → aggregate → API → Dashboard
</div>
""", unsafe_allow_html=True)