# %%
import os
import re
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import textwrap # serve para formatar textos, ajustando-os para caber em uma largura específica, com a possibilidade de quebrar linhas e aplicar recuo.
from matplotlib.ticker import MaxNLocator
# %%
# ---------------------
# Leitura dos dados
# ---------------------
df = pd.read_csv("../../../data/SMSAp/base_perfil_epidemiologico.csv",
                 sep=";")
df.head()

# %%
# --------------------
# Configurações Globais dos Gráficos
# ---------------------
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

pd.set_option('display.max_rows', None) #para mostrar todas as linhas. 

# Ajustar a exibição do pandas para mostrar mais caracteres
pd.set_option('display.max_colwidth', None)  # Permite exibir a coluna inteira


# ------------------------------
# Funções utilitárias
# ------------------------------

def criar_diretorios():
    os.makedirs('../tables', exist_ok=True)
    os.makedirs('../plots', exist_ok=True)

# Cria diretórios para plots e tabelas
criar_diretorios()

# usando matplotlib
matplotlib.rc('font', size=10)

# --------------------------
def salvar_tabela_como_imagem(df, caminho_arquivo, titulo=None, largura_max_coluna=30):
    """ Salva a tabela gerada em .png.
        Parâmetros:
        - df: DataFrame do pandas.
        - caminho_arquivo: define o caminho onde será gravada a imagem (Ex: '../tables/nome_arquivo.png')
        - title: string com o título da tabela (opcional)
        - largura_max_coluna=30: define a largura das colunas da tabela
    """

    # Copiar DataFrame e aplicar quebra de linha
    df_wrapped = df.copy()
    for col in df_wrapped.columns:
        df_wrapped[col] = df_wrapped[col].astype(str).apply(
            lambda x: "\n".join(textwrap.wrap(x, largura_max_coluna)) if len(x) > largura_max_coluna else x
        )

    # Calcular largura ideal por coluna com base no maior item (linha ou cabeçalho)
    col_widths = [
        max(
            df_wrapped[col].apply(lambda x: len(max(str(x).split("\n"), key=len))).max(),
            len(str(col))
        ) * 0.12
        for col in df_wrapped.columns
    ]
    total_width = sum(col_widths) + 1

    # Altura baseada no número de linhas
    row_height = 0.6
    fig_height = df.shape[0] * row_height + (1.5 if titulo else 1)

    fig, ax = plt.subplots(figsize=(total_width, fig_height))
    ax.axis('off')

    tabela = ax.table(
        cellText=df_wrapped.values,
        colLabels=df_wrapped.columns,
        cellLoc='center',
        loc='center'
    )

    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.scale(1, 1.5)

    for (row, col), cell in tabela.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#40466e')
        else:
            cell.set_facecolor('#f1f1f2')
        cell.set_edgecolor('gray')

    if titulo:
        plt.title(titulo, fontsize=14, weight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(caminho_arquivo, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Tabela salva como imagem em {caminho_arquivo}")     

# ----------------------------------------

def plot_barh(data, title, xlabel, ylabel, filename, obs=2, show_text=True, show_values=True):
    """
    Gera um gráfico de barras horizontal com valores percentuais centralizados nas barras
    e o eixo X em valores absolutos.

    Parâmetros:
    - data: DataFrame do pandas (colunas devem corresponder às categorias).
    - title: string com o título do gráfico.
    - xlabel: string com o rótulo do eixo X.
    - ylabel: string com o rótulo do eixo Y.
    - filename: string com o caminho e nome do arquivo (ex: 'plots/exemplo.png')
    - obs: número de observações (define quantas cores usar).
    - show_text: se True, exibe observação adicional no gráfico.
    - show_values: se True, exibe os percentuais nas barras.
    """
    # Paleta de cores personalizada
    all_colors = ["#4E5EA7", '#F28E2B', "#AF3739", '#76B7B2', '#59A14F', '#EDC948']
    color = all_colors[:obs] if isinstance(all_colors, list) else all_colors

    # Cálculo dos percentuais por linha (ILPI)
    percent_df = data.div(data.sum(axis=1), axis=0) * 100

    # Plot
    ax = data.plot(kind='barh', color=color, figsize=(10, 6))
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Inserção dos percentuais nas barras
    if show_values:
        for col_idx, container in enumerate(ax.containers):
            col_name = data.columns[col_idx]
            for bar, (idx, percent) in zip(container, percent_df[col_name].items()):
                width = bar.get_width()
                if pd.notna(percent) and width > 0:
                    x = width / 2
                    y = bar.get_y() + bar.get_height() / 2
                    font_size = max(8, min(12, width * 0.25))
                    ax.text(x, y,
                            f'{percent:.1f}%',
                            ha='center',
                            va='center',
                            color='white',
                            fontweight='bold',
                            fontsize=font_size)

    # Observação adicional opcional
    if show_text:
        plt.text(0.075, 0.3, '* Uma das instituições é composta por unidades de moradia',
                 color='red', ha='left', va='bottom', transform=plt.gcf().transFigure, wrap=True)

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()

# ----------------------------------------

def plot_percentual_por_ilpi(pivot_df: pd.DataFrame, output_path: str):
    """
    Gera um gráfico de barras empilhadas mostrando o percentual de faixas de tempo de instituição por ILPI.

    Parâmetros:
    - pivot_df: pd.DataFrame
        DataFrame com contagem de residentes por faixa de tempo e por ILPI (ILPIs como índices).
    - output_path: str
        Caminho do arquivo para salvar a imagem do gráfico (ex: '../plots/nome_do_arquivo.png').
    """

    # Calcula os percentuais por ILPI (linha)
    pivot_percent = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100

    # Paleta de cores personalizada (1 cor por faixa etária — total 8 faixas)
    custom_colors = [
        '#4E79A7',  # Azul escuro
        "#092436",  # Azul claro
        "#A7794C",  # Laranja
        "#E6811C",  # Laranja claro
        "#24D20D",  # Verde
        '#8CD17D',  # Verde claro
        "#9D7E0E",  # Amarelo escuro
        "#B72A56"   # Rosa claro
    ]

    # Criação do gráfico empilhado
    ax = pivot_df.plot(
        kind='bar',
        stacked=True,
        figsize=(12, 6),
        color=custom_colors
    )

    # Adiciona rótulos nos segmentos de barra
    for bars, col in zip(ax.containers, pivot_df.columns):  # para cada faixa de tempo
        for bar, (ilpi, percent) in zip(bars, pivot_percent[col].items()):
            height = bar.get_height()
            if height > 0 and not pd.isna(percent):
                x = bar.get_x() + bar.get_width() / 2  # centraliza o texto no segmento.
                y = bar.get_y() + height / 2           # posiciona o texto no meio vertical.
                font_size = max(8, min(12, height * 0.25)) # Ajuste conforme necessário 
                ax.text(
                    x, y,
                    f'{percent: .1f}%', #  .1f para uma casa decimal
                    ha='center',
                    va='center',
                    color='white',
                    fontweight='bold',
                    fontsize=font_size
                )

    # Eixos e legenda
    plt.xlabel('ILPI')
    plt.ylabel('Número de Residentes')
    plt.title('Distribuição de Faixa Tempo de Instituição por ILPI (% por ILPI)')
    plt.xticks(rotation=0)
    plt.legend(title='Faixa Tempo Instituição', bbox_to_anchor=(1.0, 1), loc='upper left')

    # Salvar e exibir
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo como imagem: {output_path}")
    plt.show()    

# ----------------------------------------

def plot_bar_flex_auto(data, title, xlabel, ylabel, filename,
                       orientation='h', value_format='percent',
                       show_values=True, show_text=True,
                       col_categoria=None, col_valor=None, col_percent=None,
                       xtick_rotation=0):
    """
    Gera gráfico de barras (horizontal ou vertical) com valor absoluto no eixo
    e valor percentual ou absoluto no centro da barra.

    A função detecta automaticamente se deve calcular o percentual ou usar uma coluna existente.

    Parâmetros:
    - data: DataFrame original (com ou sem percentuais)
    - title: título do gráfico
    - xlabel / ylabel: rótulos dos eixos
    - filename: caminho para salvar o gráfico
    - orientation: 'h' ou 'v'
    - value_format: 'percent' ou 'absolute'
    - show_values: exibe texto nas barras
    - show_text: mostra anotação adicional
    - col_categoria / col_valor / col_percent: nomes das colunas (ou None para auto)
    - xtick_rotation: ângulo de rotação dos rótulos do eixo X (ex: 0, 45, 90)
    """

      # Paleta de cores personalizada (1 cor por faixa etária — total 8 faixas)
    custom_colors = [
        '#4E79A7',  # Azul escuro
        "#092436",  # Azul claro
        "#A7794C",  # Laranja
        "#E6811C",  # Laranja claro
        "#24D20D",  # Verde
        '#8CD17D',  # Verde claro
        "#9D7E0E",  # Amarelo escuro
        "#B72A56"   # Rosa claro
    ]

    is_horizontal = orientation == 'h'
    kind = 'barh' if is_horizontal else 'bar'
    
    df = data.copy()

    # --- Autoidentificação das colunas numéricas ---
    if col_valor is None:
        col_valor = df.select_dtypes(include='number').columns[0]

    if col_categoria is None:
        if df.index.name is not None and df.index.name != col_valor:
            col_categoria = df.index.name
            df = df.reset_index()
        else:
            col_categoria = df.columns[0]

    if col_percent is None:
        percent_candidates = [c for c in df.columns if 'propor' in c.lower() or '%' in c]
        if percent_candidates:
            col_percent = percent_candidates[0]

    # --- Base para plotagem ---
    df_plot = df[[col_categoria, col_valor]].copy()
    df_plot.set_index(col_categoria, inplace=True)

    # --- Percentuais ---
    if value_format == 'percent':
        if col_percent and col_percent in df.columns:
            df_plot['percent'] = df.set_index(col_categoria)[col_percent] * 100
        else:
            total = df_plot[col_valor].sum()
            df_plot['percent'] = (df_plot[col_valor] / total) * 100

    # --- Plot ---
    ax = df_plot[col_valor].plot(kind=kind, figsize=(10, 6), color=custom_colors)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # --- Texto nas barras ---
    if show_values:
        for idx, bar in zip(df_plot.index, ax.containers[0]):
            value = bar.get_width() if is_horizontal else bar.get_height()
            text = f'{df_plot.loc[idx, "percent"]:.1f}%' if value_format == 'percent' else f'{int(value)}'
            x = value / 2 if is_horizontal else bar.get_x() + bar.get_width() / 2
            y = bar.get_y() + bar.get_height() / 2 if is_horizontal else value / 2
            font_size = max(8, min(12, value * 0.25))
            ax.text(x, y, text, ha='center', va='center', color='white', fontweight='bold', fontsize=font_size)

    # --- Texto extra opcional ---
    if show_text:
        plt.text(0.02, 0.3, '* Uma das instituições é composta por unidades de moradia',
                 color='red', ha='left', va='bottom', transform=plt.gcf().transFigure, wrap=True)

    # --- Rotação dos rótulos do eixo X ---
    if not is_horizontal:
        plt.xticks(rotation=xtick_rotation)

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo como imagem: {filename}")
    plt.show()

############################################

def plot_bar_flex_unificado(data, title, xlabel, ylabel, filename,
                            orientation='h', value_format='percent',
                            show_values=True, show_text=True,
                            col_categoria=None, col_valor=None,
                            col_percent=None, col_grupo=None,
                            xtick_rotation=0):
    """
    Gera gráfico de barras (horizontal/vertical), simples ou empilhado, com suporte a percentuais ou absolutos.

    Parâmetros:
    - data: DataFrame
    - title, xlabel, ylabel: Títulos e rótulos dos eixos
    - filename: caminho para salvar o gráfico
    - orientation: 'h' ou 'v'
    - value_format: 'percent' ou 'absolute'
    - show_values: mostra valores nas barras
    - show_text: insere anotação adicional
    - col_categoria: coluna de categorias (auto se None)
    - col_valor: coluna de valores numéricos (auto se None)
    - col_percent: coluna com percentuais (auto se None)
    - col_grupo: coluna de agrupamento (para gráfico empilhado)
    - xtick_rotation: rotação dos rótulos no eixo X
    """

    custom_colors = [
        '#4E79A7', "#092436", "#A7794C", "#E6811C",
        "#24D20D", '#8CD17D', "#9D7E0E", "#B72A56"
    ]

    df = data.copy()
    # Define o tipo do gráfico com base na orientação ('h' para horizontal, 'v' para vertical).
    is_horizontal = orientation == 'h'
    kind = 'barh' if is_horizontal else 'bar'

    # --- Autoidentificação das colunas ---
    # Numéricas
    # Seleciona a última coluna numérica do DataFrame como valor se não for passada explicitamente.
    if col_valor is None:
        col_valor = df.select_dtypes(include='number').columns[-1]

    # Categóricas
    # Procura a primeira coluna com número de categorias menor que o número de linhas (boa heurística para identificar categorias).
    if col_categoria is None:
        for c in df.columns:
            if c != col_valor and df[c].nunique() < len(df):
                col_categoria = c
                break
    # Para empilhamento das colunas        
    # Tenta encontrar uma coluna extra para servir como agrupador (como "raça", "sexo" etc.)
    if col_grupo is None:
        possible_groups = [c for c in df.columns if c not in [col_valor, col_categoria]]
        if possible_groups:
            col_grupo = possible_groups[0]
        else:
            col_grupo = None

    # --- Preparar dados ---
    # Se houver agrupamento (col_grupo): gráfico empilhado
    if col_grupo:
        # reorganiza os dados em formato de tabela dinâmica (linhas = categorias, colunas = grupos).
        df_pivot = df.pivot_table(index=col_categoria, columns=col_grupo, values=col_valor, aggfunc='sum').fillna(0)
        df_plot = df_pivot.copy()

        # Para mostrar percentuais no centro das barras
        # divide cada linha pelo total da linha para obter percentuais (100% por categoria).
        percent_df = df_plot.div(df_plot.sum(axis=1), axis=0) * 100
    else:
        # Se não houver agrupamento: gráfico de barras simples
        # Define df_plot com a categoria no índice.
        df_plot = df[[col_categoria, col_valor]].copy()
        df_plot.set_index(col_categoria, inplace=True)

        # Se value_format == 'percent', calcula os percentuais a serem exibidos.
        if value_format == 'percent':
            if col_percent and col_percent in df.columns:
                df_plot['display_value'] = df.set_index(col_categoria)[col_percent] * 100
            else:
                total = df_plot[col_valor].sum()
                df_plot['display_value'] = (df_plot[col_valor] / total) * 100
        else:
            df_plot['display_value'] = df_plot[col_valor]

    # --- Plotagem ---
    ax = df_plot.plot(kind=kind, figsize=(10, 6),
                      stacked=bool(col_grupo),
                      color=custom_colors[:len(df_plot.columns)])
    
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # --- Inserção de valores ---
    if show_values:
        # Para gráfico empilhado
        if col_grupo:
            # Percorre cada "grupo" dentro do empilhamento:
            for bars, col in zip(ax.containers, df_plot.columns): # ax.containers: grupos de barras no gráfico
                for bar, (idx, abs_val) in zip(bars, df_plot[col].items()):
                    if is_horizontal:
                        width = bar.get_width()
                        y = bar.get_y() + bar.get_height() / 2
                        x = bar.get_x() + width / 2
                    else:
                        height = bar.get_height() # bar.get_height(): altura da barra (valor absoluto)
                        x = bar.get_x() + bar.get_width() / 2
                        y = bar.get_y() + height / 2

                    if value_format == 'percent':
                        percent_val = percent_df.loc[idx, col] # percent_df.loc[idx, col]: valor percentual daquela parte da barra
                        if percent_val > 0:
                            ax.text(x, y, f'{percent_val:.1f}%', ha='center', va='center',
                                    color='white', fontweight='bold', fontsize=9)
                    else:
                        if abs_val > 0:
                            ax.text(x, y, f'{int(abs_val)}', ha='center', va='center',
                                    color='white', fontweight='bold', fontsize=9)
        else:
            # Para gráfico simples
            for idx, bar in zip(df_plot.index, ax.containers[0]):
                value = bar.get_width() if is_horizontal else bar.get_height()
                display_value = df_plot.loc[idx, 'display_value']

                if value_format == 'percent':
                    text = f'{display_value:.1f}%'
                else:
                    text = f'{int(display_value)}'

                x = value / 2 if is_horizontal else bar.get_x() + bar.get_width() / 2
                y = bar.get_y() + bar.get_height() / 2 if is_horizontal else value / 2

                ax.text(x, y, text, ha='center', va='center',
                        color='white', fontweight='bold', fontsize=9)

    # --- Texto adicional opcional ---
    if show_text:
        plt.text(0.02, 0.3, '* Uma das instituições é composta por unidades de moradia',
                 color='red', ha='left', va='bottom',
                 transform=plt.gcf().transFigure, wrap=True)

    # --- Rotação dos rótulos ---
    if not is_horizontal:
        plt.xticks(rotation=xtick_rotation)

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo como imagem: {filename}")
    plt.show()

 ##############################
# ------------------------------
# Funções de Processamento
# ------------------------------

def processa_uma_variavel(df, colunas_dict):
    """
    Extrai e renomeia colunas de um DataFrame.

    Parâmetros:
    - df: DataFrame original.
    - colunas_dict: dicionário com colunas originais como chave e novo nome como valor.

    Retorna:
    - Um novo DataFrame com as colunas renomeadas.
    """
    return df[list(colunas_dict.keys())].rename(columns=colunas_dict)

# ----------------------------------------

def processa_binario(df, coluna, legenda, rename_dict):
    """
    Processa variáveis binárias para análise.

    Parâmetros:
    - df: Data Frame
    - coluna: coluna da variável
    - legenda: str, nome da nova coluna de saída
    - rename_dict: dict, ex: {1: 'Sim', 0: 'Não'}
    
    Exemplo de uso:
    tabela_camas = processa_binario(
        df,
        'residents_bedroom',
        'Camas segundo a Norma',
        rename_dict)
    """
    temp = (df[['institution_name', coluna]]
                # Cria uma coluna cujo nome é o valor da variável legenda 
                # populacionando com o mapeamento
                .assign(**{legenda: df[coluna].map(rename_dict)}) 
                .rename(columns={'institution_name': 'ILPI'})
                .drop(columns=coluna)
                )
    return temp

# ----------------------------------------

def processa_uma_variavel_com_opcoes(df, coluna_original, nome_saida, mapa_valores):
    """
    Processa códigos inteiros para uma string descritiva (concatenada) com base em um dicionário de mapeamento.

    Parâmetros:
    - df: DataFrame original.
    - coluna_original: str, nome da coluna com códigos.
    - nome_saida: str, nome da nova coluna de saída.
    - mapa_valores: dict, mapeamento de código -> texto.

    Retorna:
    - DataFrame com 'ILPI' e a nova coluna.
    """
    temp = df[["institution_name", coluna_original]].copy()
    
    # Concatena textos com base nos valores
    def construir_texto(valor):
        partes = [txt for cod, txt in mapa_valores.items() if valor == cod]
        return ', '.join(partes) if partes else 'Não informado'
    
    temp[nome_saida] = temp[coluna_original].map(construir_texto)
    temp = temp.rename(columns={"institution_name": "ILPI"})[["ILPI", nome_saida]]
    
    return temp

# ----------------------------------------
def processa_multiresposta(df, colunas_dict, legenda):
    """
    Processa variáveis de múltiplas respostas (checkbox), criando uma nova coluna com
    descrições combinadas, e remove linhas sem nenhuma seleção.

    Parâmetros:
    -----------
    df : pd.DataFrame
        O DataFrame contendo os dados originais com variáveis de múltiplas respostas.
    colunas_dict : dict
        Um dicionário onde as chaves são nomes de colunas de checkbox e os valores são
        as descrições associadas a cada resposta.
    legenda : str
        Nome da nova coluna que irá conter a descrição concatenada das respostas.

    Retorno:
    --------
    pd.DataFrame
        Um novo DataFrame com as colunas 'ILPI' e a nova coluna de legenda,
        sem linhas onde nenhuma resposta foi marcada (ou seja, todas eram 0).
    """

    # Cria nova coluna com as descrições concatenadas
    df[legenda] = df.apply(
        lambda row: ', '.join(
            [desc for col, desc in colunas_dict.items() if row.get(col) == 1]
        ) if any(row.get(col) == 1 for col in colunas_dict) else np.nan,
        axis=1
    )

    # Seleciona apenas as colunas relevantes
    resultado = df[['institution_name', legenda]].rename(columns={'institution_name': 'ILPI'})

    # Remove linhas onde a nova coluna é NaN
    resultado = resultado.dropna(subset=[legenda])

    return resultado

# ----------------------------------------

def extrair_morbidades(df, morbidade_dict, nome_coluna_soma=None):
    """
    Filtra e retorna os dados de morbidades legíveis,
    agrupados por institution_name, full_name, cpf.
    A coluna 'other_morbidities' é normalizada (minúsculas, sem espaços),
    separando múltiplas entradas por vírgula, ponto e vírgula ou barra vertical.
    Soma final inclui morbidades binárias + textuais distintas.

    Parâmetros:
    - df: DataFrame.
    - morbidade_dict: dict, mapeamento de código -> texto.
    - nome_coluna_soma: str, nome da coluna soma (Se None, usa 'soma_morbidities').

    Retorna:
    - DataFrame com as morbidades processadas, incluindo:
      - 'Morbidades': lista de morbidades binárias e textuais.
      - 'other_morbidities': morbidades textuais normalizadas.
      - 'soma_morbidities': soma total de morbidades (binárias + textuais).
    """

    import re

    morbidities_cols = list(morbidade_dict.keys())
    #df[morbidities_cols] = df[morbidities_cols].apply(pd.to_numeric, errors='coerce')

    campos_para_propagacao = ['institution_name', 'full_name', 'cpf']
    for campo in campos_para_propagacao:
        df[campo] = df[campo].ffill()

    # Inclui linhas que tenham morbidades binárias OU outras textuais
    df_filtrado = df[df[morbidities_cols].eq(1).any(axis=1) | df['other_morbidities'].notna()].copy()

    if nome_coluna_soma is None:
        nome_coluna_soma = 'soma_morbidities'

    df_filtrado['soma_binarias'] = df_filtrado[morbidities_cols].sum(axis=1, numeric_only=True)

    def nomes_morbidades(row):
        return ', '.join([morbidade_dict[col] for col in morbidities_cols if row.get(col) == 1])

    df_filtrado['Morbidades'] = df_filtrado.apply(nomes_morbidades, axis=1)

    # Padroniza a coluna 'other_morbidities'
    df_filtrado['other_morbidities'] = (
        df_filtrado['other_morbidities']
        .astype(str)
        .str.lower()
        .replace('nan', '')
    )

    # Agrupamento
    df_resultado = df_filtrado.groupby(['institution_name', 'full_name', 'cpf'], as_index=False).agg({
        'Morbidades': lambda x: ', '.join(sorted(set(', '.join(x).split(', ')))),
        'other_morbidities': lambda x: ', '.join(sorted(set(filter(None, map(str.strip, x))))),
        'soma_binarias': 'sum'
    })

    # Conta as morbidades textuais, com separadores: , ; |
    def contar_textuais(texto):
        if not texto:
            return 0
        itens = re.split(r'[;,|]', texto)  # divide por vírgula, ponto e vírgula ou barra vertical
        return len([item.strip() for item in itens if item.strip()])

    df_resultado['soma_other'] = df_resultado['other_morbidities'].apply(contar_textuais)
    df_resultado[nome_coluna_soma] = df_resultado['soma_binarias'] + df_resultado['soma_other']

    # Limpa colunas auxiliares
    df_resultado = df_resultado.drop(columns=['soma_binarias', 'soma_other'])
    df_resultado = df_resultado.sort_values(by=['institution_name', 'full_name', 'cpf'])

    return df_resultado

# ----------------------------------------

def extrair_medicamentos(df):
    """
    Extrai os medicamentos usados por residente, incluindo combinações, com colunas:
    med_name, dosage, taken_daily. Cada linha representa 1 medicamento.
    """
    tomadas_dia = {
        "1": "1 x ao dia",
        "2": "2 x ao dia",
        "3": "3 x ao dia",
        "4": "4 x ao dia",
        "5": "semanalmente",
        "6": "mensalmente",
        "7": "quinzenalmente"
    }

    # Filtra apenas registros do instrumento medicamentos_em_uso
    df_meds = df[df['redcap_repeat_instrument'] == 'medicamentos_em_uso'].copy()

    # Propaga os campos-chave
    campos_chave = ['institution_name', 'full_name', 'cpf']
    for campo in campos_chave:
        if df_meds[campo].dtype == object:
            df_meds[campo] = df_meds[campo].ffill().str.upper()
        else:
            df_meds[campo] = df_meds[campo].ffill()

    registros = []

    for _, row in df_meds.iterrows():
        base_info = {
            'institution_name': row['institution_name'],
            'full_name': row['full_name'],
            'cpf': row['cpf']
        }

        # Medicamento principal
        med_name = str(row.get('med_name')).strip().lower() if pd.notnull(row.get('med_name')) else None
        if med_name:
            valor_bruto = row.get('taken_daily')
            taken_daily = None
            if pd.notnull(valor_bruto):
                chave = str(int(valor_bruto)) if not isinstance(valor_bruto, str) else valor_bruto.strip()
                taken_daily = tomadas_dia.get(chave)

            registros.append({
                **base_info,
                'med_name': med_name,
                'dosage': row.get('dosage'),
                'taken_daily': taken_daily
            })

        # Combinações
        for i in range(1, 7):
            comb_col = f'combination_{i}'
            dose_col = f'combination_dosage_{i}'

            comb_value = row.get(comb_col)
            if pd.notnull(comb_value) and str(comb_value).strip():
                registros.append({
                    **base_info,
                    'med_name': str(comb_value).strip().lower(),
                    'dosage': row.get(dose_col),
                    'taken_daily': None
                })

    # Cria DataFrame final
    df_resultado = pd.DataFrame(registros)

    # Ordena para melhor leitura
    df_resultado = df_resultado.sort_values(by=['institution_name', 'full_name', 'cpf'])

    # Renomear colunas
    df_resultado = df_resultado.rename(columns={
        "institution_name": "ILPI",
        "full_name": "Nome Completo",	
        "cpf": "CPF",	
        "med_name": "Medicamento",	
        "dosage": "Dose",	
        "taken_daily": "Tomadas ao dia"
    })

    return df_resultado

# ----------------------------------------

def classificar_risco(df, condicoes_critico, condicoes_alerta, condicoes_atencao, incluir_sem_risco=True):
    """
    Aplica condições de risco e retorna:
    - DataFrame agrupado por 'cpf' com colunas: institution_name, cpf, full_name, risco (colorido em HTML)
    - Resumo com contagem por nível de risco (rótulos limpos, sem HTML)
   
     Parâmetros:
    - df: DataFrame original
    - condicoes_critico, condicoes_alerta, condicoes_atencao: dicionários de condições
    
    - incluir_sem_risco: se True, classifica como 'Sem Risco' os registros que não se encaixam em nenhuma categoria
    OBS: Para visualizar cores no Jupyter, usar `display(HTML(resultado.to_html(escape=False)))`
    """

    df_copia = df.copy()

    df_copia['risco'] = None

    cores_por_risco = {
        'Crítico': 'red',
        'Alerta': 'orange',
        'Atenção': 'yellow',
        'Sem Risco': 'green'
    }

    def aplicar_classificacao(df_local, condicoes_dict, label):
        cond = pd.Series(True, index=df_local.index)
        for col, func in condicoes_dict.items():
            cond &= df_local[col].apply(func)
        return cond.replace({True: label, False: None})

    for condicoes, label in [
        (condicoes_critico, 'Crítico'),
        (condicoes_alerta, 'Alerta'),
        (condicoes_atencao, 'Atenção')
    ]:
        mask = aplicar_classificacao(df_copia, condicoes, label)
        condicao_vazia = df_copia['risco'].isna()
        df_copia.loc[mask.notna() & condicao_vazia, 'risco'] = label

    # Preencher com "Sem Risco", se solicitado
    if incluir_sem_risco:
        df_copia.loc[df_copia['risco'].isna(), 'risco'] = 'Sem Risco'

    # Define a ordem de severidade
    ordem_prioridade = {'Crítico': 0, 'Alerta': 1, 'Atenção': 2, 'Sem Risco': 3}
    df_copia['prioridade'] = df_copia['risco'].map(ordem_prioridade)

    agrupado = (
        df_copia
        .sort_values('prioridade')
        .groupby('cpf', as_index=False)
        .first()[['institution_name', 'cpf', 'full_name', 'risco']]
    )

    # Aplica cor HTML na coluna 'risco'
    def colorir(valor):
        cor = cores_por_risco.get(valor, 'black')
        return f'<span style="color: {cor}; font-weight: bold;">{valor}</span>'

    agrupado['Score_Fragilidade'] = agrupado['risco'].apply(colorir)

    # Resumo por grupo de risco
    resumo = (
        agrupado
        .groupby(['institution_name', 'risco'], as_index=False)
        .size()
        .rename(columns={'size': 'total'})
    )

    return agrupado.drop(columns=['risco']), resumo

# %%
## ---------------------
## Análises e Gráficos
## ---------------------

## --------------------
## ---- 1 - Gênero
## -------------------

## Filtra os valores válidos (1 = Masculino, 2 = Feminino)
df_filtered = df[df['sex'].isin([1, 2])].copy()

# Mapeia os valores de sexo para strings
df_filtered['sex'] = df_filtered['sex'].map({1: 'Masculino', 2: 'Feminino'})

# Agrupa por institution_name e sexo e reorganiza com unstack
gender = df_filtered.groupby(['institution_name', 'sex']).size().unstack(fill_value=0).reset_index()

# Remove o nome do eixo de colunas
gender.columns.name = None
gender

# %%
# Calcula a porcentagem de cada sexo por instituição
gender_prop = (round(gender[['Feminino', 'Masculino']]
                        .div(gender[['Feminino', 'Masculino']]
                        .sum(axis=1), axis=0), 2))

# Adiciona a coluna de nome da instituição
gender_prop.insert(0, 'institution_name', gender['institution_name'])
gender_prop = gender_prop.rename(columns={'Feminino':'Feminino(prop)', 'Masculino':'Masculino(prop)'})
gender_prop
# %%
# Agrupando as tabelas
gender_join = gender.merge(gender_prop)
gender_join = gender_join[[
    'institution_name', 
    'Feminino', 'Feminino(prop)', 
    'Masculino', 'Feminino(prop)', 
    'Masculino(prop)']]
gender_join
# %%
# Salvando como imagem
salvar_tabela_como_imagem(
    gender_join,
    '../tables/01_tabela_genero_abs_prop.png',
    largura_max_coluna=15
)
 
# %%
# Gráfico 01 -- Gênero dos Residentes da ILPI

# Pivot da tabela para formato wide (um DataFrame por faixa etária por ILPI)
#pivot_df = gender_prop.pivot(index='institution_name', columns=['Feminimo', 'Masculino'])

plot_barh(gender.set_index('institution_name'), 
          title='Gênero dos Residentes da ILPI', 
          xlabel='Número de residentes', ylabel='ILPIs',
          filename='../plots/01_grafico_genero_perc.png',
          obs=2,
          show_text=True,
          show_values=True)

# %%

## --------------------
## ---- 2 - Idade 
## -------------------

# Cria um DataFrame para a idade dos residentes
df_idade = df[['institution_name', 'elder_age']]

# Filtra apenas as linhas com idade dos residentes
df_idade = df_idade[df_idade['elder_age'].notna()].astype({'elder_age': 'int64'})
df_idade.head()
# %%
## ----- Plotando a idade dos residentes com linha de média
# Calcula a média geral
media_idade = df_idade['elder_age'].mean().__round__(1)
media_idade
# %%
# Cria um eixo X com base no índice dos residentes
x = range(len(df_idade))

# Plot
plt.figure(figsize=(12, 6))

# Pontos individuais
plt.scatter(x, df_idade['elder_age'], color='gray', alpha=0.6, label='Residentes')

# Linha de média
plt.axhline(y=media_idade, color='red', linestyle='--', linewidth=1.5, label=f'Média: {media_idade:.1f}')

# Eixos
plt.xlabel('Idade')
plt.ylabel('Idade')
plt.title('Idade dos Residentes com Linha de Média')

# Legenda
plt.legend()

# Layout e salvamento
plt.tight_layout()
plt.savefig('../plots/02_grafico_idades_residentes_com_media.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico de Idade dos Residentes salvo como imagem.")
plt.show()
# %%
## --------------------
## ---- Idade por ILPI
## -------------------

# Agrupa por ILPI e calcula a média de idade dos residentes

# Calcula a média por ILPI
media_idade = df_idade.groupby('institution_name')['elder_age'].mean().reset_index()
media_idade.columns = ['institution_name', 'Média']

# Define ILPIs únicos e ordenados (para o eixo X)
ilpis = sorted(df_idade['institution_name'].unique())

# Plot
plt.figure(figsize=(12, 6))

# Pontos individuais
plt.scatter(df_idade['institution_name'], df_idade['elder_age'], color='gray', alpha=0.6, label='Residentes')

# Médias por ILPI em vermelho
plt.scatter(media_idade['institution_name'], media_idade['Média'], color='red', s=100, marker='D', label='Média por ILPI')

# Eixos e rótulos
plt.xlabel('ILPI')
plt.ylabel('Idade dos Residentes')
plt.title('Idade dos Residentes por ILPI com Média Destacada')

# Definir o eixo X com os valores inteiros das ILPIs
plt.xticks(ilpis)

# Legenda, layout e salvamento
plt.legend()
plt.tight_layout()
plt.savefig('../plots/02_grafico_idades_residentes_por_ilpi.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico de Idade dos Residentes por ILPI salvo como imagem.")
plt.show()

# %%
## --------------------
## ---- Faixa Etária por ILPI
## -------------------

# Agrupa por institution_name e idade, contando os residentes
idade = df_idade['elder_age'].value_counts().reset_index()
idade.head()
# %%
# Define os intervalos de idade para as categorias

elder_age_bins = {
    '61 a 65 anos': (60, 65),
    '66 a 70 anos': (65, 70),
    '71 a 75 anos': (70, 75),
    '76 a 80 anos': (75, 80),
    '81 a 85 anos': (80, 85),
    '86 a 90 anos': (85, 90),
    '91 a 95 anos': (90, 95),
    '96 a 100 anos': (95, 100)       
}

# Gera a lista de bins e labels
bins = [60] + [v[1] for v in elder_age_bins.values()]
labels = list(elder_age_bins.keys())

# Garante que estamos trabalhando com uma cópia
df_idade = df_idade.copy()

# Cria a coluna de faixa etária
df_idade['elder_age_bin'] = pd.cut(df_idade['elder_age'],bins=bins,labels=labels,right=False)

# Deleta a coluna 'elder_age' original
df_idade = df_idade.drop(columns=['elder_age'])

# Filtra apenas as linhas com faixa etária atribuída (i.e., que não são NaN) e
# Exibe a contagem de residentes por faixa etária
df_idade = df_idade[df_idade['elder_age_bin'].notna()].value_counts().sort_index()
df_idade

# %%
# Cria um DataFrame a partir da série de contagem
df_idade = df_idade.reset_index()
df_idade
# %%
# Renomeia as colunas
df_idade = df_idade.rename(columns={'institution_name': 'ILPI', 'elder_age_bin': 'Faixa Etária', 'count': 'Número de Residentes'}) 
df_idade

# %%
# Salvando a tabela de idades
salvar_tabela_como_imagem(
    df_idade,
    '../tables/02_tabela_idade.png',
    largura_max_coluna=25
)
# %%

# Pivot da tabela para formato wide (um DataFrame por faixa etária por ILPI)
pivot_df = df_idade.pivot(index='ILPI', columns='Faixa Etária', values='Número de Residentes')

plot_percentual_por_ilpi(
    pivot_df,
    '../plots/02_grafico_faixa_etaria_por_ilpi.png'
    )
# %%
## --------------------
## ---- 3 - Raça e Cor
## -------------------

# Cria um DataFrame para a raça dos residentes
df_raca = df[['institution_name', 'race']]
df_raca.head()
# %%
# Filtra apenas as linhas com raça dos residentes       
df_raca = df_raca[df_raca['race'].notna()].astype({'race': 'int64'})
df_raca.head()
# %%
# Agrupa por 'race', usa .size() para contar quantas vezes cada raça aparece e
# renomeia a coluna de contagem para 'total'
df_raca_grouped = df_raca.groupby('race').size().reset_index(name='total')
df_raca_grouped
# %%
# Calcula proporção de cada raça
df_raca_grouped['proporcao'] = df_raca_grouped['total'] / df_raca_grouped['total'].sum()
df_raca_grouped['proporcao'] = (df_raca_grouped['proporcao']).round(2)
df_raca_grouped
# %%
# Define um dicionário para mapear os códigos de raça para strings
df_raca_grouped['race'] = df_raca_grouped['race'].replace({ 
    1: 'Branca',
    2: 'Preta',
    3: 'Parda',
    4: 'Amarela',
    5: 'Indígena',
    6: 'Não Informado',
})

df_raca_grouped 

# %%
# Salvando a tabela de raça 
# A tabela df_raca_grouped contém a proporção de raça geral
salvar_tabela_como_imagem(
    df_raca_grouped,
    '../tables/03_tabela_raca_geral.png', 
    largura_max_coluna=25,
)                             
# %%

plot_bar_flex_auto(
    df_raca_grouped,
    title='Distribuíção por Raça/Cor dos Residentes',
    xlabel='Raça/Cor', ylabel='Número de residentes',
    filename='../plots/03_grafico_raca_geral.png',
    show_values=True,
    show_text=False,
    value_format='absolute',
    orientation='v',
    xtick_rotation=0
)

plot_bar_flex_auto(
    df_raca_grouped,
    title='Distribuíção por Raça/Cor dos Residentes (%)',
    xlabel='Raça/Cor', ylabel='Número de residentes',
    filename='../plots/03_grafico_raca_geral_percentual.png',
    show_values=True,
    show_text=False,
    value_format='percent',
    orientation='v',
    xtick_rotation=0
)

# %%
# Cria um DataFrame raça por ILPI
df_raca_inst = df_raca.groupby(['institution_name', 'race']).size().reset_index(name='total')
df_raca_inst
# %%
# Calcula proporção dentro de cada instituição com .transform()
# Para cada grupo (cada institution_name), ele calcula a soma dos valores na coluna total.
# mas ao invés de reduzir o grupo a um único valor (como o .sum() padrão faria), ele replica 
# esse valor para cada linha do grupo.
df_raca_inst['proporcao'] = df_raca_inst['total'] / df_raca_inst.groupby('institution_name')['total'].transform('sum')
df_raca_inst['proporcao'] = (df_raca_inst['proporcao']).round(2)
df_raca_inst        
# %%
# Define um dicionário para mapear os códigos de raça para strings por ILPI
df_raca_inst['race'] = df_raca_inst['race'].replace({ 
    1: 'Branca',
    2: 'Preta',
    3: 'Parda',
    4: 'Amarela',
    5: 'Indígena',
    6: 'Não sabe',
})

df_raca_inst
# %%
# Salvando a tabela de raça 
# A tabela df_raca_grouped contém a proporção de raça geral
salvar_tabela_como_imagem(
    df_raca_inst,
    '../tables/03_tabela_raca_por_ILPI.png', 
    largura_max_coluna=25,
)                             

# %%
# Gráfico residentes por ILPI absoluto
plot_bar_flex_unificado(
    df_raca_inst,
    col_categoria='institution_name',
    col_valor='total',
    col_grupo='race',
    value_format='absolute',  # Texto em %
    orientation='v',
    title='Distribuição por Raça/Cor dos Residentes por ILPI',
    xlabel='ILPI',
    ylabel='Número de residentes',  # Eixo Y correto: absolutos
    filename='../plots/03_grafico_raca_por_ilpi_absoluto.png',
    show_text=False
)
# %%
# Gráfico residentes por ILPI percentual
plot_bar_flex_unificado(
    df_raca_inst,
    col_categoria='institution_name',
    col_valor='total',
    col_grupo='race',
    value_format='percent',  # Texto em %
    orientation='v',
    title='Distribuição por Raça/Cor dos Residentes por ILPI',
    xlabel='ILPI',
    ylabel='Número de residentes',  # Eixo Y correto: absolutos
    filename='../plots/03_grafico_raca_por_ilpi_percentual.png',
    show_text=False
)

# %%
## --------------------
## ---- 4 - Escolaridade
## -------------------

# Cria um DataFrame para a escolaridade dos residentes
df_escolaridade = df[['institution_name', 'scholarship']]
df_escolaridade.head()
# %%
# Filtra apenas as linhas com escolaridade dos residentes
df_escolaridade = df_escolaridade[df_escolaridade['scholarship'].notna()].astype({'scholarship': 'int64'})
df_escolaridade.head()
# %%
# Agrupa por 'scholarshiphip, usa .size() para contar quantas vezes cada escolaridade aparece e
# renomeia a coluna de contagem para 'total'
df_escolaridade_grouped = df_escolaridade.groupby('scholarship').size().reset_index(name='total')
df_escolaridade_grouped.head()
# %%
# Calcula proporção dentro de cada instituição com .transform()
# Para cada grupo (cada institution_name), ele calcula a soma dos valores na coluna total.
# mas ao invés de reduzir o grupo a um único valor (como o .sum() padrão faria), ele replica 
# esse valor para cada linha do grupo.
df_escolaridade_grouped['proporcao'] = df_escolaridade_grouped['total'] / df_escolaridade_grouped['total'].sum()
df_escolaridade_grouped['proporcao'] = (df_escolaridade_grouped['proporcao']).round(2)
df_escolaridade_grouped
# %%
# Define um dicionário para mapear os códigos de escolaridade para strings
df_escolaridade_grouped['scholarship'] = df_escolaridade_grouped['scholarship'].replace({ 
    1: 'nenhuma',
    2: '1 a 3 anos',
    3: '4 a 7 anos',
    4: '8 anos ou mais',
    5: 'não há registro',
})
df_escolaridade_grouped
# %%
salvar_tabela_como_imagem(
    df_escolaridade_grouped,
    '../tables/04_tabela_escolaridade_geral.png',
    largura_max_coluna=25,
                          )
# %%

plot_bar_flex_auto(df_escolaridade_grouped,
                   col_categoria='scholarship',
                   col_valor='total',
                   #col_grupo='institution_name',
                   value_format='absolute',  # Texto em %
                   orientation='v',
                   title='Escolaridade Geral dos Residentes',
                   xlabel='Tempo de estudo', ylabel='Número de Residentes',
                   filename='../plots/04_grafico_escolaridade_residente_por_ILPI.png',
                   show_text=False)

plot_bar_flex_auto(df_escolaridade_grouped,
                   col_categoria='scholarship',
                   col_valor='total',
                   #col_grupo='institution_name',
                   value_format='percent',  # Texto em %
                   orientation='v',
                   title='Escolaridade Geral dos Residentes',
                   xlabel='Tempo de estudo', ylabel='Número de Residentes',
                   filename='../plots/04_grafico_escolaridade_residente_por_ILPI_percentual.png',
                   show_text=False)
# %%
# Cria um Data Frame escolaridade por ILPI
df_escolar_inst = df_escolaridade.groupby(['institution_name', 'scholarship']).size().reset_index(name='total')
df_escolar_inst
# %%

# Calcula proporção de cada escolaridade
df_escolar_inst['proporcao'] = df_escolar_inst['total'] / df_escolar_inst.groupby('institution_name')['total'].transform('sum')
df_escolar_inst['proporcao'] = (df_escolar_inst['proporcao']).round(2)
df_escolar_inst     
# %%
# Define um dicionário para mapear os códigos de escolaridade para strings
df_escolar_inst['scholarship'] = df_escolar_inst['scholarship'].replace({ 
    1: 'nenhuma',
    2: '1 a 3 anos',
    3: '4 a 7 anos',
    4: '8 anos ou mais',
    5: 'não há registro',
})
df_escolar_inst
# %%
salvar_tabela_como_imagem(
    df_escolar_inst,
     '../tables/04_tabela_escolaridade_por_ILPI.png',
    largura_max_coluna=25,
)
# %%
# Criando gráfico escolaridade por ILPI absoluto
plot_bar_flex_unificado(df_escolar_inst,
                        col_categoria='institution_name',
                        col_valor='total',
                        col_grupo='scholarship',
                        title='Distribuíção por escolaridade por instituição',
                        xlabel='Tempo de estudo', ylabel='Número de residentes',
                        filename='../plots/04_grafico_escolaridade_por_ILPI_absoluto.png',
                        orientation='v',
                        value_format='absolute',
                        show_values=True,
                        show_text=False
)

# Criando gráfico escolaridade por ILPI absoluto
plot_bar_flex_unificado(df_escolar_inst,
                        col_categoria='institution_name',
                        col_valor='total',
                        col_grupo='scholarship',
                        title='Distribuíção percentual por escolaridade por instituição',
                        xlabel='Tempo de estudo', ylabel='Número de residentes',
                        filename='../plots/04_grafico_proporcao_escolaridade_por_ILPI.png',
                        orientation='v',
                        value_format='percent',
                        show_values=True,
                        show_text=False
)
# %%

## --------------------
## ----- 5 - Tempo institucionalizado
## --------------------
# Estatística básica
df['institut_time_years'].describe()
# %%
# Acha os registros que provavelmente estejam errados
df.loc[df['institut_time_years'] > 30]
# %%
temp_instit = df[['institution_name', 'institut_time_years']]
temp_instit.head()
# %%
# Filtra apenas as linhas com tempo de institucionalização
temp_instit = temp_instit[temp_instit['institut_time_years'].notna()].astype({'institut_time_years':'int64'})
temp_instit.head()
# %%
# Agrupa por 'institut_time_years', usa .size() para contar quantas vezes cada escolaridade aparece e
# renomeia a coluna de contagem para 'total'
temp_instit_grouped = temp_instit.groupby('institut_time_years').size().reset_index(name='total')
temp_instit_grouped.head()
# %%
# Calcula proporcao de tempo de institucionalização
temp_instit_grouped['proporcao'] = temp_instit_grouped['total'] / temp_instit_grouped['total'].sum()
temp_instit_grouped['proporcao'] = temp_instit_grouped['proporcao'].round(2)
temp_instit_grouped
# %%
salvar_tabela_como_imagem(
    temp_instit_grouped,
    '../tables/05_tabela_tempo _institucionalização.png',
    largura_max_coluna=25,
)
# %%
# Configura o tamanho do gráfico
plot_bar_flex_auto(temp_instit_grouped,
                        #col_categoria='institution_name',
                        col_valor='total',
                        #col_grupo='institut_time_years',
                        title='Tempo de Institucionalização dos Residentes',
                        xlabel='Tempo de instituíção', ylabel='Número de residentes',
                        filename='../plots/05_grafico_tempo_instit.png',
                        orientation='v',
                        value_format='absolute',
                        show_values=True,
                        show_text=False
)

# Criando gráfico tempo institucionalização por ILPI absoluto
plot_bar_flex_auto(temp_instit_grouped,
                        #col_categoria='institution_name',
                        col_valor='total',
                        #col_grupo='institut_time_years',
                        title='Tempo de Institucionalização dos Residentes Percentual',
                        xlabel='Tempo de instituíção', ylabel='Número de residentes',
                        filename='../plots/05_grafico_proporcao_tempo_instit.png',
                        orientation='v',
                        value_format='percent',
                        show_values=True,
                        show_text=False
)

# %%
# Define os intervalos tempo instituíção para as categorias

inst_time_bins = {
    '0 a 5 anos': (0, 5),
    '6 a 10 anos': (5, 10),
    '11 a 15 anos': (10, 15),
    '16 a 20 anos': (15, 20),
    '21 a 25 anos': (20, 25),
    '26 a 30 anos': (25, 30),
    'mais de 31 anos': (30, 50)       
}

# Gera a lista de bins e labels
bins = [0] + [v[1] for v in inst_time_bins.values()]
labels = list(inst_time_bins.keys())

# Garante que estamos trabalhando com uma cópia
temp_instit = temp_instit.copy()

# Cria a coluna de faixa etária
temp_instit['inst_time_bin'] = pd.cut(temp_instit['institut_time_years'],bins=bins,labels=labels,right=False)

# Deleta a coluna 'institut_time_years' original
temp_instit = temp_instit.drop(columns=['institut_time_years'])

# Filtra apenas as linhas com faixa etária atribuída (i.e., que não são NaN) e
# Exibe a contagem de residentes por faixa etária
temp_instit = temp_instit[temp_instit['inst_time_bin'].notna()].value_counts().sort_index()
temp_instit

# %%
# Cria um DataFrame a partir da série de contagem
temp_instit = temp_instit.reset_index()
temp_instit
# %%
# Renomeia as colunas
temp_instit = temp_instit.rename(columns={'institution_name': 'ILPI', 'inst_time_bin': 'Faixa Tempo Instituíção', 'count': 'Número de Residentes'}) 
temp_instit

# %%
# Salvando a tabela de idades
salvar_tabela_como_imagem(
    temp_instit,
    '../tables/05_tabela_faixa_tempo_institucionalização.png',
    largura_max_coluna=25
)

# %%

# Configura o tamanho do gráfico
plot_bar_flex_unificado(temp_instit,
                        #col_categoria='Faixa Tempo Instituíção',
                        col_valor='Número de Residentes',
                        col_grupo='Faixa Tempo Instituíção',
                        title='Tempo de Institucionalização dos Residentes por ILPI',
                        xlabel='Tempo de instituíção', ylabel='Número de residentes',
                        filename='../plots/05_grafico_tempo_instit_por_ILPI.png',
                        orientation='v',
                        value_format='absolute',
                        show_values=True,
                        show_text=False
)

# Criando gráfico tempo institucionalização por ILPI absoluto
plot_bar_flex_unificado(temp_instit,
                        #col_categoria='Faixa Tempo Instituíção',
                        col_valor='Número de Residentes',
                        col_grupo='Faixa Tempo Instituíção',
                        title='Tempo de Institucionalização Percentual dos Residentes por ILPI ',
                        xlabel='Tempo de instituíção', ylabel='Número de residentes',
                        filename='../plots/05_grafico_proporcao_tempo_instit_por_ILPI.png',
                        orientation='v',
                        value_format='percent',
                        show_values=True,
                        show_text=False
)

# %%
## --------------------
## ----- 6 - Suporte Familiar
## --------------------

# Cria um DF com suporte familiar
suporte = df[['institution_name', 'family_support']]
suporte.head(20)
# %%
# Filtra apenas as linhas que existam dados de suporte familiar
suporte_gruped = suporte[suporte['family_support'].notna()].astype({'family_support':'int64'})
suporte_gruped.head(20)
#%%
# %%
# Agrupa por 'family_support', usa .size() para contar quantas vezes cada suporte aparece e
# renomeia a coluna de contagem para 'total'
suporte_gruped = suporte.groupby('family_support').size().reset_index(name='total')
suporte_gruped
# %%
# Calcula proporção de cada raça
suporte_gruped['proporcao'] = suporte_gruped['total'] / suporte_gruped['total'].sum()
suporte_gruped['proporcao'] = (suporte_gruped['proporcao']).round(2)
suporte_gruped
# %%
# Define um dicionário para mapear os códigos de raça para strings
suporte_gruped['family_support'] = suporte_gruped['family_support'].replace({ 
    1: 'Sim',
    2: 'Não',
    3: 'Não consta no prontuário',
})

suporte_gruped
# %%
# Salva a tabela geral de suporte familiar
salvar_tabela_como_imagem(
    suporte_gruped,
    '../tables/06_tabela_suporte_famil_geral.png',
    largura_max_coluna=25,

)
# %%
# Gráfico Geral Suporte familiar absoluto
plot_bar_flex_unificado(
    suporte_gruped,
    title='Frequência do Suporte Familiar dos Residentes',
    xlabel='', ylabel='Número de residentes',
    filename='../plots/06_grafico_suporte_familiar_absoluto.png',
    orientation='v',
    value_format='absolute',
    show_values=True,
    show_text=False,
    col_categoria='family_support',
    col_valor='total',
)
# %%
# Agrupa por 'institutuin_name' e 'family_support', usa .size() para contar quantas vezes cada suporte aparece e
# renomeia a coluna de contagem para 'total'
suporte_inst = suporte.groupby(['institution_name', 'family_support']).size().reset_index(name='total')
suporte_inst
# %%
# Calcula proporçao de cada suporte dentro de cada ILPI
suporte_inst['proporcao'] = suporte_inst['total'] / suporte_inst.groupby('institution_name')['total'].transform('sum')
suporte_inst['proporcao'] = (suporte_inst['proporcao']).round(2)
suporte_inst
# %%
# Define um dicionário para mapear os códigos de raça para strings
suporte_inst['family_support'] = suporte_inst['family_support'].replace({ 
    1: 'Sim',
    2: 'Não',
    3: 'Não consta no prontuário',
})

suporte_inst
# %%
# Salvando a tabela de suporte familiar por ILPI
salvar_tabela_como_imagem(
    suporte_inst,
    '../tables/06_tabela_suporte_famil_por_ILPI.png',
    largura_max_coluna=25,
)
# %%
# Gráfico Suporte familiar por ILPI absoluto
plot_bar_flex_unificado(
    suporte_inst,
    title='Frequência do Suporte Familiar dos Residentes por ILPI',
    xlabel='', ylabel='Número de residentes',
    filename='../plots/06_grafico_suporte_familiar_por_ILPI.png',
    orientation='v',
    value_format='absolute',
    show_values=True,
    show_text=False,
    col_categoria='institution_name',
    col_valor='total',
)
# %%
# Gráfico Suporte familiar por ILPI percentagem
plot_bar_flex_unificado(
    suporte_inst,
    title='Frequência do Suporte Familiar dos Residentes por ILPI',
    xlabel='', ylabel='Número de residentes',
    filename='../plots/06_grafico_suporte_familiar_por_ILPI_percent.png',
    orientation='v',
    value_format='percent',
    show_values=True,
    show_text=False,
    col_categoria='institution_name',
    col_valor='total',
)
# %%
## --------------------
## ----- 7 - Grau de dependência
## --------------------

# Cria um DF com grau_dependencia
grau_dependencia = df[['institution_name', 'dependence_degree']]
grau_dependencia.head(20)
# %%
# Filtra apenas as linhas que existam dados de grau_dependencia
grau_dependencia_gruped = grau_dependencia[grau_dependencia['dependence_degree'].notna()].astype({'dependence_degree':'int64'})
grau_dependencia_gruped.head(20)
#%%
# Agrupa por 'dependence_degree', usa .size() para contar quantas vezes cada grau_dependencia aparece e
# renomeia a coluna de contagem para 'total'
grau_dependencia_gruped = grau_dependencia.groupby('dependence_degree').size().reset_index(name='total')
grau_dependencia_gruped
# %%
# Calcula proporção de cada grau de dependencia
grau_dependencia_gruped['proporcao'] = grau_dependencia_gruped['total'] / grau_dependencia_gruped['total'].sum()
grau_dependencia_gruped['proporcao'] = (grau_dependencia_gruped['proporcao']).round(2)
grau_dependencia_gruped
# %%
# Define um dicionário para mapear os códigos grau de dependencia para strings
grau_dependencia_gruped['dependence_degree'] = grau_dependencia_gruped['dependence_degree'].replace({ 
    1: 'Independente',
    2: 'Parcialmente dependente',
    3: 'Totalmente dependente',
})

grau_dependencia_gruped
# %%
# Salva a tabela geral de grau_dependencia 
salvar_tabela_como_imagem(
    grau_dependencia_gruped,
    '../tables/07_tabela_grau_dependencia_geral.png',
    largura_max_coluna=25,

)
# %%
# Gráfico Geral grau_dependencia absoluto
plot_bar_flex_unificado(
    grau_dependencia_gruped,
    title='Frequência do Grau de Dependência dos Residentes',
    xlabel='', ylabel='Número de residentes',
    filename='../plots/07_grafico_grau_dependencia_familiar_absoluto.png',
    orientation='v',
    value_format='absolute',
    show_values=True,
    show_text=False,
    col_categoria='dependence_degree',
    col_valor='total',
)
# %%
# Agrupa por 'institutuin_name' e 'dependence_degree', usa .size() para contar quantas vezes cada suporte aparece e
# renomeia a coluna de contagem para 'total'
grau_dependencia_inst = grau_dependencia.groupby(['institution_name', 'dependence_degree']).size().reset_index(name='total')
grau_dependencia_inst
# %%
# Calcula proporçao de cada grau_dependencia dentro de cada ILPI
grau_dependencia_inst['proporcao'] = grau_dependencia_inst['total'] / grau_dependencia_inst.groupby('institution_name')['total'].transform('sum')
grau_dependencia_inst['proporcao'] = (grau_dependencia_inst['proporcao']).round(2)
grau_dependencia_inst
# %%
# Define um dicionário para mapear os códigos de raça para strings
grau_dependencia_inst['dependence_degree'] = grau_dependencia_inst['dependence_degree'].replace({ 
    1: 'Sim',
    2: 'Não',
    3: 'Não consta no prontuário',
})

grau_dependencia_inst
# %%
# Salvando a tabela de grau_dependencia familiar por ILPI
salvar_tabela_como_imagem(
    grau_dependencia_inst,
    '../tables/07_tabela_grau_dependencia_famil_por_ILPI.png',
    largura_max_coluna=25,
)
# %%
# Gráfico grau_dependencia familiar por ILPI absoluto
plot_bar_flex_unificado(
    grau_dependencia_inst,
    title='Frequência do grau_dependencia Familiar dos Residentes por ILPI',
    xlabel='', ylabel='Número de residentes',
    filename='../plots/07_grafico_grau_dependencia_familiar_por_ILPI.png',
    orientation='v',
    value_format='absolute',
    show_values=True,
    show_text=False,
    col_categoria='institution_name',
    col_valor='total',
)
# %%
# Gráfico grau_dependencia familiar por ILPI percentagem
plot_bar_flex_unificado(
    grau_dependencia_inst,
    title='Frequência do grau_dependencia Familiar dos Residentes por ILPI',
    xlabel='', ylabel='Número de residentes',
    filename='../plots/07_grafico_grau_dependencia_familiar_por_ILPI_percent.png',
    orientation='v',
    value_format='percent',
    show_values=True,
    show_text=False,
    col_categoria='institution_name',
    col_valor='total',
)
# %%
## --------------------
## ----- 8 - Tipo de Vínculo
## --------------------
# %%
# Define um dicionário para mapear os códigos tipos de vinculo para strings
vinculo_cols = { 
    'link_type___1': 'Privado',
    'link_type___2': 'Filantrópico',
    'link_type___3': 'Convênio com a Prefeitura',
}
# %%
# Cria um DF com vínculo com ILPI
vinculo_instit = processa_multiresposta(df, vinculo_cols, 'Vínculo com a ILPI')
vinculo_instit.head(20)
# %%
# Agrupa por 'link_type', usa .size() para contar quantas vezes cada vinculo_instit aparece e
# renomeia a coluna de contagem para 'total'
vinculo_instit_gruped = vinculo_instit.groupby('Vínculo com a ILPI').size().reset_index(name='total')
vinculo_instit_gruped.head()
# %%
# Calcula proporção de cada vinculo
vinculo_instit_gruped['proporcao'] = vinculo_instit_gruped['total'] / vinculo_instit_gruped['total'].sum()
vinculo_instit_gruped['proporcao'] = (vinculo_instit_gruped['proporcao']).round(2)
vinculo_instit_gruped
# %%
# Salva a tabela geral de vinculo_instit 
salvar_tabela_como_imagem(
    vinculo_instit_gruped,
    '../tables/08_tabela_vinculo_instit_geral.png',
    largura_max_coluna=25,

)
# %%
# Gráfico Geral tipo de vinculo absoluto
plot_bar_flex_unificado(
    vinculo_instit_gruped,
    title='Frequência do Vinculo dos Residentes',
    xlabel='Tipo de vínculo', ylabel='Número de residentes',
    filename='../plots/08_grafico_tipos_vinculo_absoluto.png',
    orientation='v',
    value_format='absolute',
    show_values=True,
    show_text=False,
    col_categoria='Vínculo com a ILPI',
    col_valor='total',
)
# %%
# Agrupa por 'institutuin_name' e 'link_type', usa .size() para contar quantas vezes cada suporte aparece e
# renomeia a coluna de contagem para 'total'
vinculo_inst = vinculo_instit.groupby(['ILPI', 'Vínculo com a ILPI']).size().reset_index(name='total')
vinculo_inst
# %%
# Calcula proporçao de cada vinculo dentro de cada ILPI
vinculo_inst['proporcao'] = vinculo_inst['total'] / vinculo_inst.groupby('ILPI')['total'].transform('sum')
vinculo_inst['proporcao'] = (vinculo_inst['proporcao']).round(2)
vinculo_inst
# %%
# Salvando a tabela de vinculo familiar por ILPI
salvar_tabela_como_imagem(
    vinculo_inst,
    '../tables/08_tabela_vinculo_famil_por_ILPI.png',
    largura_max_coluna=25,
)
# %%
# Gráfico vinculo familiar por ILPI absoluto
plot_bar_flex_unificado(
    vinculo_inst,
    title='Frequência do Vínculo Familiar dos Residentes por ILPI',
    xlabel='', ylabel='Número de residentes',
    filename='../plots/08_grafico_vinculo_familiar_por_ILPI.png',
    orientation='v',
    value_format='absolute',
    show_values=True,
    show_text=False,
    col_categoria='ILPI',
    col_valor='total',
)
# %%
# Gráfico vinculo familiar por ILPI percentagem
plot_bar_flex_unificado(
    vinculo_inst,
    title='Frequência do vinculo Familiar dos Residentes por ILPI',
    xlabel='', ylabel='Número de residentes',
    filename='../plots/08_grafico_vinculo_familiar_por_ILPI_percent.png',
    orientation='v',
    value_format='percent',
    show_values=True,
    show_text=False,
    col_categoria='ILPI',
    col_valor='total',
)
# %%
## --------------------
## ----- 9 - Fonte de Renda
## --------------------

# Cria um DF com fonte de renda 
fonte_renda = df[['institution_name', 'elder_income_source']]
fonte_renda.head(20)
# %%
# Filtra apenas as linhas que existam dados de fonte de renda 
fonte_renda_gruped = fonte_renda[fonte_renda['elder_income_source'].notna()].astype({'elder_income_source':'int64'})
fonte_renda_gruped.head(20)
#%%
# Agrupa por 'elder_income_source', usa .size() para contar quantas vezes cada fonte_renda_gruped aparece e
# renomeia a coluna de contagem para 'total'
fonte_renda_gruped = fonte_renda_gruped.groupby('elder_income_source').size().reset_index(name='total')
fonte_renda_gruped
# %%
# Calcula proporção de cada fonte de renda
fonte_renda_gruped['proporcao'] = fonte_renda_gruped['total'] / fonte_renda_gruped['total'].sum()
fonte_renda_gruped['proporcao'] = (fonte_renda_gruped['proporcao']).round(2)
fonte_renda_gruped
# %%
# Define um dicionário para mapear os códigos de fonte de renda para strings
fonte_renda_gruped['elder_income_source'] = fonte_renda_gruped['elder_income_source'].replace({ 
    1: 'Aposentadoria/pensão',
    2: 'Benefíco de Prestação',
    3: 'Bolsa Família',
    4: 'Nenhum',
    5: 'Não sabe'
})

fonte_renda_gruped
# %%
# Salva a tabela geral de fonte_renda_gruped
salvar_tabela_como_imagem(
    fonte_renda_gruped,
    '../tables/09_tabela_fonte_renda_geral.png',
    largura_max_coluna=25,

)
# %%
# Gráfico Geral Fonte de Renda absoluto
plot_bar_flex_unificado(
    fonte_renda_gruped,
    title='Frequência Fonte de Renda dos Residentes',
    xlabel='', ylabel='Número de residentes',
    filename='../plots/09_grafico_fonte_renda_absoluto.png',
    orientation='v',
    value_format='absolute',
    show_values=True,
    show_text=False,
    col_categoria='elder_income_source',
    col_valor='total',
)
# %%
# %%
# Agrupa por 'institutuin_name' e 'lelder_income_source', usa .size() para contar quantas vezes cada suporte aparece e
# renomeia a coluna de contagem para 'total'
fonte_renda_inst = fonte_renda.groupby(['institution_name', 'elder_income_source']).size().reset_index(name='total')
fonte_renda_inst
# %%
# Calcula proporçao de cada fonte_renda dentro de cada ILPI
fonte_renda_inst['proporcao'] = fonte_renda_inst['total'] / fonte_renda_inst.groupby('institution_name')['total'].transform('sum')
fonte_renda_inst['proporcao'] = (fonte_renda_inst['proporcao']).round(2)
fonte_renda_inst
# %%
# Define um dicionário para mapear os códigos de fonte de renda para strings
fonte_renda_inst['elder_income_source'] = fonte_renda_inst['elder_income_source'].replace({ 
    1: 'Aposentadoria/pensão',
    2: 'Benefíco de Prestação',
    3: 'Bolsa Família',
    4: 'Nenhum',
    5: 'Não sabe'
})

fonte_renda_inst
# %%
# Salvando a tabela de fonte_renda familiar por ILPI
salvar_tabela_como_imagem(
    fonte_renda_inst,
    '../tables/09_tabela_fonte_renda_famil_por_ILPI.png',
    largura_max_coluna=25,
)
# %%
# Gráfico fonte_renda familiar por ILPI absoluto
plot_bar_flex_unificado(
    fonte_renda_inst,
    title='Frequência da Fonte de Renda dos Residentes por ILPI',
    xlabel='', ylabel='Número de residentes',
    filename='../plots/09_grafico_fonte_renda_familiar_por_ILPI.png',
    orientation='v',
    value_format='absolute',
    show_values=True,
    show_text=False,
    col_categoria='institution_name',
    col_valor='total',
)
# %%
# Gráfico fonte_renda familiar por ILPI percentagem
plot_bar_flex_unificado(
    fonte_renda_inst,
    title='Frequência da Fonte de Renda dos Residentes por ILPI',
    xlabel='', ylabel='Número de residentes',
    filename='../plots/09_grafico_fonte_renda_familiar_por_ILPI_percent.png',
    orientation='v',
    value_format='percent',
    show_values=True,
    show_text=False,
    col_categoria='institution_name',
    col_valor='total',
)
# %%
## --------------------
## ----- 10 - Medicamentos
## --------------------

# Criar um DF para registro de medicamentos

medic_registro = df[['institution_name', 'recorded']]
medic_registro.head(20)
# %%

# Filtra apenas as linhas que existam dado recorded
medic_registro_grouped = medic_registro[medic_registro['recorded'].notna()].astype({'recorded': 'int64'})
medic_registro_grouped.head(20)
# %%

# Agrupa por 'recorded', usa .size() para contar quantas vezes cada 'recorded' aparece e
# renomeia a coluna de contagem para 'total'
medic_registro_grouped = medic_registro_grouped.groupby('recorded').size().reset_index(name='total')
medic_registro_grouped
# %%
# Calcula a proporção de cada recorded
medic_registro_grouped['proporcao'] = medic_registro_grouped['total'] / medic_registro_grouped['total'].sum()
medic_registro_grouped['proporcao'] = medic_registro_grouped['proporcao'].round(2)
medic_registro_grouped
# %%

# Mapeia a coluna recorded e atribui valor "sim e não"
medic_registro_grouped['recorded'] = medic_registro_grouped['recorded'].map({1: 'Sim', 0: 'Não'})
medic_registro_grouped
# %%
salvar_tabela_como_imagem(
    medic_registro_grouped,
    '../tables/10_tabela_registro_medic.png',
    largura_max_coluna=25
)

# %%

# Plotagem 

plot_bar_flex_unificado(
    medic_registro_grouped,
    title='Frequência de Registro de Medicamentos do Residente',
    xlabel='',ylabel='Registro',
    filename='../plots/10_gráfico_registro_medicamentos.png',
    orientation='v', 
    value_format='absolute',
    col_valor='total',
    col_categoria='recorded',
    show_values=True,
    show_text=False
)
# %%
# Agrupa por 'recorded', usa .size() para contar quantas vezes cada 'recorded' aparece e
# renomeia a coluna de contagem para 'total'
medic_registro_instit = medic_registro.groupby(['institution_name', 'recorded']).size().reset_index(name='total')
medic_registro_instit
# %%
# Calcula a proporção de cada recorded para cada ILPI
medic_registro_instit['proporcao'] = medic_registro_instit['total'] / medic_registro_instit.groupby('institution_name')['total'].transform('sum')
medic_registro_instit['proporcao'] = medic_registro_instit['proporcao'].round(2)
medic_registro_instit
# %%
# Salva a tabela de registro de medicamentos por ILPI
salvar_tabela_como_imagem(
    medic_registro_instit,
    '../tables/10_tabela_registro_medic_por_ILPI.png',
    largura_max_coluna=25,
)
# %%
# Gráfico registro medicamentos por ILPI percentagem
plot_bar_flex_unificado(
    fonte_renda_inst,
    title='Frequência do Registro de Medicamentos dos Residentes por ILPI',
    xlabel='', ylabel='Número de residentes',
    filename='../plots/09_grafico_registro_medic_por_ILPI_percent.png',
    orientation='v',
    value_format='percent',
    show_values=True,
    show_text=False,
    col_categoria='institution_name',
    col_valor='total',
)
# %%
# Usar a funçao para montar uma tabela com os medicamentos
medic_por_residente = extrair_medicamentos(df)
medic_por_residente.head(20)
# %%
# # Agrupa por 'ILPI' e 'lelder_income_source', usa .size() para contar quantas vezes cada suporte aparece e
# renomeia a coluna de contagem para 'total'
contagem_medic_por_residente = medic_por_residente.groupby(['ILPI','CPF','Nome Completo']).size().reset_index(name='total')
contagem_medic_por_residente.head(20)

# %%
## --------------------
##  Morbidades
## --------------------
# Definindo um dicionário para morbidades binárias
morb_dict = {
    "morbidities___1" : "Hipertensão Arterial",
    "morbidities___2" : "Diabetes Mellitus",
    "morbidities___3" : "Hipercolesterolemia",
    "morbidities___4" : "Doença na coluna",
    "morbidities___5" : "Insuficiência cardíaco",
    "morbidities___6" : "Infarto",
    "morbidities___7" : "Insuficiência renal",
    "morbidities___8" : "Câncer",
    "morbidities___9" : "Enfisema pulmonar",
    "morbidities___10":	"Asma",
    "morbidities___11":	"Bronquite",
    "morbidities___12":	"Transtorno Mental",
    "morbidities___13":	"Osteoporose",
    "morbidities___14":	"Artrite",
    "morbidities___15":	"Demência",
    "morbidities___16":	"Alzheimer",
    "morbidities___17":	"Parkinson",
    "morbidities___18":	"Etilismo",
    "morbidities___19":	"Tabagismo",
    "morbidities___20":	"Usuário de drogas",
}

# %%
# Extraindo morbidades, outras morbidades e soma
df_morbidades = extrair_morbidades(df, morb_dict)
# Exibindo o DataFrame resultante   
df_morbidades
# %%
## --------------------
##  - COMPONENTES DE FRAGILIDADE
## --------------------


#amount_weight_loss_dict ={1: "de 1 a 3 kg",2: "mais de 3 kg",}
#elder_strenght_dict = {1:"Sim",2:"Não"}	
#elder_hospitalized_dict = {1: "nenhuma", 2: "1 a 2 vezes", 3: "3 vezes", 4: "4 ou mais",}
#elder_difficulties_dict = {1:"nenhuma", 2: "alguma",3: "não consegue",}
#elder_mobility_dict = {1: "Sim",2: "Não"}	
#basic_activities_diffic_dict = 	{1:	"Sim",2: "Não"}	
#falls_number_dict = {1: " nenhuma", 2: "1 a 3 quedas", 3: "4 e mais",}


condicao_atencao = {
    'amount_weight_loss':(lambda x: x == 1),
    'elder_strenght':(lambda x: x == 2),
    'elder_hospitalized':(lambda x: x ==1),
    'elder_difficulties':(lambda x: x == 1),
    'elder_mobility':(lambda x: x == 2),
    'basic_activities_diffic':(lambda x: x ==1),
    'falls_number':(lambda x: x ==1)
}

condicao_alerta = {
    'amount_weight_loss':(lambda x: x == 1),
    'elder_strenght':(lambda x: x == 1),
    'elder_hospitalized':(lambda x: x in [2, 3] ),
    'elder_difficulties':(lambda x: x == 2),
    'elder_mobility':(lambda x: x == 1),
    'basic_activities_diffic':(lambda x: x == 1),
    'falls_number':(lambda x: x == 2)
}

condicao_critica = {
    'amount_weight_loss':(lambda x: x == 2),
    'elder_strenght':(lambda x: x == 1),
    'elder_hospitalized':(lambda x: x in [3, 4]),
    'elder_difficulties':(lambda x: x == 1),
    'elder_mobility':(lambda x: x == 1),
    'basic_activities_diffic':(lambda x: x ==1),
    'falls_number':(lambda x: x == 3)
}
# %%



# %%
resultado, resumo = classificar_risco(df, condicao_critica, condicao_alerta, condicao_atencao)

# %%
from IPython.display import display, HTML

# Exibe o resultado com cores
display(HTML(resultado.to_html(escape=False)))

# Mostra o resumo correto
display(HTML(resumo.to_html(escape=False)))

# %%
salvar_tabela_como_imagem(
    resumo,
    '../tables/12_tabela_resummo_score_fragilidade.png',
    titulo='Score de Fragilidade do Residente por ILPI',
    largura_max_coluna=25
)
# %%
