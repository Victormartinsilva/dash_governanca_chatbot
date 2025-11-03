#!/usr/bin/env python
"""
Script para limpar o cache de dados do painel.
Execute este script para forçar a recarga dos dados com as novas configurações.
Após executar, reinicie o servidor do painel.
"""

from src.utils.data_cache import clear_cache, get_cache_info

def main():
    print("=" * 60)
    print("Limpando cache de dados do painel...")
    print("=" * 60)
    
    # Mostra informações do cache antes de limpar
    info_antes = get_cache_info()
    print(f"\nAntes da limpeza:")
    print(f"  - Arquivos em cache: {info_antes['data_files_cached']}")
    print(f"  - Uso de memória: {info_antes['total_memory_usage']:.2f} MB")
    
    # Limpa o cache
    clear_cache()
    
    # Verifica se foi limpo
    info_depois = get_cache_info()
    print(f"\nApós a limpeza:")
    print(f"  - Arquivos em cache: {info_depois['data_files_cached']}")
    print(f"  - Uso de memória: {info_depois['total_memory_usage']:.2f} MB")
    
    print("\n" + "=" * 60)
    print("[OK] Cache limpo com sucesso!")
    print("=" * 60)
    print("\n[IMPORTANTE] Reinicie o servidor do painel para aplicar as mudancas.")
    print("   Execute: python app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()

