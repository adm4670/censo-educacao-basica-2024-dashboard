import streamlit as st
import pandas as pd
import plotly.express as px

# Paleta de cores padrão Plotly (mais rica e diversificada)
COLOR_PALETTE = px.colors.qualitative.Plotly

def render(df):
    """Renderiza a aba de Infraestrutura e Recursos."""
    st.header("Infraestrutura e Recursos")
    st.markdown("""
        A qualidade da educação está intrinsecamente ligada à infraestrutura disponível nas escolas. 
        Esta seção analisa a proporção de escolas que possuem recursos essenciais, como água potável, 
        internet, laboratórios e quadras esportivas.
    """)

    # 1. Indicadores de Infraestrutura (Gráfico de Barras - Proporção de Escolas)
    st.subheader("Proporção de Escolas com Infraestrutura Essencial")

    # Colunas de Infraestrutura (Binárias - 1: Sim, 0: Não)
    # Variáveis adicionais baseadas no dicionário de dados (microdados_unidade_coleta)
    infra_cols = {
        'IN_AGUA_POTAVEL': 'Água Potável',
        'IN_INTERNET': 'Acesso à Internet',
        'IN_ACESSIBILIDADE': 'Acessibilidade', # Variável que foi ignorada antes, mas é crucial
        'IN_LABORATORIO_INFORMATICA': 'Laboratório de Informática',
        'IN_LABORATORIO_CIENCIAS': 'Laboratório de Ciências',
        'IN_QUADRA_ESPORTES': 'Quadra Esportiva',
        'IN_BIBLIOTECA': 'Biblioteca'
    }
    
    # Filtrar colunas que realmente existem no DataFrame
    infra_cols_existentes = {k: v for k, v in infra_cols.items() if k in df.columns}

    # Cálculo da proporção de escolas com o recurso
    total_escolas = df['CO_ENTIDADE'].nunique()
    
    data_infra = []
    for col, label in infra_cols_existentes.items():
        # Contagem de escolas que possuem o recurso (valor 1)
        escolas_com_recurso = df[df[col] == 1]['CO_ENTIDADE'].nunique()
        proporcao = (escolas_com_recurso / total_escolas) * 100 if total_escolas > 0 else 0
        data_infra.append({'Recurso': label, 'Proporção (%)': proporcao})

    df_infra = pd.DataFrame(data_infra)
    
    fig_infra = px.bar(
        df_infra,
        x='Recurso',
        y='Proporção (%)',
        text='Proporção (%)',
        title=f'Proporção de Escolas com Recursos Essenciais (Total de Escolas: {total_escolas:,})'.replace(",", "."),
        labels={'Proporção (%)': 'Proporção de Escolas (%)'},
        color='Recurso', # Usando cor para diferenciar as categorias
        color_discrete_sequence=COLOR_PALETTE
    )
    fig_infra.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_infra.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', yaxis_range=[0, 100])
    st.plotly_chart(fig_infra, use_container_width=True)

    st.markdown("""
        **Interpretação:** O gráfico de barras exibe o percentual de escolas que possuem cada um dos recursos 
        de infraestrutura. A presença de recursos como laboratórios e bibliotecas é essencial para a 
        qualidade do ensino e para a formação integral dos alunos.
    """)

    st.markdown("---")

    # 2. Análise Comparativa: Internet por Localização
    st.subheader("Acesso à Internet: Comparativo Urbano vs. Rural")
    
    # Agrupamento por Localização (Urbana/Rural) e contagem de escolas com Internet
    df_internet = df.groupby('TP_LOCALIZACAO_DESC').agg(
        total_escolas=('CO_ENTIDADE', 'nunique'),
        escolas_com_internet=('IN_INTERNET', 'sum')
    ).reset_index()
    
    df_internet['Proporção (%)'] = (df_internet['escolas_com_internet'] / df_internet['total_escolas']) * 100
    
    fig_internet = px.bar(
        df_internet,
        x='TP_LOCALIZACAO_DESC',
        y='Proporção (%)',
        color='TP_LOCALIZACAO_DESC',
        text='Proporção (%)',
        title='Proporção de Escolas com Internet por Localização',
        labels={'TP_LOCALIZACAO_DESC': 'Localização', 'Proporção (%)': 'Proporção de Escolas com Internet (%)'},
        color_discrete_sequence=[COLOR_PALETTE[0], COLOR_PALETTE[1]]
    )
    fig_internet.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_internet.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', yaxis_range=[0, 100])
    st.plotly_chart(fig_internet, use_container_width=True)

    st.markdown("""
        **Interpretação:** A comparação entre as escolas urbanas e rurais no que tange ao acesso à Internet 
        é fundamental. A disparidade observada (se houver) é um indicador de **desigualdade digital**, 
        com sérias implicações para o ensino e a aprendizagem.
    """)

