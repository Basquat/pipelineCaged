import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.app.utils.api import fetch_funil_lideranca
from src.app.utils.ui import (
    load_custom_css, render_metric_card, render_section_header, 
    render_kpi_row, format_currency, format_number
)

st.set_page_config(page_title="Funil Liderança", layout="wide", page_icon="🎯")

load_custom_css()

st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="margin: 0; background: linear-gradient(90deg, #00B450, #2ED573); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🎯 Funil de Liderança — Admissões em Cargos de Liderança</h1>
    <p style="color: #A0A0A0; margin-top: 8px;">Participação (% das admissões) em cada grande grupo CBO, com destaque para liderança (Grande Grupo 1)</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎛️ Filtros")
    df_raw = fetch_funil_lideranca()
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

total_admissoes = df["admissoes"].sum()
total_lideranca = lideranca_df["admissoes"].sum() if not lideranca_df.empty else 0
pct_lideranca = (total_lideranca / total_admissoes * 100) if total_admissoes > 0 else 0
num_grupos_demo = df[["sexo", "raca_cor_agrupada"]].drop_duplicates().shape[0]

render_section_header("Indicadores de Liderança", "📈")
render_kpi_row([
    ("Total Admissões", format_number(total_admissoes), None, True, "👥"),
    ("Admissões em Liderança", format_number(total_lideranca), None, True, "👔"),
    ("% em Liderança", f"{pct_lideranca:.2f}%", f"{num_grupos_demo} grupos demográficos", True, "📊"),
    ("Grupos CBO", f"{df['grande_grupo_nome'].nunique()}", "Grande Grupo 1 = Liderança", True, "🏢"),
])

render_section_header("Participação em Liderança (Grande Grupo 1) por Grupo Demográfico", "🎯")

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
            color_discrete_map={"Homem": "#1E90FF", "Mulher": "#FF4757"},
            text="pct_no_grupo_demografico",
        )
        fig.update_traces(
            texttemplate='%{x:.2f}%',
            textposition='outside',
            textfont=dict(color='#E0E0E0', size=11),
            hovertemplate='<b>%{y}</b> - %{legendgroup}<br>% em liderança: %{x:.2f}%<extra></extra>',
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0', family='sans-serif'),
            xaxis=dict(gridcolor='#2D3139', title="% das admissões"),
            yaxis=dict(gridcolor='#2D3139', categoryorder='total ascending'),
            legend=dict(bgcolor='rgba(26,29,36,0.9)', bordercolor='#2D3139', orientation='h', y=1.1),
            margin=dict(l=10, r=60, t=40, b=40),
            height=450,
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
            color_discrete_map={"Homem": "#1E90FF", "Mulher": "#FF4757"},
            text="admissoes",
        )
        fig2.update_traces(
            texttemplate='%{x:,.0f}',
            textposition='outside',
            textfont=dict(color='#E0E0E0', size=11),
            hovertemplate='<b>%{y}</b> - %{legendgroup}<br>Admissões: %{x:,.0f}<extra></extra>',
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0', family='sans-serif'),
            xaxis=dict(gridcolor='#2D3139', title="Nº admissões"),
            yaxis=dict(gridcolor='#2D3139', categoryorder='total ascending'),
            legend=dict(bgcolor='rgba(26,29,36,0.9)', bordercolor='#2D3139', orientation='h', y=1.1),
            margin=dict(l=10, r=60, t=40, b=40),
            height=450,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        fig3 = px.sunburst(
            lideranca_df,
            path=["sexo", "raca_cor_agrupada"],
            values="admissoes",
            color="pct_no_grupo_demografico",
            color_continuous_scale=[[0, "#0E1117"], [0.5, "#00B450"], [1, "#2ED573"]],
            title="Composição das Admissões em Liderança",
        )
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0', family='sans-serif'),
            margin=dict(l=10, r=10, t=50, b=10),
            height=450,
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        fig4 = px.treemap(
            lideranca_df,
            path=["sexo", "raca_cor_agrupada"],
            values="admissoes",
            color="pct_no_grupo_demografico",
            color_continuous_scale=[[0, "#0E1117"], [0.5, "#00B450"], [1, "#2ED573"]],
            title="Treemap: Admissões em Liderança",
        )
        fig4.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0', family='sans-serif'),
            margin=dict(l=10, r=10, t=50, b=10),
            height=450,
        )
        st.plotly_chart(fig4, use_container_width=True)

else:
    st.markdown("""
    <div style="background: #1A1D24; border: 1px solid #2D3139; border-radius: 10px; padding: 40px; text-align: center;">
        <h3 style="color: #FF9F1C;">⚠️ Sem admissões em liderança</h3>
        <p style="color: #A0A0A0;">Nenhum dado de admissão em cargos de liderança para os filtros atuais.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

render_section_header("Distribuição Completa das Admissões por Grande Grupo CBO", "📊")

categorias_ordem = sorted(df["grande_grupo_nome"].unique())

fig5 = px.bar(
    df,
    x="grande_grupo_nome",
    y="pct_no_grupo_demografico",
    color="sexo",
    facet_col="raca_cor_agrupada",
    labels={"pct_no_grupo_demografico": "% das admissões no grupo demográfico", "grande_grupo_nome": "Grande grupo CBO"},
    category_orders={"grande_grupo_nome": categorias_ordem},
    color_discrete_map={"Homem": "#1E90FF", "Mulher": "#FF4757"},
    barmode="group",
)
fig5.update_xaxes(tickangle=45)
fig5.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#E0E0E0', family='sans-serif', size=10),
    xaxis=dict(gridcolor='#2D3139'),
    yaxis=dict(gridcolor='#2D3139'),
    legend=dict(bgcolor='rgba(26,29,36,0.9)', bordercolor='#2D3139', orientation='h', y=1.1),
    margin=dict(l=10, r=10, t=40, b=80),
    height=500,
)
st.plotly_chart(fig5, use_container_width=True)

render_section_header("Tabela Completa", "📋")

st.dataframe(
    df.sort_values(["grande_grupo_nome", "sexo", "raca_cor_agrupada"]).style.format({
        "admissoes": "{:,.0f}",
        "pct_no_grupo_demografico": "{:.2f}%",
    }).background_gradient(subset=["admissoes"], cmap="Greens").background_gradient(subset=["pct_no_grupo_demografico"], cmap="Blues"),
    use_container_width=True,
    hide_index=True,
    height=400,
)

st.markdown("""
<div class="footer">
    Fonte: MTE/PDET — Microdados do Novo CAGED | Liderança = CBO-2002 Grande Grupo 1 (Dirigentes e gerentes)
</div>
""", unsafe_allow_html=True)