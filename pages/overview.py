import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

COLOR_PALETTE = px.colors.qualitative.Plotly

def render(df):
    """Renderiza a aba de Visão Geral e Contexto."""
    st.header("Visão Geral e Contexto da Educação Básica")
    st.markdown("""
        Esta seção apresenta os indicadores macro da rede de ensino, permitindo uma compreensão rápida 
        da distribuição de escolas, matrículas e docentes no contexto dos filtros aplicados.
    """)

    col1, col2, col3, col4 = st.columns(4)
    
    total_escolas = df["CO_ENTIDADE"].nunique()
    total_matriculas = df["QT_MAT_BAS"].sum()
    total_docentes = df["QT_DOC_BAS"].sum()
    total_turmas = df["QT_TUR_BAS"].sum()

    with col1:
        st.metric(label="Total de Escolas", value=f"{total_escolas:,}".replace(",", "."))
    with col2:
        st.metric(label="Total de Matrículas", value=f"{total_matriculas:,}".replace(",", "."))
    with col3:
        st.metric(label="Total de Docentes", value=f"{total_docentes:,}".replace(",", "."))
    with col4:
        st.metric(label="Total de Turmas", value=f"{total_turmas:,}".replace(",", "."))

    st.markdown("---")

    st.subheader("Distribuição de Matrículas por Rede de Ensino")
    
    df_dependencia = df.groupby("TP_DEPENDENCIA_DESC")["QT_MAT_BAS"].sum().reset_index()
    df_dependencia.columns = ["Rede de Ensino", "Total de Matrículas"]
    
    fig_dependencia = px.bar(
        df_dependencia,
        x="Rede de Ensino",
        y="Total de Matrículas",
        color="Rede de Ensino",
        title="Matrículas por Dependência Administrativa",
        labels={"Total de Matrículas": "Matrículas"},
        color_discrete_sequence=COLOR_PALETTE
    )
    fig_dependencia.update_layout(xaxis={"categoryorder": "total descending"})
    st.plotly_chart(fig_dependencia, use_container_width=True)
    
    st.markdown("""
        **Interpretação:** O gráfico de barras ilustra o **volume de matrículas** em cada rede de ensino. 
        As redes estaduais e municipais concentram a maior parte das matrículas da educação básica. 
        Essa visualização é fundamental para entender a responsabilidade de cada esfera administrativa.
    """)
    
    st.markdown("---")
    st.subheader("Análise Regional: Relação Aluno-Professor (RAP) e Acesso à Internet")
    
    df_regional = df.groupby("NO_REGIAO").agg(
        total_matriculas=("QT_MAT_BAS", "sum"),
        total_docentes=("QT_DOC_BAS", "sum"),
        escolas_com_internet=("IN_INTERNET", "sum"),
        total_escolas=("CO_ENTIDADE", "nunique")
    ).reset_index()

    df_regional["RAP"] = np.where(
        df_regional["total_docentes"] > 0, 
        df_regional["total_matriculas"] / df_regional["total_docentes"], 
        0
    )
    df_regional["Proporção Internet (%)"] = np.where(
        df_regional["total_escolas"] > 0, 
        (df_regional["escolas_com_internet"] / df_regional["total_escolas"]) * 100, 
        0
    )
    
    fig_regional = go.Figure()

    fig_regional.add_trace(go.Bar(
        name='RAP (Alunos/Docente)',
        x=df_regional['NO_REGIAO'],
        y=df_regional['RAP'],
        yaxis='y',
        marker_color=COLOR_PALETTE[0]
    ))

    fig_regional.add_trace(go.Bar(
        name='Internet (%)',
        x=df_regional['NO_REGIAO'],
        y=df_regional['Proporção Internet (%)'],
        yaxis='y2',
        marker_color=COLOR_PALETTE[1]
    ))

    fig_regional.update_layout(
        title='Comparativo de Indicadores por Região',
        xaxis_title="Região Geográfica",
        yaxis=dict(
            title='RAP (Alunos/Docente)',
            side='left'
        ),
        yaxis2=dict(
            title='Proporção de Escolas com Internet (%)',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        barmode='group',
        legend=dict(x=0, y=1.1, orientation="h")
    )
    st.plotly_chart(fig_regional, use_container_width=True)

    st.markdown("""
        **Interpretação:** Este gráfico de barras duplas permite uma **análise comparativa regional**. 
        A **Relação Aluno-Professor (RAP)** (eixo esquerdo) indica a sobrecarga potencial dos docentes, 
        enquanto a **Proporção de Escolas com Internet** (eixo direito) reflete a infraestrutura digital. 
        Regiões com RAP alto e baixa conectividade podem enfrentar os maiores desafios de qualidade.""")
