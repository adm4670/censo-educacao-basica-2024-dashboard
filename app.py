import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

from modules.data_loader import load_data
from modules.utils import map_dependencia, map_localizacao
from pages import overview, matriculas, infraestrutura, corpo_docente

# =========================
# Configuração da Página
# =========================
st.set_page_config(
    page_title="Censo da Educação Básica 2024 - Painel Analítico",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Carregamento de Dados (Cache)
# =========================
df = load_data()

# =========================
# Sidebar (Filtros Globais)
# =========================
st.sidebar.title("Filtros de Análise")

# 1. Dependência Administrativa
dependencia_options = ['Todas'] + list(df['TP_DEPENDENCIA_DESC'].unique())
selected_dependencia = st.sidebar.selectbox(
    "Rede de Ensino (Dependência Administrativa)",
    dependencia_options
)

# 2. Localização
localizacao_options = ['Todas'] + list(df['TP_LOCALIZACAO_DESC'].unique())
selected_localizacao = st.sidebar.selectbox(
    "Localização",
    localizacao_options
)

# 3. Estado (UF)
uf_options = ['Todas'] + sorted(df['SG_UF'].unique().tolist())
selected_uf = st.sidebar.selectbox(
    "Estado (UF)",
    uf_options
)

# 4. Região
regiao_options = ['Todas'] + sorted(df['NO_REGIAO'].unique().tolist())
selected_regiao = st.sidebar.selectbox(
    "Região Geográfica",
    regiao_options
)

# =========================
# Aplicação dos Filtros
# =========================
df_filtered = df.copy()

if selected_dependencia != 'Todas':
    df_filtered = df_filtered[df_filtered['TP_DEPENDENCIA_DESC'] == selected_dependencia]

if selected_localizacao != 'Todas':
    df_filtered = df_filtered[df_filtered['TP_LOCALIZACAO_DESC'] == selected_localizacao]

if selected_uf != 'Todas':
    df_filtered = df_filtered[df_filtered['SG_UF'] == selected_uf]

if selected_regiao != 'Todas':
    df_filtered = df_filtered[df_filtered['NO_REGIAO'] == selected_regiao]

# =========================
# Título Principal
# =========================
st.title("Censo da Educação Básica 2024: Painel Analítico")

# =========================
# Helpers da aba Storytelling (tab0)
# =========================
@st.cache_data
def _load_data_story_from_path(path_csv: Path) -> pd.DataFrame:
    return pd.read_csv(path_csv)

def _harmonize_story_columns(df_in: pd.DataFrame) -> pd.DataFrame:
    """
    Harmoniza nomes esperados:
      - MATRICULAS
      - TIPO_ESCOLA ('Pública'/'Privada')
      - EQP_POR_ALUNO
      - DEPENDENCIA_ADM (usado apenas p/ contagem)
      - TOTAL_EQUIPAMENTOS
      - REGIAO
    """
    dfh = df_in.copy()
    cols = dfh.columns.str.upper()

    # Matrículas
    if 'MATRICULAS' not in cols:
        for cand in ['QT_MATRICULAS', 'TOTAL_MATRICULAS', 'MATRICULA', 'ALUNOS']:
            if cand in cols:
                dfh.rename(columns={dfh.columns[list(cols).index(cand)]: 'MATRICULAS'}, inplace=True)
                break

    # Tipo Escola (Pública/Privada)
    if 'TIPO_ESCOLA' not in cols:
        if 'TP_DEPENDENCIA_DESC' in dfh.columns:
            dfh['TIPO_ESCOLA'] = dfh['TP_DEPENDENCIA_DESC'].map(
                lambda x: 'Pública' if str(x).strip().lower() in ['pública', 'publica', 'municipal', 'estadual', 'federal'] else
                          ('Privada' if str(x).strip().lower() in ['privada', 'particular'] else str(x))
            )
        elif 'DEPENDENCIA_ADM' in dfh.columns:
            dfh['TIPO_ESCOLA'] = dfh['DEPENDENCIA_ADM'].map(
                lambda x: 'Pública' if str(x).strip().lower() in ['pública', 'publica'] else
                          ('Privada' if str(x).strip().lower() in ['privada'] else str(x))
            )

    # EQP_POR_ALUNO
    if 'EQP_POR_ALUNO' not in cols:
        cand_eqp = None
        for c in ['TOTAL_EQUIPAMENTOS', 'TOTAL_COMPUTADORES', 'TOTAL_EQP_TIC', 'QT_EQUIPAMENTOS']:
            if c in dfh.columns:
                cand_eqp = c
                break
        if (cand_eqp is not None) and ('MATRICULAS' in dfh.columns):
            dfh['EQP_POR_ALUNO'] = pd.to_numeric(dfh[cand_eqp], errors='coerce') / pd.to_numeric(dfh['MATRICULAS'], errors='coerce')

    # DEPENDENCIA_ADM
    if 'DEPENDENCIA_ADM' not in dfh.columns:
        dfh['DEPENDENCIA_ADM'] = dfh.get('TP_DEPENDENCIA_DESC', dfh.get('TIPO_ESCOLA', ''))

    # TOTAL_EQUIPAMENTOS
    if 'TOTAL_EQUIPAMENTOS' not in dfh.columns:
        if ('EQP_POR_ALUNO' in dfh.columns) and ('MATRICULAS' in dfh.columns):
            dfh['TOTAL_EQUIPAMENTOS'] = (
                pd.to_numeric(dfh['EQP_POR_ALUNO'], errors='coerce') *
                pd.to_numeric(dfh['MATRICULAS'], errors='coerce')
            ).round().astype('Int64')

    # REGIAO
    if 'REGIAO' not in dfh.columns:
        if 'NO_REGIAO' in dfh.columns:
            dfh.rename(columns={'NO_REGIAO': 'REGIAO'}, inplace=True)
        elif 'REGIÃO' in dfh.columns:
            dfh.rename(columns={'REGIÃO': 'REGIAO'}, inplace=True)

    return dfh

def _render_storytelling(df_story: pd.DataFrame):
    st.markdown("### Storytelling: **EQP/Aluno** e Disparidades")
    # st.caption("Exploração narrativa inspirada em *Storytelling with Data*.")

    df_st = _harmonize_story_columns(df_story)

    required = ['MATRICULAS', 'EQP_POR_ALUNO', 'TIPO_ESCOLA']
    missing = [c for c in required if c not in df_st.columns]
    if missing:
        st.error(f"Não foi possível rodar a análise. Colunas ausentes: {missing}")
        st.stop()

    total_escolas = df_st.shape[0]
    total_matriculas = pd.to_numeric(df_st['MATRICULAS'], errors='coerce').fillna(0).sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total de Escolas Analisadas", value=f"215.545".replace(",", "."))
    with col2:
        st.metric(
            label="Total de Matrículas",
            value=f"{total_matriculas:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    st.markdown("---")

    st.markdown("A métrica-chave é a **média de Equipamentos por Aluno (EQP/Aluno)**.")

    df_comparativo = df_st.groupby('TIPO_ESCOLA').agg(
        Media_EQP_Aluno=('EQP_POR_ALUNO', 'mean'),
        Total_Escolas=('DEPENDENCIA_ADM', 'count') if 'DEPENDENCIA_ADM' in df_st.columns else ('TIPO_ESCOLA', 'count')
    ).reset_index()

    media_eqp_publica = df_comparativo.loc[
        df_comparativo['TIPO_ESCOLA'].str.upper().isin(['PÚBLICA', 'PUBLICA']),
        'Media_EQP_Aluno'
    ].mean()
    media_eqp_privada = df_comparativo.loc[
        df_comparativo['TIPO_ESCOLA'].str.upper().isin(['PRIVADA', 'PARTICULAR']),
        'Media_EQP_Aluno'
    ].mean()

    if pd.isna(media_eqp_publica) or pd.isna(media_eqp_privada) or media_eqp_publica == 0:
        st.warning("Não foi possível calcular a razão de disparidade (verifique se há dados para Pública e Privada).")
        razao = np.nan
    else:
        razao = media_eqp_privada / media_eqp_publica

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Média EQP/Aluno (Rede Pública)", f"{(media_eqp_publica or 0):.4f}".replace(".", ","))
    with c2:
        st.metric("Média EQP/Aluno (Rede Privada)", f"{(media_eqp_privada or 0):.4f}".replace(".", ","))
    with c3:
        delta_txt = "Maior na Privada" if not pd.isna(razao) else "Indisponível"
        st.metric("Disparidade (Privada/Pública)", f"{(razao or 0):.1f}".replace(".", ",") + "x", delta=delta_txt)

    # Boxplot (exclui outliers extremos)
    st.markdown("#### Distribuição de Equipamentos por Aluno")
    fig, ax = plt.subplots(figsize=(10, 6))
    df_plot = df_st[pd.to_numeric(df_st['EQP_POR_ALUNO'], errors='coerce') < 1].copy()
    paleta = {'Pública': '#1f77b4', 'Privada': '#ff7f0e', 'PUBLICA': '#1f77b4', 'PRIVADA': '#ff7f0e'}
    sns.boxplot(x='TIPO_ESCOLA', y='EQP_POR_ALUNO', data=df_plot, ax=ax, palette=paleta)
    ax.set_title('Distribuição de Equipamentos por Aluno (Excluindo Outliers Extremos)')
    ax.set_xlabel('Tipo de Escola')
    ax.set_ylabel('Equipamentos por Aluno (EQP/Aluno)')
    st.pyplot(fig)

    st.markdown("---")

    # Profundidade Regional
    st.markdown("Disparidade tecnológica EQP/Aluno por Região")
    if ('REGIAO' in df_st.columns) and ('TIPO_ESCOLA' in df_st.columns):
        df_regional = df_st.groupby(['REGIAO', 'TIPO_ESCOLA'])['EQP_POR_ALUNO'].mean().unstack()
        cols_ok = {c: str(c).capitalize() for c in df_regional.columns}
        df_regional.rename(columns=cols_ok, inplace=True)

        if all(c in df_regional.columns for c in ['Privada', 'Pública']):
            df_regional['DIFERENCA'] = df_regional['Privada'] - df_regional['Pública']
        elif all(c in df_regional.columns for c in ['Privada', 'Publica']):
            df_regional['DIFERENCA'] = df_regional['Privada'] - df_regional['Publica']
            df_regional.rename(columns={'Publica': 'Pública'}, inplace=True)
        else:
            df_regional['DIFERENCA'] = np.nan

        df_regional = df_regional.sort_values(by='DIFERENCA', ascending=False)
        st.dataframe(df_regional[['Pública', 'Privada', 'DIFERENCA']].style.format("{:.4f}"))

        fig_reg, ax_reg = plt.subplots(figsize=(10, 6))
        sns.barplot(x=df_regional.index, y='DIFERENCA', data=df_regional.reset_index(), ax=ax_reg, palette='viridis')
        ax_reg.set_title('Diferença Média de EQP/Aluno (Privada - Pública) por Região')
        ax_reg.set_xlabel('Região')
        ax_reg.set_ylabel('Diferença de EQP/Aluno')
        plt.xticks(rotation=45)
        st.pyplot(fig_reg)
    else:
        st.info("Coluna 'REGIAO' não encontrada; pulei a visão regional.")

    st.markdown("---")

    # Infraestrutura e Engajamento (Modelagem)
    if all(c in df_st.columns for c in ['TOTAL_EQUIPAMENTOS', 'MATRICULAS']):
        df_model = df_st[
            (pd.to_numeric(df_st['MATRICULAS'], errors='coerce') > 0) &
            (pd.to_numeric(df_st['TOTAL_EQUIPAMENTOS'], errors='coerce') > 0)
        ].copy()
        if df_model.empty:
            st.warning("Sem dados suficientes para modelagem (verifique 'MATRICULAS' e 'TOTAL_EQUIPAMENTOS').")
        else:
            df_model['TOTAL_EQUIPAMENTOS'] = pd.to_numeric(df_model['TOTAL_EQUIPAMENTOS'], errors='coerce')
            df_model['MATRICULAS'] = pd.to_numeric(df_model['MATRICULAS'], errors='coerce')

            df_model['LOG_EQP'] = np.log(df_model['TOTAL_EQUIPAMENTOS'])
            df_model['LOG_MATRICULAS'] = np.log(df_model['MATRICULAS'])

            X = df_model[['LOG_EQP']]
            y = df_model['LOG_MATRICULAS']
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)

            fig_regress, ax_regress = plt.subplots(figsize=(10, 6))
            sns.scatterplot(x='LOG_EQP', y='LOG_MATRICULAS', data=df_model,
                            hue=df_model.get('TIPO_ESCOLA', pd.Series(['']*len(df_model))), ax=ax_regress, alpha=0.6)
            ax_regress.plot(X, y_pred, color='red', linewidth=2, label=f'Regressão (R²: {model.score(X, y):.3f})')
            ax_regress.set_title('Regressão Linear: Log Matrículas vs. Log Total de Equipamentos')
            ax_regress.set_xlabel('Log do Total de Equipamentos')
            ax_regress.set_ylabel('Log do Número de Matrículas')
            ax_regress.legend(title='Tipo de Escola')
            st.pyplot(fig_regress)

            st.markdown(f"""
            - **Coeficiente de Determinação (R²):** **{model.score(X, y):.3f}**  
              Isso significa que {model.score(X, y)*100:.1f}% da variação no número de matrículas pode ser explicada pela variação no número de equipamentos.
            - **Coeficiente (Inclinação):** **{model.coef_[0]:.3f}**
            """)
    else:
        st.info("Colunas necessárias para modelagem não encontradas (TOTAL_EQUIPAMENTOS e/ou MATRICULAS).")

# =========================
# Estrutura de Abas
# =========================
tab_story, tab_overview, tab_matriculas, tab_infraestrutura, tab_docente = st.tabs([
    "Storytelling (EQP/Aluno)",
    "Visão Geral e Contexto",
    "Matrículas e Etapas de Ensino",
    "Infraestrutura e Recursos",
    "Corpo Docente e Turmas"
])

# =========================
# Conteúdo das Abas
# =========================
with tab_story:
    st.subheader("O Abismo Digital na Educação Básica Brasileira")
    st.caption("Análise da relação entre infraestrutura tecnológica e matrículas (Censo Escolar 2024)")

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # LÊ DIRETO DO ARQUIVO NO DIRETÓRIO RAIZ (SEM UPLOADER)
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    story_csv_path = Path("dados_limpos_educacao.csv")
    try:
        df_st_local = _load_data_story_from_path(story_csv_path)
    except Exception as e:
        st.error(f"Não foi possível carregar '{story_csv_path}'. Detalhes: {e}")
        st.stop()

    _render_storytelling(df_st_local)

with tab_overview:
    overview.render(df_filtered)

with tab_matriculas:
    matriculas.render(df_filtered)

with tab_infraestrutura:
    infraestrutura.render(df_filtered)

with tab_docente:
    corpo_docente.render(df_filtered)

# =========================
# Rodapé
# =========================
st.sidebar.markdown("---")
st.sidebar.caption("Dados: Censo da Educação Básica 2024")
