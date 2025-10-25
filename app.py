import streamlit as st
import pandas as pd
import plotly.express as px
import os
from modules.data_loader import load_data
from modules.utils import map_dependencia, map_localizacao
from pages import overview, matriculas, infraestrutura, corpo_docente

# --- Configuração da Página ---
st.set_page_config(
    page_title="Censo da Educação Básica 2024 - Painel Analítico",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Carregamento de Dados (Cache) ---
df = load_data()

# --- Sidebar (Filtros Globais) ---
st.sidebar.title("Filtros de Análise")

# 1. Filtro de Dependência Administrativa (Rede de Ensino)
dependencia_options = ['Todas'] + list(df['TP_DEPENDENCIA_DESC'].unique())
selected_dependencia = st.sidebar.selectbox(
    "Rede de Ensino (Dependência Administrativa)",
    dependencia_options
)

# 2. Filtro de Localização
localizacao_options = ['Todas'] + list(df['TP_LOCALIZACAO_DESC'].unique())
selected_localizacao = st.sidebar.selectbox(
    "Localização",
    localizacao_options
)

# 3. Filtro de Estado (UF)
uf_options = ['Todas'] + sorted(df['SG_UF'].unique().tolist())
selected_uf = st.sidebar.selectbox(
    "Estado (UF)",
    uf_options
)

# 4. Filtro de Região
regiao_options = ['Todas'] + sorted(df['NO_REGIAO'].unique().tolist())
selected_regiao = st.sidebar.selectbox(
    "Região Geográfica",
    regiao_options
)

# --- Aplicação dos Filtros ---
df_filtered = df.copy()

if selected_dependencia != 'Todas':
    df_filtered = df_filtered[df_filtered['TP_DEPENDENCIA_DESC'] == selected_dependencia]

if selected_localizacao != 'Todas':
    df_filtered = df_filtered[df_filtered['TP_LOCALIZACAO_DESC'] == selected_localizacao]

if selected_uf != 'Todas':
    df_filtered = df_filtered[df_filtered['SG_UF'] == selected_uf]

if selected_regiao != 'Todas':
    df_filtered = df_filtered[df_filtered['NO_REGIAO'] == selected_regiao]

# --- Título Principal ---
st.title("🇧🇷 Censo da Educação Básica 2024: Painel Analítico")
st.markdown("Uma visão estratégica e intuitiva dos microdados do Censo Escolar, focada em clareza e narrativa visual.")

# --- Estrutura de Abas Temáticas ---
tab_overview, tab_matriculas, tab_infraestrutura, tab_docente = st.tabs([
    "Visão Geral e Contexto", 
    "Matrículas e Etapas de Ensino", 
    "Infraestrutura e Recursos", 
    "Corpo Docente e Turmas"
])

# --- Conteúdo das Abas ---

with tab_overview:
    overview.render(df_filtered)

with tab_matriculas:
    matriculas.render(df_filtered)

with tab_infraestrutura:
    infraestrutura.render(df_filtered)

with tab_docente:
    corpo_docente.render(df_filtered)

# --- Rodapé ---
st.sidebar.markdown("---")
st.sidebar.caption("Dados: Censo da Educação Básica 2024")
