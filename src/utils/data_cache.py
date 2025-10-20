import pandas as pd
import os
from typing import Dict, Any, Optional

# Cache global para dados
_data_cache = {}
_metadata_cache = {}

def load_data_once(csv_path: str) -> pd.DataFrame:
    """
    Carrega os dados do CSV uma única vez usando chunks e armazena em cache.
    
    Args:
        csv_path: Caminho para o arquivo CSV
        
    Returns:
        DataFrame com todos os dados
    """
    global _data_cache
    
    if csv_path not in _data_cache:
        print(f"Carregando dados do CSV: {csv_path}")
        try:
            if not os.path.exists(csv_path):
                print(f"Aviso: Arquivo CSV não encontrado em {csv_path}. Retornando DataFrame vazio.")
                _data_cache[csv_path] = pd.DataFrame()
                return _data_cache[csv_path]

            # Carrega dados em chunks para evitar problemas de memória
            chunk_size = 100000  # 100k registros por chunk
            chunks = []
            
            print("Carregando dados em chunks...")
            for i, chunk in enumerate(pd.read_csv(
                csv_path, 
                encoding='latin1', 
                sep=',', 
                parse_dates=['dataCriacao'],
                low_memory=False,
                dtype={'statusFluxo': 'category'},
                chunksize=chunk_size
            )):
                # Limpa colunas do chunk
                chunk.columns = [c.strip().lstrip('\ufeff') for c in chunk.columns]
                chunks.append(chunk)
                
                if (i + 1) % 10 == 0:  # Log a cada 1M registros
                    print(f"Chunk {i+1}: {len(chunk):,} registros processados")
            
            # Concatena todos os chunks
            df = pd.concat(chunks, ignore_index=True)
            
            # Armazena no cache
            _data_cache[csv_path] = df
            print(f"Dados carregados: {len(df):,} registros")
            
        except FileNotFoundError as e:
            print(f"Erro: Arquivo CSV não encontrado em {csv_path}. {e}")
            _data_cache[csv_path] = pd.DataFrame()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            _data_cache[csv_path] = pd.DataFrame()
    
    return _data_cache[csv_path]

def get_metadata(csv_path: str) -> Dict[str, Any]:
    """
    Obtém metadados dos dados (anos, fluxos, serviços, formulários).
    
    Args:
        csv_path: Caminho para o arquivo CSV
        
    Returns:
        Dicionário com metadados
    """
    global _metadata_cache
    
    if csv_path not in _metadata_cache:
        df = load_data_once(csv_path)
        
        if df.empty:
            return {"anos": [], "fluxos": [], "servicos": [], "formularios": []}
        
        # Extrai metadados
        anos = sorted(df['dataCriacao'].dt.year.dropna().unique().astype(int).tolist())
        fluxos = sorted(df['fluxo'].dropna().unique().astype(str).tolist())
        servicos = sorted(df['servico'].dropna().unique().astype(str).tolist())
        formularios = sorted(df['formulario'].dropna().unique().astype(str).tolist())
        
        _metadata_cache[csv_path] = {
            "anos": anos,
            "fluxos": fluxos,
            "servicos": servicos,
            "formularios": formularios
        }
        
        print(f"Metadados extraidos: {len(anos)} anos, {len(fluxos)} fluxos, {len(servicos)} servicos, {len(formularios)} formularios")
    
    return _metadata_cache[csv_path]

def get_filtered_data(csv_path: str, ano: Optional[str] = None, fluxo: Optional[str] = None, 
                     servico: Optional[str] = None, formulario: Optional[str] = None) -> pd.DataFrame:
    """
    Obtém dados filtrados do cache.
    
    Args:
        csv_path: Caminho para o arquivo CSV
        ano: Filtro por ano
        fluxo: Filtro por fluxo
        servico: Filtro por serviço
        formulario: Filtro por formulário
        
    Returns:
        DataFrame filtrado
    """
    df = load_data_once(csv_path)
    
    if df.empty:
        return df
    
    # Aplica filtros
    filtered_df = df.copy()
    
    if ano and 'dataCriacao' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['dataCriacao'].dt.year == int(ano)]
    
    if fluxo and 'fluxo' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['fluxo'] == fluxo]
    
    if servico and 'servico' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['servico'] == servico]
    
    if formulario and 'formulario' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['formulario'] == formulario]
    
    return filtered_df

def get_filtered_data_safe(csv_path: str, ano: Optional[str] = None, fluxo: Optional[str] = None, 
                          servico: Optional[str] = None, formulario: Optional[str] = None, 
                          max_rows: int = 50000) -> pd.DataFrame:
    """
    Obtém dados filtrados com limite de linhas para evitar problemas de memória.
    
    Args:
        csv_path: Caminho para o arquivo CSV
        ano: Filtro por ano
        fluxo: Filtro por fluxo
        servico: Filtro por serviço
        formulario: Filtro por formulário
        max_rows: Número máximo de linhas a retornar
        
    Returns:
        DataFrame filtrado limitado
    """
    df = get_filtered_data(csv_path, ano, fluxo, servico, formulario)
    
    if len(df) > max_rows:
        print(f"Limitando dados a {max_rows:,} registros de {len(df):,} disponíveis")
        df = df.sample(n=max_rows, random_state=42)
    
    return df

def get_sampled_data_for_charts(csv_path: str, ano: Optional[str] = None, fluxo: Optional[str] = None, 
                               servico: Optional[str] = None, formulario: Optional[str] = None, 
                               sample_size: int = 100000) -> pd.DataFrame:
    """
    Obtém uma amostra representativa dos dados para uso em gráficos.
    
    Args:
        csv_path: Caminho para o arquivo CSV
        ano: Filtro por ano
        fluxo: Filtro por fluxo
        servico: Filtro por serviço
        formulario: Filtro por formulário
        sample_size: Tamanho da amostra
        
    Returns:
        DataFrame amostrado
    """
    df = get_filtered_data(csv_path, ano, fluxo, servico, formulario)
    
    if len(df) > sample_size:
        # Amostragem estratificada para manter representatividade
        print(f"Amostrando {sample_size:,} registros de {len(df):,} para gráficos")
        
        # Se há muitos dados, faz amostragem estratificada por ano
        if 'dataCriacao' in df.columns and len(df) > sample_size * 2:
            df['ano'] = df['dataCriacao'].dt.year
            sample_per_ano = sample_size // len(df['ano'].unique())
            sampled_df = df.groupby('ano').apply(
                lambda x: x.sample(min(len(x), sample_per_ano), random_state=42)
            ).reset_index(drop=True)
            
            # Se ainda precisar de mais dados, adiciona aleatoriamente
            if len(sampled_df) < sample_size:
                remaining = sample_size - len(sampled_df)
                additional = df.sample(n=min(remaining, len(df)), random_state=42)
                sampled_df = pd.concat([sampled_df, additional], ignore_index=True)
            
            return sampled_df.sample(n=min(sample_size, len(sampled_df)), random_state=42)
        else:
            return df.sample(n=sample_size, random_state=42)
    
    return df

def clear_cache():
    """Limpa o cache de dados."""
    global _data_cache, _metadata_cache
    _data_cache.clear()
    _metadata_cache.clear()
    print("Cache limpo")

def get_cache_info() -> Dict[str, Any]:
    """Retorna informações sobre o cache."""
    return {
        "data_files_cached": len(_data_cache),
        "metadata_files_cached": len(_metadata_cache),
        "total_memory_usage": sum(df.memory_usage(deep=True).sum() for df in _data_cache.values()) / 1024 / 1024  # MB
    }
