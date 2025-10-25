import streamlit as st
import pandas as pd
import plotly.express as px

# Paleta de cores padrão Plotly (mais rica e diversificada)
COLOR_PALETTE = px.colors.qualitative.Plotly

def render(df):
    """Renderiza a aba de Matrículas e Etapas de Ensino."""
    st.header("Matrículas e Etapas de Ensino")
    st.markdown("""
        Esta seção detalha a distribuição das matrículas por etapa de ensino (Infantil, Fundamental, Médio, EJA, Especial, etc.), 
        oferecendo insights sobre a estrutura da demanda educacional e a oferta de ensino por rede.
    """)

    # Colunas de Matrículas por Etapa
    mat_cols = {
        'QT_MAT_INF': 'Educação Infantil',
        'QT_MAT_FUND': 'Ensino Fundamental',
        'QT_MAT_MED': 'Ensino Médio',
        'QT_MAT_EJA': 'EJA',
        'QT_MAT_ESP': 'Educação Especial'
    }
    
    # 1. Matrículas por Etapa de Ensino (Gráfico de Barras)
    st.subheader("Distribuição de Matrículas por Etapa de Ensino")
    
    # Agregação dos totais de matrícula por etapa
    df_mat_etapa = df[list(mat_cols.keys())].sum().reset_index()
    df_mat_etapa.columns = ['Variavel', 'Total de Matrículas']
    df_mat_etapa['Etapa de Ensino'] = df_mat_etapa['Variavel'].map(mat_cols)
    
    fig_etapa = px.bar(
        df_mat_etapa,
        x='Etapa de Ensino',
        y='Total de Matrículas',
        color='Etapa de Ensino', # Usando cor para diferenciar as categorias
        title='Total de Matrículas por Etapa de Ensino',
        labels={'Total de Matrículas': 'Matrículas'},
        color_discrete_sequence=COLOR_PALETTE
    )
    fig_etapa.update_layout(xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig_etapa, use_container_width=True)

    st.markdown("""
        **Interpretação:** O gráfico acima mostra a concentração das matrículas nas diferentes etapas. 
        O **Ensino Fundamental** é, historicamente, a etapa com maior volume. A análise da proporção 
        entre as etapas é vital para o planejamento de recursos e infraestrutura.
    """)

    st.markdown("---")

    # 2. Matrículas por Localização e Etapa (Análise Comparativa)
    st.subheader("Matrículas por Etapa e Localização (Urbana vs. Rural)")

    # Agregação por Localização e Etapa
    df_mat_local = df.groupby('TP_LOCALIZACAO_DESC')[list(mat_cols.keys())].sum().reset_index()
    
    # Transformar o DataFrame para o formato 'long' para visualização
    df_mat_local_long = pd.melt(
        df_mat_local, 
        id_vars=['TP_LOCALIZACAO_DESC'], 
        value_vars=list(mat_cols.keys()), 
        var_name='Variavel', 
        value_name='Total de Matrículas'
    )
    df_mat_local_long['Etapa de Ensino'] = df_mat_local_long['Variavel'].map(mat_cols)

    fig_local = px.bar(
        df_mat_local_long,
        x='Etapa de Ensino',
        y='Total de Matrículas',
        color='TP_LOCALIZACAO_DESC',
        barmode='group',
        title='Comparativo de Matrículas por Etapa e Localização',
        labels={'Total de Matrículas': 'Matrículas', 'TP_LOCALIZACAO_DESC': 'Localização'},
        color_discrete_sequence=[COLOR_PALETTE[0], COLOR_PALETTE[1]]
    )
    st.plotly_chart(fig_local, use_container_width=True)

    st.markdown("""
        **Interpretação:** Este comparativo destaca a diferença na demanda educacional entre áreas **Urbanas** e **Rurais**. 
        Em geral, as matrículas rurais são mais concentradas no Ensino Fundamental, refletindo a distribuição 
        populacional e a oferta de ensino.
    """)
    
    st.markdown("---")

    # 3. Oferta de Etapas por Dependência Administrativa
    st.subheader("Oferta de Etapas de Ensino por Rede (Contagem de Escolas)")
    
    etapa_cols = {
        'IN_INF': 'Infantil',
        'IN_FUND': 'Fundamental',
        'IN_MED': 'Médio',
        'IN_PROF': 'Profissional',
        'IN_EJA': 'EJA',
        'IN_ESP': 'Especial'
    }
    
    # Agrupamento por Dependência e Contagem de Escolas que Oferecem a Etapa (IN_* == 1)
    df_oferta = df.groupby('TP_DEPENDENCIA_DESC')[list(etapa_cols.keys())].sum().reset_index()
    
    # Transformar o DataFrame para o formato 'long'
    df_oferta_long = pd.melt(
        df_oferta, 
        id_vars=['TP_DEPENDENCIA_DESC'], 
        value_vars=list(etapa_cols.keys()), 
        var_name='Variavel', 
        value_name='Escolas que Oferecem'
    )
    df_oferta_long['Etapa de Ensino'] = df_oferta_long['Variavel'].map(etapa_cols)

    fig_oferta = px.bar(
        df_oferta_long,
        x='Etapa de Ensino',
        y='Escolas que Oferecem',
        color='TP_DEPENDENCIA_DESC',
        barmode='group',
        title='Número de Escolas que Oferecem Cada Etapa por Rede',
        labels={'Escolas que Oferecem': 'Nº de Escolas', 'TP_DEPENDENCIA_DESC': 'Rede de Ensino'},
        color_discrete_sequence=COLOR_PALETTE
    )
    st.plotly_chart(fig_oferta, use_container_width=True)

    st.markdown("""
        **Interpretação:** Este gráfico mostra a **responsabilidade de oferta** de cada etapa por rede de ensino. 
        Por exemplo, a Educação Infantil é predominantemente ofertada pela rede Municipal e Privada, 
        enquanto o Ensino Médio é majoritariamente Estadual e Privado.
    """)
