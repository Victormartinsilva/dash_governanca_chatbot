import pandas as pd
import os
from src.utils.data_cache import load_data_once, get_metadata, get_filtered_data

def _clean_columns(df):
    df.columns = [c.strip().lstrip('\ufeff') for c in df.columns]
    return df

def load_metadata(path_csv):
    script_dir = os.path.dirname(__file__)
    abs_path_csv = os.path.join(script_dir, "..", "..", path_csv)
    """
    Carrega metadados do CSV usando o cache.
    """
    return get_metadata(abs_path_csv)

def stream_filtered_df(path_csv, ano=None, fluxo=None, servico=None, formulario=None):
    script_dir = os.path.dirname(__file__)
    abs_path_csv = os.path.join(script_dir, "..", "..", path_csv)
    """
    Obtém um DataFrame filtrado do cache. Não é mais um stream, mas retorna o DF completo filtrado.
    """
    return get_filtered_data(abs_path_csv, ano, fluxo, servico, formulario)

def quick_read(path_csv, nrows=None):
    script_dir = os.path.dirname(__file__)
    abs_path_csv = os.path.join(script_dir, "..", "..", path_csv)
    """
    Lê uma porção do CSV ou o CSV completo, utilizando o cache.
    Se nrows for None, lê o arquivo completo via cache.
    """
    df = load_data_once(abs_path_csv)
    if nrows:
        return df.head(nrows)
    return df

