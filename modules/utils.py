import pandas as pd

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

def map_localizacao(codigo):
    """Mapeia o código da Localização para o nome."""
    if codigo == 1:
        return 'Urbana'
    elif codigo == 2:
        return 'Rural'
    return 'Não Informado'

