"""
Script para processar e preparar dados uma única vez.
Este script deve ser executado quando os dados CSV são atualizados.

Uso:
    python scripts/process_data.py
"""
import os
import sys
import pandas as pd

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.data_cache import load_data_once, clear_cache
from src.utils.data_processor import enrich_dataframe

def process_and_save_data():
    """
    Processa os dados do CSV, enriquece e salva em formato Parquet otimizado.
    """
    # Caminhos
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(script_dir, "data", "meu_arquivo.csv")
    parquet_path = os.path.join(script_dir, "data", "meu_arquivo_processed.parquet")
    
    print("=" * 60)
    print("PROCESSAMENTO DE DADOS")
    print("=" * 60)
    
    # Limpar cache para garantir dados atualizados
    clear_cache()
    
    # Carregar dados do CSV
    print(f"\n1. Carregando dados do CSV: {csv_path}")
    df = load_data_once(csv_path)
    
    if df.empty:
        print("ERRO: DataFrame vazio!")
        return
    
    print(f"   Dados carregados: {len(df):,} registros, {len(df.columns)} colunas")
    
    # Processar e enriquecer dados
    print(f"\n2. Processando e enriquecendo dados...")
    df_processed = enrich_dataframe(df)
    
    print(f"   Colunas adicionadas: is_padronizado, tipo_componente")
    if 'is_padronizado' in df_processed.columns:
        total_padronizados = df_processed['is_padronizado'].sum()
        total_registros = len(df_processed)
        print(f"   Campos padronizados: {total_padronizados:,} de {total_registros:,} ({total_padronizados/total_registros*100:.1f}%)")
        
        # Estatísticas de tipo de componente
        if 'tipo_componente' in df_processed.columns:
            tipos_unicos = df_processed['tipo_componente'].nunique()
            print(f"   Tipos de componentes únicos: {tipos_unicos}")
    
    # Salvar dados processados em Parquet
    print(f"\n3. Salvando dados processados: {parquet_path}")
    try:
        df_processed.to_parquet(parquet_path, compression='snappy', index=False)
        print(f"   ✓ Dados processados salvos com sucesso!")
        
        # Comparar tamanhos
        if os.path.exists(csv_path):
            csv_size = os.path.getsize(csv_path) / 1024 / 1024
            parquet_size = os.path.getsize(parquet_path) / 1024 / 1024
            print(f"   Tamanho original (CSV): {csv_size:.2f} MB")
            print(f"   Tamanho processado (Parquet): {parquet_size:.2f} MB")
            print(f"   Redução: {((csv_size - parquet_size) / csv_size * 100):.1f}%")
        
        # Memória do DataFrame
        memory_mb = df_processed.memory_usage(deep=True).sum() / 1024 / 1024
        print(f"   Memória do DataFrame: {memory_mb:.2f} MB")
    except Exception as e:
        print(f"   ✗ Erro ao salvar: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print(f"\nOs dados processados estão em: {parquet_path}")
    print("Agora os callbacks podem carregar dados já processados, muito mais rápido!")
    print("\nPróximos passos:")
    print("1. Os callbacks agora usarão dados processados automaticamente")
    print("2. Execute este script novamente quando o CSV for atualizado")

if __name__ == "__main__":
    process_and_save_data()

