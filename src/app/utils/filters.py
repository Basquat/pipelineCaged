"""Shared filter sidebar component for all dashboard pages."""
import streamlit as st
import pandas as pd
from typing import Optional, Tuple


def render_filters(
    df: pd.DataFrame,
    page_type: str = "gap",
) -> Tuple[Optional[int], Optional[str], Optional[str], Optional[str], Optional[bool]]:
    """Render a consistent filter sidebar and return selected filter values.

    Args:
        df: Raw DataFrame with all available data (used to populate filter options).
        page_type: One of "gap", "funil", " perfil".

    Returns:
        Tuple of (ano, uf, sexo, raca, lideranca) where each may be None for "all".
    """
    st.markdown("### 🎛️ Filtros")
    st.markdown("---")

    if df.empty:
        st.warning("⚠️ Sem dados. Rode o pipeline: `make aggregate`")
        st.stop()

    # Ano filter (gap and funil pages)
    ano = None
    if page_type in ("gap", "funil"):
        anos = sorted(df["ano"].unique(), reverse=True)
        ano = st.selectbox("📅 Ano", anos, index=0, key=f"ano_{page_type}")

    # UF filter
    if page_type == "perfil":
        ufs = ["Todas"] + sorted(df["uf"].unique())
    else:
        ufs = ["Todas"] + sorted(df[df["ano"] == ano]["uf"].unique() if ano else df["uf"].unique())
    uf = st.selectbox("🗺️ UF", ufs, key=f"uf_{page_type}")

    # Sexo filter
    sexos = ["Todos"] + sorted(df["sexo"].unique())
    sexo = st.selectbox("👥 Sexo", sexos, key=f"sexo_{page_type}")

    # Raça filter
    racas = ["Todas"] + sorted(df["raca_cor_agrupada"].unique())
    raca = st.selectbox("🌍 Raça agrupada", racas, key=f"raca_{page_type}")

    # Liderança filter (only perfil page)
    lideranca = None
    if page_type == "perfil":
        opts = {"Todas": None, "Sim (Liderança)": True, "Não (Sem liderança)": False}
        label = st.selectbox("👔 Liderança", list(opts.keys()), key="lideranca")
        lideranca = opts[label]

    # Competência slider (only perfil page)
    comp_range = None
    if page_type == "perfil":
        competencias = sorted(df["competencia"].unique())
        comp_range = st.select_slider(
            "📅 Competência (intervalo)",
            options=competencias,
            value=(competencias[0], competencias[-1]),
            key="competencia_slider",
        )

    st.markdown("---")
    st.markdown(
        f"<div style='font-size: 0.75rem; color: #707070;'>"
        f"📊 {len(df):,} registros</div>",
        unsafe_allow_html=True,
    )

    return ano, uf, sexo, raca, lideranca, comp_range


def apply_filters(
    df: pd.DataFrame,
    ano: Optional[int] = None,
    uf: Optional[str] = None,
    sexo: Optional[str] = None,
    raca: Optional[str] = None,
   lideranca: Optional[bool] = None,
    competencia_range: Optional[Tuple[str, str]] = None,
) -> pd.DataFrame:
    """Apply selected filters to a DataFrame."""
    result = df.copy()
    if ano is not None:
        result = result[result["ano"] == ano]
    if uf is not None and uf != "Todas":
        result = result[result["uf"] == uf]
    if sexo is not None and sexo != "Todos":
        result = result[result["sexo"] == sexo]
    if raca is not None and raca != "Todas":
        result = result[result["raca_cor_agrupada"] == raca]
    if lideranca is not None:
        result = result[result["lideranca"] == lideranca]
    if competencia_range is not None:
        comp_min, comp_max = competencia_range
        result = result[(result["competencia"] >= comp_min) & (result["competencia"] <= comp_max)]
    return result


def show_empty_state(message: str = "Nenhum dado para os filtros selecionados."):
    """Show a friendly empty state."""
    st.markdown(
        f"""
        <div style="background: #1A1D24; border: 1px solid #2D3139; border-radius: 10px;
                    padding: 40px; text-align: center; margin: 20px 0;">
            <h3 style="color: #FF9F1C; margin: 0 0 8px 0;">⚠️ {message}</h3>
            <p style="color: #A0A0A0; margin: 0;">
                Tente ajustar os filtros no menu lateral.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )