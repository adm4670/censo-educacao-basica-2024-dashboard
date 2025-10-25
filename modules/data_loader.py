import pandas as pd
import streamlit as st

@st.cache_data
def map_dependencia(codigo):
    """Mapeia o código da Dependência Administrativa para o nome."""
    if codigo == 1:
        return 'Federal'
    elif codigo == 2:
        return 'Estadual'
    elif codigo == 3:
        return 'Municipal'
    elif codigo == 4:
        return 'Privada'
    return 'Não Informado'

@st.cache_data
def map_localizacao(codigo):
    """Mapeia o código da Localização para o nome."""
    if codigo == 1:
        return 'Urbana'
    elif codigo == 2:
        return 'Rural'
    return 'Não Informado'

@st.cache_data
def load_data():
    """Carrega e pré-processa os microdados do Censo Escolar."""
    try:
        df = pd.read_csv('microdados_processados.csv')
    except FileNotFoundError:
        st.error("Arquivo 'microdados_processados.csv' não encontrado. Certifique-se de que a fase de análise de dados foi concluída.")
        return pd.DataFrame()

    colunas_quantidades = [col for col in df.columns if col.startswith('QT_')]
    for col in colunas_quantidades:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    colunas_binarias = [col for col in df.columns if col.startswith('IN_')]
    for col in colunas_binarias:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    df['TP_DEPENDENCIA_DESC'] = df['TP_DEPENDENCIA'].apply(map_dependencia)
    df['TP_LOCALIZACAO_DESC'] = df['TP_LOCALIZACAO'].apply(map_localizacao)
    
    def get_etapas_ofertadas(row):
        etapas = []
        if row['IN_INF'] == 1: etapas.append('Infantil')
        if row['IN_FUND'] == 1: etapas.append('Fundamental')
        if row['IN_MED'] == 1: etapas.append('Médio')
        if row['IN_PROF'] == 1: etapas.append('Profissional')
        if row['IN_EJA'] == 1: etapas.append('EJA')
        if row['IN_ESP'] == 1: etapas.append('Especial')
        return ', '.join(etapas)

    df['ETAPAS_OFERTADAS'] = df.apply(get_etapas_ofertadas, axis=1)

    df['NU_ESCOLAS'] = 1
    
    return df

