import streamlit as st
from pathlib import Path


def load_custom_css():
    """Load custom CSS for PowerBI-style theme"""
    css_path = Path(__file__).parent.parent / ".streamlit" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_metric_card(title: str, value: str, delta: str = None, delta_positive: bool = True, icon: str = ""):
    """Render a custom metric card with PowerBI styling"""
    delta_class = "positive" if delta_positive else "negative"
    delta_html = f'<div class="metric-card-delta {delta_class}">{delta}</div>' if delta else ""
    icon_html = f'<span style="font-size: 1.5rem; margin-right: 8px;">{icon}</span>' if icon else ""
    
    st.markdown(f"""
    <div class="metric-card animate-fade-in">
        <div class="metric-card-title">{icon_html}{title}</div>
        <div class="metric-card-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str, icon: str = "📊"):
    """Render a styled section header"""
    st.markdown(f"""
    <div class="section-header animate-fade-in">
        <div class="section-header-icon">{icon}</div>
        <h2 class="section-header-title">{title}</h2>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_row(metrics: list):
    """Render a row of KPI metric cards"""
    cols = st.columns(len(metrics))
    for col, (title, value, delta, delta_pos, icon) in zip(cols, metrics):
        with col:
            render_metric_card(title, value, delta, delta_pos, icon)


def format_currency(value: float) -> str:
    """Format value as Brazilian currency (R$ 1.234,56)"""
    if value >= 1_000_000:
        return f"R$ {value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"R$ {value/1_000:.1f}K"
    return f"R$ {value:,.2f}".replace(",", "|").replace(".", ",").replace("|", ".")


def format_number(value: float) -> str:
    """Format number with Brazilian notation"""
    if value >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    return f"{value:,.0f}".replace(",", ".")