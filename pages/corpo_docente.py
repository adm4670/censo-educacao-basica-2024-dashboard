import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

COLOR_PALETTE = px.colors.qualitative.Plotly

def render(df):
    """Renderiza a aba de Corpo Docente e Turmas."""
    st.header("Corpo Docente e Turmas")
    st.markdown("""Esta seção foca nos recursos humanos e na organização das turmas, fornecendo indicadores 
        críticos para a qualidade do ensino, como a relação aluno-professor e o tamanho médio das turmas.""")

    # 1. Relação Aluno-Professor (RAP)
    st.subheader("Relação Aluno-Professor (RAP) e Tamanho Médio das Turmas")

    # Cálculo do RAP e Alunos por Turma
    total_matriculas = df['QT_MAT_BAS'].sum()
    total_docentes = df['QT_DOC_BAS'].sum()
    total_turmas = df['QT_TUR_BAS'].sum()
    
    rap = total_matriculas / total_docentes if total_docentes > 0 else 0
    apt = total_matriculas / total_turmas if total_turmas > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total de Matrículas", value=f"{total_matriculas:,}".replace(",", "."))
    with col2:
        st.metric(label="Relação Aluno-Professor (RAP)", value=f"{rap:.1f} alunos/docente")
    with col3:
        st.metric(label="Alunos por Turma (APT)", value=f"{apt:.1f} alunos/turma")

    st.markdown("""
        **Interpretação:** A **Relação Aluno-Professor (RAP)** e o **Alunos por Turma (APT)** são indicadores 
        de eficiência e qualidade. Um RAP muito alto pode sugerir sobrecarga de trabalho para os docentes, 
        enquanto um APT elevado pode impactar negativamente a atenção individualizada ao aluno.
    """)

    st.markdown("---")

    st.subheader("Distribuição de Docentes por Etapa de Ensino")
    doc_cols = {
        'QT_DOC_INF': 'Educação Infantil',
        'QT_DOC_FUND': 'Ensino Fundamental',
        'QT_DOC_MED': 'Ensino Médio',
    }
    
    df_doc_etapa = df[list(doc_cols.keys())].sum().reset_index()
    df_doc_etapa.columns = ['Variavel', 'Total de Docentes']
    df_doc_etapa['Etapa de Ensino'] = df_doc_etapa['Variavel'].map(doc_cols)
    
    fig_doc = px.bar(
        df_doc_etapa,
        x='Etapa de Ensino',
        y='Total de Docentes',
        color='Etapa de Ensino',
        title='Total de Docentes por Etapa de Ensino',
        labels={'Total de Docentes': 'Docentes'},
        color_discrete_sequence=COLOR_PALETTE
    )
    fig_doc.update_layout(xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig_doc, use_container_width=True)

    st.markdown("""
        **Interpretação:** Este gráfico mostra a alocação de docentes pelas principais etapas de ensino. 
        A distribuição deve ser analisada em conjunto com a distribuição de matrículas (aba anterior) 
        para verificar se a alocação de pessoal está proporcional à demanda de alunos em cada etapa.
    """)
    
    st.markdown("---")

    st.subheader("Relação Aluno-Professor (RAP) por Rede de Ensino")
    df_rap_dependencia = df.groupby('TP_DEPENDENCIA_DESC').agg(
        total_matriculas=('QT_MAT_BAS', 'sum'),
        total_docentes=('QT_DOC_BAS', 'sum')
    ).reset_index()
    
    df_rap_dependencia['RAP'] = np.where(
        df_rap_dependencia['total_docentes'] > 0, 
        df_rap_dependencia['total_matriculas'] / df_rap_dependencia['total_docentes'], 
        0
    )
    
    fig_rap = px.bar(
        df_rap_dependencia,
        x='TP_DEPENDENCIA_DESC',
        y='RAP',
        color='TP_DEPENDENCIA_DESC',
        text='RAP',
        title='RAP por Dependência Administrativa',
        labels={'TP_DEPENDENCIA_DESC': 'Rede de Ensino', 'RAP': 'Relação Aluno-Professor'},
        color_discrete_sequence=COLOR_PALETTE
    )
    fig_rap.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_rap.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', yaxis_range=[0, df_rap_dependencia['RAP'].max() * 1.1])
    st.plotly_chart(fig_rap, use_container_width=True)

    st.markdown("""**Interpretação:** O comparativo do RAP entre as redes de ensino revela diferenças na gestão de pessoal. 
        A Rede Federal, por exemplo, frequentemente apresenta um RAP menor devido à sua natureza e foco. 
        Valores muito discrepantes entre redes (pública vs. privada, ou municipal vs. estadual) merecem 
        investigação para entender as causas e possíveis impactos na qualidade.""")
