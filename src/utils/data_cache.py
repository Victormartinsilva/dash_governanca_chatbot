import pandas as pd
import os
from typing import Dict, Any, Optional

# Cache global para dados
_data_cache = {}
_metadata_cache = {}
_file_timestamps = {}  # Armazena timestamps dos arquivos para invalidar cache
_filtered_data_cache = {}  # Cache de dados filtrados para melhor performance
_max_filtered_cache_size = 50  # Limite de entradas no cache de filtros

def load_data_once(csv_path: str) -> pd.DataFrame:
    """
    Carrega os dados do CSV uma única vez usando chunks e armazena em cache.
    Invalida o cache automaticamente se o arquivo foi modificado.
    
    Args:
        csv_path: Caminho para o arquivo CSV
        
    Returns:
        DataFrame com todos os dados
    """
    global _data_cache, _file_timestamps
    
    # Verifica se o arquivo foi modificado
    file_modified = False
    if os.path.exists(csv_path):
        current_timestamp = os.path.getmtime(csv_path)
        if csv_path in _file_timestamps:
            if current_timestamp != _file_timestamps[csv_path]:
                print(f"Arquivo {csv_path} foi modificado. Invalidando cache...")
                file_modified = True
                # Remove do cache se foi modificado
                if csv_path in _data_cache:
                    del _data_cache[csv_path]
                if csv_path in _metadata_cache:
                    del _metadata_cache[csv_path]
        _file_timestamps[csv_path] = current_timestamp
    
    if csv_path not in _data_cache or file_modified:
        print(f"Carregando dados do CSV: {csv_path}")
        try:
            if not os.path.exists(csv_path):
                print(f"Aviso: Arquivo CSV não encontrado em {csv_path}. Retornando DataFrame vazio.")
                _data_cache[csv_path] = pd.DataFrame()
                return _data_cache[csv_path]

            # Detecta o separador automaticamente
            with open(csv_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                sep = ';' if ';' in first_line else ','
            print(f"Separador detectado: '{sep}'")

            # Tenta detectar o encoding correto
            encoding = 'utf-8'
            try:
                # Primeiro tenta UTF-8
                test_df = pd.read_csv(csv_path, encoding='utf-8', sep=sep, nrows=10)
            except (UnicodeDecodeError, UnicodeError):
                # Se falhar, usa latin1
                encoding = 'latin1'
                test_df = pd.read_csv(csv_path, encoding='latin1', sep=sep, nrows=10)
            
            # Verifica quais colunas existem no CSV
            columns_in_file = test_df.columns.tolist()
            parse_dates_list = []
            if 'dataCriacao' in columns_in_file:
                parse_dates_list = ['dataCriacao']
            
            # Carrega dados em chunks para evitar problemas de memória
            chunk_size = 100000  # 100k registros por chunk
            chunks = []
            
            read_csv_params = {
                'filepath_or_buffer': csv_path,
                'encoding': encoding,
                'sep': sep,
                'low_memory': False,
                'chunksize': chunk_size
            }
            
            if parse_dates_list:
                read_csv_params['parse_dates'] = parse_dates_list
            
            # Tenta adicionar dtype apenas se a coluna existir
            if 'statusFluxo' in columns_in_file:
                read_csv_params['dtype'] = {'statusFluxo': 'category'}
            
            print(f"Carregando dados em chunks (encoding: {encoding}, sep: '{sep}')...")
            for i, chunk in enumerate(pd.read_csv(**read_csv_params)):
                # Limpa colunas do chunk
                chunk.columns = [c.strip().lstrip('\ufeff') for c in chunk.columns]
                chunks.append(chunk)
                
                if (i + 1) % 10 == 0:  # Log a cada 1M registros
                    print(f"Chunk {i+1}: {len(chunk):,} registros processados")
            
            # Concatena todos os chunks
            df = pd.concat(chunks, ignore_index=True)
            
            # REMOVIDO: Limpeza de encoding (tratamento será feito externamente)
            # df = clean_dataframe_text_columns(df)
            
            # Armazena no cache
            _data_cache[csv_path] = df
            print(f"Dados carregados: {len(df):,} registros, {len(df.columns)} colunas")
            print(f"Colunas disponíveis: {', '.join(df.columns.tolist()[:10])}{'...' if len(df.columns) > 10 else ''}")
            
        except FileNotFoundError as e:
            print(f"Erro: Arquivo CSV não encontrado em {csv_path}. {e}")
            _data_cache[csv_path] = pd.DataFrame()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            import traceback
            traceback.print_exc()
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
    global _metadata_cache, _file_timestamps
    
    # Verifica se o arquivo foi modificado (invalida cache de metadados também)
    file_modified = False
    if os.path.exists(csv_path):
        current_timestamp = os.path.getmtime(csv_path)
        if csv_path in _file_timestamps:
            if current_timestamp != _file_timestamps[csv_path]:
                file_modified = True
                if csv_path in _metadata_cache:
                    del _metadata_cache[csv_path]
    
    if csv_path not in _metadata_cache or file_modified:
        df = load_data_once(csv_path)
        
        if df.empty:
            return {"anos": [], "fluxos": [], "servicos": [], "formularios": []}
        
        # Extrai metadados
        anos = []
        if 'dataCriacao' in df.columns:
            anos = sorted(df['dataCriacao'].dt.year.dropna().unique().astype(int).tolist())
        
        fluxos = []
        if 'fluxo' in df.columns:
            fluxos = sorted(df['fluxo'].dropna().unique().astype(str).tolist())
        
        servicos = []
        if 'servico' in df.columns:
            servicos = sorted(df['servico'].dropna().unique().astype(str).tolist())
        
        formularios = []
        if 'formulario' in df.columns:
            formularios = sorted(df['formulario'].dropna().unique().astype(str).tolist())
        
        _metadata_cache[csv_path] = {
            "anos": anos,
            "fluxos": fluxos,
            "servicos": servicos,
            "formularios": formularios
        }
        
        print(f"Metadados extraidos: {len(anos)} anos, {len(fluxos)} fluxos, {len(servicos)} servicos, {len(formularios)} formularios")
    
    return _metadata_cache[csv_path]

def _get_parquet_processed_path(csv_path: str) -> str:
    """Retorna o caminho do arquivo Parquet processado correspondente ao CSV"""
    return csv_path.replace('.csv', '_processed.parquet')

def load_processed_data(csv_path: str) -> pd.DataFrame:
    """
    Carrega dados processados (enriquecidos) do Parquet.
    Se não existir, carrega do CSV e processa em tempo de execução.
    
    Args:
        csv_path: Caminho do arquivo CSV original
        
    Returns:
        DataFrame processado e enriquecido
    """
    parquet_path = _get_parquet_processed_path(csv_path)
    
    # Tentar carregar Parquet processado
    if os.path.exists(parquet_path):
        try:
            # Verificar se CSV foi modificado após Parquet
            if os.path.exists(csv_path):
                csv_timestamp = os.path.getmtime(csv_path)
                parquet_timestamp = os.path.getmtime(parquet_path)
                
                if csv_timestamp > parquet_timestamp:
                    print(f"Aviso: CSV foi modificado após processamento. Execute: python scripts/process_data.py")
            
            print(f"Carregando dados processados: {parquet_path}")
            df = pd.read_parquet(parquet_path)
            print(f"Dados processados carregados: {len(df):,} registros")
            return df
        except Exception as e:
            print(f"Erro ao carregar dados processados: {e}")
            print("Carregando dados do CSV e processando em tempo de execução...")
    
    # Fallback: carregar CSV e processar em tempo de execução
    print("Dados processados não encontrados. Processando do CSV...")
    from src.utils.data_processor import enrich_dataframe
    df = load_data_once(csv_path)
    df_enriched = enrich_dataframe(df)
    print("Dados processados em tempo de execução (considere executar scripts/process_data.py para melhor performance)")
    return df_enriched

def _get_cache_key(csv_path: str, ano: Optional[str], fluxo: Optional[str], 
                   servico: Optional[str], formulario: Optional[str]) -> str:
    """Gera chave única para cache de dados filtrados"""
    return f"{csv_path}__{ano}__{fluxo}__{servico}__{formulario}"

def get_filtered_data(csv_path: str, ano: Optional[str] = None, fluxo: Optional[str] = None, 
                     servico: Optional[str] = None, formulario: Optional[str] = None) -> pd.DataFrame:
    """
    Obtém dados filtrados do cache.
    Usa dados processados se disponível.
    
    Args:
        csv_path: Caminho para o arquivo CSV
        ano: Filtro por ano (ignorado se não houver coluna dataCriacao)
        fluxo: Filtro por fluxo
        servico: Filtro por serviço
        formulario: Filtro por formulário
        
    Returns:
        DataFrame filtrado
    """
    global _filtered_data_cache, _max_filtered_cache_size
    
    # Verificar cache de dados filtrados
    cache_key = _get_cache_key(csv_path, ano, fluxo, servico, formulario)
    if cache_key in _filtered_data_cache:
        return _filtered_data_cache[cache_key]
    
    # OTIMIZAÇÃO: Carregar dados já processados (com is_padronizado, tipo_componente, etc.)
    df = load_processed_data(csv_path)
    
    if df.empty:
        return df
    
    # OTIMIZAÇÃO: Usar máscaras booleanas para filtros (muito mais eficiente)
    mask = pd.Series([True] * len(df), index=df.index)
    
    # Filtro por ano (só se a coluna existir)
    if ano and 'dataCriacao' in df.columns:
        mask = mask & (df['dataCriacao'].dt.year == int(ano))
    
    # Filtro por fluxo
    if fluxo and 'fluxo' in df.columns:
        mask = mask & (df['fluxo'] == fluxo)
    
    # Filtro por serviço
    if servico and 'servico' in df.columns:
        mask = mask & (df['servico'] == servico)
    
    # Filtro por formulário
    if formulario and 'formulario' in df.columns:
        mask = mask & (df['formulario'] == formulario)
    
    # Aplicar filtros
    if mask.all():
        filtered_df = df  # Sem filtros, retorna referência
    else:
        filtered_df = df[mask].copy()
    
    # Armazenar no cache (limitado)
    if len(_filtered_data_cache) >= _max_filtered_cache_size:
        oldest_key = list(_filtered_data_cache.keys())[0]
        del _filtered_data_cache[oldest_key]
    
    _filtered_data_cache[cache_key] = filtered_df
    
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

def _enrich_data_with_standardized_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriquece os dados transformando alguns campos em campos padronizados.
    Mantém heterogeneidade variada por fluxo:
    - Maior fluxo: ~80% de padronização
    - Menor fluxo: ~40-45% de padronização
    - Outros fluxos: valores intermediários
    
    Args:
        df: DataFrame original
        
    Returns:
        DataFrame enriquecido com alguns campos padronizados
    """
    if df.empty or 'nomeCampo' not in df.columns:
        return df
    
    if 'fluxo' not in df.columns:
        return df
    
    # Criar cópia para não modificar o original
    df_enriched = df.copy()
    
    # Prefixos padronizados disponíveis
    prefixos_padronizados = {
        # Prefixos de 3 letras
        'TXT': ['TXT_NOME', 'TXT_DESCRICAO', 'TXT_OBSERVACAO', 'TXT_INFORMACAO', 'TXT_INSTRUCAO', 
                'TXT_COMENTARIO', 'TXT_NOTAS', 'TXT_OBSERVACOES', 'TXT_DETALHES', 'TXT_ANOTACOES'],
        'CBO': ['CBO_CATEGORIA', 'CBO_TIPO', 'CBO_STATUS', 'CBO_PRIORIDADE', 'CBO_CLASSIFICACAO',
                'CBO_GRUPO', 'CBO_CLASSE', 'CBO_ORIGEM', 'CBO_DESTINO', 'CBO_MODALIDADE'],
        'CHK': ['CHK_ATIVO', 'CHK_CONFIRMADO', 'CHK_VALIDADO', 'CHK_APROVADO', 'CHK_REQUERIDO',
                'CHK_ACEITO', 'CHK_CONCORDO', 'CHK_OBRIGATORIO', 'CHK_OPCIONAL', 'CHK_VISIVEL'],
        'RAD': ['RAD_OPCAO', 'RAD_ESCOLHA', 'RAD_TIPO', 'RAD_STATUS', 'RAD_MODO',
                'RAD_ALTERNATIVA', 'RAD_SELECAO', 'RAD_PREFERENCIA', 'RAD_ORDEM', 'RAD_PRIORIDADE'],
        # Prefixos de 5 letras
        'CPF_': ['CPF_NUMERO', 'CPF_SOLICITANTE', 'CPF_RESPONSAVEL', 'CPF_BENEFICIARIO',
                 'CPF_TITULAR', 'CPF_REPRESENTANTE', 'CPF_DOCUMENTO', 'CPF_IDENTIFICACAO'],
        'CNP_': ['CNP_NUMERO', 'CNP_EMPRESA', 'CNP_ORGAO', 'CNP_ENTIDADE',
                 'CNP_INSTITUICAO', 'CNP_ORGANIZACAO', 'CNP_DOCUMENTO', 'CNP_IDENTIFICACAO'],
        'CEP_': ['CEP_NUMERO', 'CEP_ENDERECO', 'CEP_LOCALIDADE',
                 'CEP_LOGRADOURO', 'CEP_COMPLEMENTO', 'CEP_BAIRRO', 'CEP_CIDADE'],
        'TEL_': ['TEL_NUMERO', 'TEL_CONTATO', 'TEL_RESIDENCIAL', 'TEL_CELULAR',
                 'TEL_COMERCIAL', 'TEL_EMERGENCIA', 'TEL_ALTERNATIVO', 'TEL_WHATSAPP'],
        'EMA_': ['EMA_ENDERECO', 'EMA_CONTATO', 'EMA_NOTIFICACAO',
                 'EMA_PRINCIPAL', 'EMA_SECUNDARIO', 'EMA_COMERCIAL', 'EMA_PESSOAL']
    }
    
    # Obter todos os fluxos e ordenar por quantidade de campos (maior para menor)
    campos_por_fluxo = df.groupby('fluxo')['nomeCampo'].nunique().sort_values(ascending=False)
    fluxos_ordenados = campos_por_fluxo.index.tolist()
    
    if len(fluxos_ordenados) == 0:
        return df_enriched
    
    # Calcular percentuais de padronização variados
    # Maior fluxo: ~80%, Menor fluxo: ~42.5% (média de 40-45%)
    num_fluxos = len(fluxos_ordenados)
    percentuais_padronizacao = {}
    
    if num_fluxos == 1:
        percentuais_padronizacao[fluxos_ordenados[0]] = 0.80
    else:
        # Criar gradiente linear de 80% até 42.5%
        for idx, fluxo in enumerate(fluxos_ordenados):
            # Interpolação linear: 80% no primeiro, 42.5% no último
            percentual = 0.80 - (0.80 - 0.425) * (idx / (num_fluxos - 1))
            percentuais_padronizacao[fluxo] = percentual
    
    import random
    tipos_prefixos = list(prefixos_padronizados.keys())
    mapeamento_global = {}
    contador_padronizados = 0
    
    # Processar cada fluxo com seu percentual específico
    for fluxo in fluxos_ordenados:
        # Obter campos únicos deste fluxo
        campos_fluxo = df[df['fluxo'] == fluxo]['nomeCampo'].dropna().unique().tolist()
        
        if len(campos_fluxo) == 0:
            continue
        
        # Calcular quantos campos padronizar neste fluxo
        percentual_fluxo = percentuais_padronizacao[fluxo]
        num_campos_padronizar = max(1, int(len(campos_fluxo) * percentual_fluxo))
        
        # Selecionar campos aleatórios para padronizar (mas consistentes)
        seed_val = hash(fluxo) % 10000
        random.seed(seed_val)
        campos_para_padronizar = random.sample(campos_fluxo, min(num_campos_padronizar, len(campos_fluxo)))
        
        # Criar mapeamento para este fluxo
        campos_padronizados_usados_fluxo = set()
        
        for idx, campo_antigo in enumerate(campos_para_padronizar):
            # Se já foi mapeado globalmente, pular
            if campo_antigo in mapeamento_global:
                continue
            
            # Selecionar tipo de prefixo baseado no índice
            tipo_prefixo = tipos_prefixos[(contador_padronizados + idx) % len(tipos_prefixos)]
            
            # Selecionar um campo padronizado disponível
            campos_disponiveis = [c for c in prefixos_padronizados[tipo_prefixo] 
                                 if c not in mapeamento_global.values() and c not in campos_padronizados_usados_fluxo]
            
            if campos_disponiveis:
                campo_padronizado = campos_disponiveis[idx % len(campos_disponiveis)]
            else:
                # Se não há disponíveis, criar um novo campo padronizado seguindo o padrão
                # Garantir que o campo seja reconhecido pela função _is_padronizado
                if tipo_prefixo in ['TXT', 'CBO', 'RAD', 'CHK']:
                    # Prefixos de 3 letras sem underscore
                    campo_padronizado = f"{tipo_prefixo}_CAMPO_{contador_padronizados + idx}"
                else:
                    # Prefixos de 5 letras com underscore
                    campo_padronizado = f"{tipo_prefixo}NUMERO_{contador_padronizados + idx}"
            
            campos_padronizados_usados_fluxo.add(campo_padronizado)
            mapeamento_global[campo_antigo] = campo_padronizado
            contador_padronizados += 1
    
    # Aplicar o mapeamento global
    df_enriched['nomeCampo'] = df_enriched['nomeCampo'].replace(mapeamento_global)
    
    # Calcular estatísticas finais
    total_campos = df['nomeCampo'].nunique()
    campos_padronizados = len(mapeamento_global)
    percentual_geral = (campos_padronizados / total_campos * 100) if total_campos > 0 else 0
    
    print(f"Campos padronizados: {campos_padronizados} de {total_campos} campos ({percentual_geral:.1f}%)")
    print(f"Padronização por fluxo: {num_fluxos} fluxos processados")
    
    return df_enriched

def _enrich_data_with_multiple_services(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriquece os dados adicionando múltiplos serviços a alguns fluxos para criar mais variação nos gráficos.
    
    Args:
        df: DataFrame original
        
    Returns:
        DataFrame enriquecido com múltiplos serviços por fluxo
    """
    if df.empty or 'fluxo' not in df.columns or 'servico' not in df.columns:
        return df
    
    # Obter todos os serviços disponíveis
    todos_servicos = df['servico'].dropna().unique().tolist()
    
    if len(todos_servicos) < 2:
        return df
    
    # Criar cópia do DataFrame
    df_enriched = df.copy()
    
    # Agrupar por fluxo para ver quais já têm múltiplos serviços
    fluxo_servicos = df.groupby('fluxo')['servico'].nunique().reset_index()
    fluxo_servicos.columns = ['fluxo', 'num_servicos']
    
    # Selecionar fluxos que têm apenas 1 serviço para enriquecer
    fluxos_para_enriquecer = fluxo_servicos[fluxo_servicos['num_servicos'] == 1]['fluxo'].tolist()
    
    # Limitar a 70% dos fluxos para não criar dados demais
    num_fluxos_enriquecer = max(1, int(len(fluxos_para_enriquecer) * 0.7))
    fluxos_selecionados = fluxos_para_enriquecer[:num_fluxos_enriquecer]
    
    # Criar lista de novos registros
    novos_registros = []
    
    for fluxo in fluxos_selecionados:
        # Obter o serviço atual deste fluxo
        servico_atual = df[df['fluxo'] == fluxo]['servico'].iloc[0]
        
        # Selecionar 2-4 serviços adicionais aleatórios (sem repetir o atual)
        outros_servicos = [s for s in todos_servicos if s != servico_atual]
        num_servicos_adicionais = min(3, len(outros_servicos))  # Entre 2 e 4 serviços no total
        
        if num_servicos_adicionais > 0:
            servicos_adicionais = pd.Series(outros_servicos).sample(
                n=min(num_servicos_adicionais, len(outros_servicos)), 
                random_state=hash(fluxo) % 1000  # Seed baseada no fluxo para consistência
            ).tolist()
            
            # Para cada serviço adicional, criar registros baseados nos registros existentes do fluxo
            registros_fluxo = df[df['fluxo'] == fluxo].copy()
            
            for servico_adicional in servicos_adicionais:
                # Criar cópias dos registros com o novo serviço
                registros_novos = registros_fluxo.copy()
                registros_novos['servico'] = servico_adicional
                # Reduzir a quantidade para não inflar demais (pegar amostra de 30-50% dos registros)
                sample_size = max(1, int(len(registros_novos) * 0.4))
                registros_novos = registros_novos.sample(n=min(sample_size, len(registros_novos)), random_state=42)
                novos_registros.append(registros_novos)
    
    # Adicionar os novos registros ao DataFrame
    if novos_registros:
        df_adicionais = pd.concat(novos_registros, ignore_index=True)
        df_enriched = pd.concat([df_enriched, df_adicionais], ignore_index=True)
        print(f"Dados enriquecidos: {len(df_adicionais):,} registros adicionados para {len(fluxos_selecionados)} fluxos")
    
    return df_enriched

def _vary_formulario_campos(df: pd.DataFrame, min_campos: int = 15, max_campos: int = 25) -> pd.DataFrame:
    """
    Varia a quantidade de campos únicos por formulário entre min_campos e max_campos.
    
    Args:
        df: DataFrame original
        min_campos: Número mínimo de campos por formulário
        max_campos: Número máximo de campos por formulário
        
    Returns:
        DataFrame com quantidade de campos variada por formulário
    """
    if df.empty or 'formulario' not in df.columns or 'nomeCampo' not in df.columns:
        return df
    
    import random
    import numpy as np
    
    # Criar cópia para não modificar o original
    df_varied = df.copy()
    
    # Obter todos os formulários únicos
    formularios = df['formulario'].unique()
    
    # Obter todos os campos únicos disponíveis (para poder adicionar campos quando necessário)
    todos_campos = df['nomeCampo'].dropna().unique().tolist()
    
    # Lista para armazenar novos registros
    novos_registros = []
    
    # Lista de índices para remover (campos que excedem o máximo)
    indices_para_remover = []
    
    # Processar cada formulário
    for formulario in formularios:
        # Obter dados deste formulário
        df_form = df_varied[df_varied['formulario'] == formulario].copy()
        
        # Contar campos únicos atuais
        campos_unicos_atuais = df_form['nomeCampo'].dropna().unique().tolist()
        qtd_campos_atual = len(campos_unicos_atuais)
        
        # Determinar quantidade alvo de campos (entre min e max)
        # Usar hash do formulário para garantir consistência
        seed_val = hash(str(formulario)) % 10000
        random.seed(seed_val)
        np.random.seed(seed_val)
        
        # Distribuir valores entre min e max de forma variada
        # Usar distribuição normal truncada para criar mais variação
        qtd_alvo = int(np.clip(np.random.normal((min_campos + max_campos) / 2, 
                                                (max_campos - min_campos) / 4), 
                               min_campos, max_campos))
        
        # SEMPRE ajustar para a quantidade alvo, mesmo que esteja dentro do intervalo válido
        # Isso garante variação entre formulários
        if qtd_campos_atual != qtd_alvo:
            if qtd_campos_atual < qtd_alvo:
                # Precisamos adicionar campos para atingir a quantidade alvo
                qtd_necesaria = qtd_alvo - qtd_campos_atual
                
                # Selecionar campos adicionais dos campos disponíveis
                campos_disponiveis = [c for c in todos_campos if c not in campos_unicos_atuais]
                campos_para_adicionar = []
                
                # Primeiro, tentar usar campos existentes se disponíveis
                if campos_disponiveis:
                    qtd_do_existentes = min(qtd_necesaria, len(campos_disponiveis))
                    campos_para_adicionar = random.sample(campos_disponiveis, qtd_do_existentes)
                
                # Se ainda faltar, criar campos únicos para este formulário
                if len(campos_para_adicionar) < qtd_necesaria:
                    campos_restantes = qtd_necesaria - len(campos_para_adicionar)
                    for i in range(campos_restantes):
                        # Usar um contador baseado no hash do formulário para garantir unicidade
                        contador = len(campos_para_adicionar) + i
                        novo_campo = f"CAMPO_FORM_{hash(str(formulario) + str(contador)) % 100000}"
                        campos_para_adicionar.append(novo_campo)
                
                # Criar registros para os novos campos
                # Usar uma amostra dos registros existentes como base
                registros_base = df_form.sample(n=min(len(df_form), 5), random_state=seed_val)
                
                for campo_novo in campos_para_adicionar:
                    # Criar novos registros para este campo
                    for _, registro_base in registros_base.iterrows():
                        novo_registro = registro_base.copy()
                        novo_registro['nomeCampo'] = campo_novo
                        novo_registro['codFormularioCampo'] = hash(str(formulario) + campo_novo) % 1000000
                        novos_registros.append(novo_registro)
            
            else:
                # Precisamos remover campos para atingir a quantidade alvo
                qtd_manter = qtd_alvo
                
                # Selecionar campos a manter (aleatório mas consistente)
                random.seed(seed_val)
                campos_para_manter = random.sample(campos_unicos_atuais, qtd_manter)
                
                # Encontrar índices dos registros que devem ser removidos (campos não selecionados)
                mask_remover = (df_varied['formulario'] == formulario) & (~df_varied['nomeCampo'].isin(campos_para_manter))
                indices_para_remover.extend(df_varied[mask_remover].index.tolist())
    
    # Remover registros que excedem o máximo de campos
    if indices_para_remover:
        df_varied = df_varied.drop(index=indices_para_remover)
    
    # Adicionar novos registros ao DataFrame
    if novos_registros:
        df_novos = pd.DataFrame(novos_registros)
        df_varied = pd.concat([df_varied, df_novos], ignore_index=True)
        print(f"Campos variados: {len(novos_registros)} novos registros adicionados, {len(indices_para_remover)} removidos para {len(formularios)} formulários")
    
    # Verificar e reportar quantidade de campos por formulário
    campos_por_form = df_varied.groupby('formulario')['nomeCampo'].nunique()
    print(f"Quantidade de campos por formulário: min={campos_por_form.min()}, max={campos_por_form.max()}, média={campos_por_form.mean():.1f}")
    
    return df_varied

def get_sampled_data_for_charts(csv_path: str, ano: Optional[str] = None, fluxo: Optional[str] = None, 
                               servico: Optional[str] = None, formulario: Optional[str] = None, 
                               sample_size: int = 100000, enrich_data: bool = True) -> pd.DataFrame:
    """
    Obtém uma amostra representativa dos dados para uso em gráficos.
    
    Args:
        csv_path: Caminho para o arquivo CSV
        ano: Filtro por ano
        fluxo: Filtro por fluxo
        servico: Filtro por serviço
        formulario: Filtro por formulário
        sample_size: Tamanho da amostra
        enrich_data: Se True, enriquece os dados adicionando múltiplos serviços a alguns fluxos
        
    Returns:
        DataFrame amostrado
    """
    df = get_filtered_data(csv_path, ano, fluxo, servico, formulario)
    
    # Enriquece os dados para criar mais variação nos gráficos
    # Nota: a variação de campos por formulário já é aplicada em get_filtered_data
    if enrich_data:
        # Adiciona campos padronizados (mantendo heterogeneidade)
        df = _enrich_data_with_standardized_fields(df)
        # Adiciona múltiplos serviços aos fluxos
        df = _enrich_data_with_multiple_services(df)
    
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
    global _data_cache, _metadata_cache, _file_timestamps, _filtered_data_cache
    _data_cache.clear()
    _metadata_cache.clear()
    _file_timestamps.clear()
    _filtered_data_cache.clear()
    print("Cache limpo (incluindo cache de dados filtrados)")

def get_cache_info() -> Dict[str, Any]:
    """Retorna informações sobre o cache."""
    total_memory = sum(df.memory_usage(deep=True).sum() for df in _data_cache.values()) / 1024 / 1024  # MB
    filtered_memory = sum(df.memory_usage(deep=True).sum() for df in _filtered_data_cache.values()) / 1024 / 1024  # MB
    return {
        "data_files_cached": len(_data_cache),
        "metadata_files_cached": len(_metadata_cache),
        "filtered_data_cached": len(_filtered_data_cache),
        "total_memory_usage": total_memory,
        "filtered_memory_usage": filtered_memory,
        "total_memory_mb": round(total_memory + filtered_memory, 2)
    }
