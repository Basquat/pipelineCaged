import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.app.utils.api import fetch_perfil_mensal
from src.app.utils.ui import (
    load_custom_css, render_metric_card, render_section_header, 
    render_kpi_row, format_currency, format_number
)

st.set_page_config(page_title="Perfil Mensal", layout="wide", page_icon="📈")

load_custom_css()

st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="margin: 0; background: linear-gradient(90deg, #00B450, #2ED573); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📈 Perfil Mensal — Saldo e Volume de Movimentações</h1>
    <p style="color: #A0A0A0; margin-top: 8px;">Saldo (admissões - desligamentos) e total de movimentações por competência, UF, sexo, raça e liderança</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎛️ Filtros")
    df_raw = fetch_perfil_mensal()
    if df_raw.empty:
        st.warning("Sem dados. Rode o pipeline: `make aggregate`")
        st.stop()

    ufs = ["Todas"] + sorted(df_raw["uf"].unique())
    uf = st.selectbox("🗺️ UF", ufs)

    sexos = ["Todos"] + sorted(df_raw["sexo"].unique())
    sexo = st.selectbox("👥 Sexo", sexos)

    racas = ["Todas"] + sorted(df_raw["raca_cor_agrupada"].unique())
    raca = st.selectbox("🌍 Raça agrupada", racas)

    lideranca_opts = {"Todas": None, "Sim (Liderança)": True, "Não": False}
    lideranca_label = st.selectbox("👔 Liderança", list(lideranca_opts.keys()))
    lideranca = lideranca_opts[lideranca_label]

    competencias = sorted(df_raw["competencia"].unique())
    comp_min, comp_max = st.select_slider(
        "📅 Competência (intervalo)",
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

saldo_total = df["saldo"].sum()
admissoes_total = df[df["saldo"] > 0]["saldo"].sum() if "saldo" in df.columns else 0
movs_total = df["movs"].sum()
competencias_count = df["competencia"].nunique()
saldo_medio_mensal = df.groupby("competencia")["saldo"].sum().mean()
ultima_competencia = df["competencia"].max()
saldo_ultimo = df[df["competencia"] == ultima_competencia]["saldo"].sum()

render_section_header("Indicadores Mensais", "📊")
render_kpi_row([
    ("Saldo Total no Período", format_number(saldo_total), f"Média mensal: {format_number(saldo_medio_mensal)}", saldo_total >= 0, "⚖️"),
    ("Total Movimentações", format_number(movs_total), f"{competencias_count} competências", True, "🔄"),
    ("Última Competência", str(ultima_competencia), f"Saldo: {format_number(saldo_ultimo)}", saldo_ultimo >= 0, "📅"),
    ("Admissões Estimadas", format_number(admissoes_total), "Baseado em saldo positivo", True, "📥"),
])

render_section_header("Saldo Mensal (Admissões - Desligamentos)", "📈")

saldo_mensal = df.groupby("competencia", as_index=False)["saldo"].sum().sort_values("competencia")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=saldo_mensal["competencia"],
    y=saldo_mensal["saldo"],
    mode='lines+markers',
    line=dict(color='#00B450', width=3),
    marker=dict(size=8, color='#00B450', line=dict(width=2, color='#0E1117')),
    fill='tozeroy',
    fillcolor='rgba(0, 180, 80, 0.15)',
    name='Saldo',
    hovertemplate='<b>Competência: %{x}</b><br>Saldo: %{y:,.0f}<extra></extra>',
))
fig.add_hline(y=0, line_dash="dash", line_color="#707070", line_width=1)
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#E0E0E0', family='sans-serif'),
    xaxis=dict(title="Competência", gridcolor='#2D3139', tickangle=45),
    yaxis=dict(title="Saldo", gridcolor='#2D3139'),
    hovermode='x unified',
    margin=dict(l=10, r=10, t=20, b=60),
    height=450,
)
st.plotly_chart(fig, use_container_width=True)

render_section_header("Volume de Movimentações Mensais", "📊")

movs_mensal = df.groupby("competencia", as_index=False)["movs"].sum().sort_values("competencia")

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=movs_mensal["competencia"],
    y=movs_mensal["movs"],
    marker_color='#1E90FF',
    marker_line=dict(width=0),
    name='Movimentações',
    text=movs_mensal["movs"].apply(lambda x: f'{x:,.0f}'),
    textposition='outside',
    textfont=dict(color='#E0E0E0', size=10),
    hovertemplate='<b>Competência: %{x}</b><br>Movimentações: %{y:,.0f}<extra></extra>',
))
fig2.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#E0E0E0', family='sans-serif'),
    xaxis=dict(title="Competência", gridcolor='#2D3139', tickangle=45),
    yaxis=dict(title="Total de movimentações", gridcolor='#2D3139'),
    margin=dict(l=10, r=10, t=20, b=60),
    height=400,
)
st.plotly_chart(fig2, use_container_width=True)

render_section_header("Saldo por Sexo e Raça (Últimas 12 Competências)", "👥")

competencias_unicas = sorted(df["competencia"].unique())
recent_comps = competencias_unicas[-12:] if len(competencias_unicas) >= 12 else competencias_unicas
recent = df[df["competencia"].isin(recent_comps)]

fig3 = px.line(
    recent.groupby(["competencia", "sexo", "raca_cor_agrupada"], as_index=False)["saldo"].sum(),
    x="competencia",
    y="saldo",
    color="sexo",
    line_dash="raca_cor_agrupada",
    markers=True,
    labels={"saldo": "Saldo", "competencia": "Competência", "sexo": "Sexo", "raca_cor_agrupada": "Raça"},
    color_discrete_map={"Homem": "#1E90FF", "Mulher": "#FF4757"},
)
fig3.add_hline(y=0, line_dash="dash", line_color="#707070", line_width=1)
fig3.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#E0E0E0', family='sans-serif'),
    xaxis=dict(gridcolor='#2D3139', tickangle=45),
    yaxis=dict(gridcolor='#2D3139'),
    legend=dict(bgcolor='rgba(26,29,36,0.9)', bordercolor='#2D3139', orientation='h', y=1.1),
    margin=dict(l=10, r=10, t=20, b=60),
    height=450,
)
st.plotly_chart(fig3, use_container_width=True)

render_section_header("Heatmap: Saldo por Competência e Sexo/Raça", "🔥")

heatmap_data = recent.groupby(["competencia", "sexo", "raca_cor_agrupada"], as_index=False)["saldo"].sum()
heatmap_pivot = heatmap_data.pivot_table(
    index=["sexo", "raca_cor_agrupada"],
    columns="competencia",
    values="saldo",
    fill_value=0
)

fig4 = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values,
    x=heatmap_pivot.columns,
    y=[f"{row[0]} - {row[1]}" for row in heatmap_pivot.index],
    colorscale=[[0, '#FF4757'], [0.5, '#0E1117'], [1, '#00B450']],
    colorbar=dict(title="Saldo", tickfont=dict(color='#E0E0E0')),
    hovertemplate='<b>%{y}</b><br>Competência: %{x}<br>Saldo: %{z:,.0f}<extra></extra>',
))
fig4.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#E0E0E0', family='sans-serif'),
    xaxis=dict(title="Competência", gridcolor='#2D3139', tickangle=45),
    yaxis=dict(gridcolor='#2D3139'),
    margin=dict(l=10, r=10, t=20, b=60),
    height=400,
)
st.plotly_chart(fig4, use_container_width=True)

render_section_header("Tabela (Últimas 20 Competências)", "📋")

df_display = df.sort_values("competencia", ascending=False).head(20)
st.dataframe(
    df_display.style.format({
        "saldo": "{:,.0f}",
        "movs": "{:,.0f}",
        "admissoes": "{:,.0f}",
        "desligamentos": "{:,.0f}",
    }).background_gradient(subset=["saldo"], cmap="RdYlGn", vmin=-df_display["saldo"].abs().max(), vmax=df_display["saldo"].abs().max()).background_gradient(subset=["movs"], cmap="Blues"),
    use_container_width=True,
    hide_index=True,
    height=400,
)

st.markdown("""
<div class="footer">
    Fonte: MTE/PDET — Microdados do Novo CAGED | Saldo = Admissões - Desligamentos
</div>
""", unsafe_allow_html=True)