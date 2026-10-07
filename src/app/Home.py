import streamlit as st

st.set_page_config(
    page_title="Novo CAGED - Gap Salarial e Funil de Liderança",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Novo CAGED — Gap Salarial e Funil de Liderança")
st.caption("Dados do MTE/PDET — Microdados do Novo CAGED")

st.markdown("""
Este dashboard apresenta análises baseadas nos microdados do **Novo CAGED** (Cadastro Geral de Empregados e Desempregados),
focadas em **gap salarial** e **funil de liderança** por sexo e raça.

### Páginas disponíveis
- **1_Gap_Salarial** — Salário médio/mediano de admissão por grande grupo CBO, sexo e raça
- **2_Funil_Lideranca** — Participação em cargos de liderança (CBO Grande Grupo 1) por grupo demográfico
- **3_Perfil_Mensal** — Saldo e volume de movimentações mensais por UF, sexo, raça e liderança

### Filtros comuns
Todas as páginas suportam filtros por: **Ano**, **UF**, **Sexo**, **Raça agrupada**.

---
**Fonte:** `ftp.mtps.gov.br/pdet/microdados/NOVO CAGED`  
**Pipeline:** download → clean (Parquet) → aggregate (CSV) → API (FastAPI) → Dashboard (Streamlit)
""")

with st.expander("ℹ️ Metodologia e limitações"):
    st.markdown("""
- **Liderança** = CBO-2002 Grande Grupo 1 (Dirigentes e gerentes)
- **Salário** = salário de admissão (saldo = +1); valores < R$ 100 tratados como nulos
- **Raça agrupada**: Branca / Negra (preta+parda) / Amarela / Indígena / Não informada
- **Sexo**: Homem (1) e Mulher (3); código 9 descartado
- ⚠️ O Novo CAGED não tem identificador de trabalhador → não mede "tempo até liderança"
- O funil aqui é **transversal** (% de admissões em liderança por grupo), não longitudinal
""")

st.divider()
st.write("Use o menu lateral para navegar entre as páginas.")