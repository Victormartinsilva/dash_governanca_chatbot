"""
Script para verificar se todas as mudanças foram aplicadas corretamente.
"""
import sys
import os

print("=" * 60)
print("VERIFICAÇÃO DE MUDANÇAS")
print("=" * 60)

# 1. Verificar se a página Biblioteca existe
print("\n1. Verificando página Biblioteca...")
try:
    from src.pages.biblioteca import biblioteca_layout
    layout = biblioteca_layout()
    print("   ✓ Página Biblioteca criada com sucesso")
except Exception as e:
    print(f"   ✗ Erro ao criar página Biblioteca: {e}")
    sys.exit(1)

# 2. Verificar se os callbacks da Biblioteca existem
print("\n2. Verificando callbacks da Biblioteca...")
try:
    from src.callbacks.biblioteca_callbacks import register_callbacks
    print("   ✓ Callbacks da Biblioteca importados com sucesso")
except Exception as e:
    print(f"   ✗ Erro ao importar callbacks da Biblioteca: {e}")
    sys.exit(1)

# 3. Verificar se a aba Biblioteca está no layout
print("\n3. Verificando aba Biblioteca no layout...")
try:
    from src.layouts.main_layout import create_layout
    from src.utils.data_loader import load_metadata
    
    meta = load_metadata("data/meu_arquivo.csv")
    layout = create_layout(meta)
    
    # Verificar se há 5 abas (incluindo Biblioteca)
    layout_str = str(layout)
    if "biblioteca" in layout_str.lower() or "📚" in layout_str:
        print("   ✓ Aba Biblioteca encontrada no layout")
    else:
        print("   ✗ Aba Biblioteca NÃO encontrada no layout")
except Exception as e:
    print(f"   ✗ Erro ao verificar layout: {e}")
    sys.exit(1)

# 4. Verificar se os callbacks estão registrados
print("\n4. Verificando registro de callbacks...")
try:
    from dash import Dash
    from src.callbacks import register_all
    
    app = Dash(__name__)
    register_all(app)
    print("   ✓ Todos os callbacks registrados com sucesso")
except Exception as e:
    print(f"   ✗ Erro ao registrar callbacks: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. Verificar se o gráfico foi removido da página Fluxos
print("\n5. Verificando página Fluxos...")
try:
    from src.pages.fluxos import fluxos_layout
    fluxos_layout_str = str(fluxos_layout())
    
    if "fluxos-hierarquia-tree" not in fluxos_layout_str:
        print("   ✓ Gráfico de hierarquia removido da página Fluxos")
    else:
        print("   ✗ Gráfico de hierarquia AINDA está na página Fluxos")
    
    if "padronizacao-por-fluxo-tabela" in fluxos_layout_str:
        print("   ✓ Outros componentes da página Fluxos presentes")
except Exception as e:
    print(f"   ✗ Erro ao verificar página Fluxos: {e}")

print("\n" + "=" * 60)
print("VERIFICAÇÃO CONCLUÍDA!")
print("=" * 60)
print("\nPRÓXIMOS PASSOS:")
print("1. PARAR o servidor atual (Ctrl+C no terminal onde está rodando)")
print("2. REINICIAR o servidor: python app.py")
print("3. LIMPAR o cache do navegador (Ctrl+Shift+Delete ou F5 forçado)")
print("4. Verificar se a aba 'Biblioteca' aparece no menu")
print("\nSe ainda não funcionar após reiniciar, verifique o console do navegador (F12) para erros.")

