# %%
# Bibliotecas
# --------------------
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
#from matplotlib.backends.backend_pdf import PdfPages # Salvar como PDF
#from reportlab.lib.pagesizes import letter, landscape
#from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
#from reportlab.lib import colors
# %%
# ---------------------
# Leitura dos dados
# ---------------------
df = pd.read_csv('data/base_ilpi.csv')
 # %%
# --------------------
# Configurações Globais dos Gráficos
# ---------------------
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
# Ajustar a exibição do pandas para mostrar mais caracteres
pd.set_option('display.max_colwidth', None)  # Permite exibir a coluna inteira


# ------------------------------
# Funções utilitárias
# ------------------------------

def criar_diretorios():
    os.makedirs('../tables', exist_ok=True)
    os.makedirs('../plots', exist_ok=True)

#def salvar_tabela_pdf_reportlab(df, filename, title="Tabela"):
#    """
#    Salva uma tabela em PDF usando reportlab (visual profissional).
#    """
#    pdf = SimpleDocTemplate(
#        filename,
#        pagesize=landscape(letter)
#    )
#
#    data = [df.columns.tolist()] + df.values.tolist()
#
#    table = Table(data)
#    style = TableStyle([
#        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4E79A7")),
#        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
#        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#        ('GRID', (0, 0), (-1, -1), 1, colors.black)
#    ])
#    table.setStyle(style)
#
#    elementos = [table]
#    pdf.build(elementos)    

# usando lib matplotlib
matplotlib.rc('font', size=10)

def salvar_tabela_como_imagem(df, caminho_arquivo, titulo=None):
    """
    Salva um DataFrame como uma imagem (PNG) de tabela bem formatada.

    Parâmetros:
    - df: DataFrame do pandas.
    - caminho_arquivo: string com o caminho e nome do arquivo (ex: 'output/tabela.png').
    - titulo: opcional, string com o título da tabela.
    """
    fig, ax = plt.subplots(figsize=(len(df.columns) * 2.5, len(df) * 0.6 + 1))

    ax.axis('off')

    # Cria a tabela
    tabela = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center'
    )

    # Ajusta estilo da tabela
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.scale(1, 1.5)

    # Estilo de cabeçalho
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


def plot_barh(data, title, xlabel, filename, color=['#4E79A7', '#F28E2B'], nota=True):
    """Gera um gráfico de barras horizontal.
    Parâmetros:
    - data: DataFrame do pandas.
    - title: string com o título da tabela.
    - xlabel: string com a legenda eixo x
    - filename: string com o caminho e nome do arquivo (ex: 'plots/exemplo.png )
    """
    data.plot(kind='barh', color=color)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(title)
    if nota:
        plt.text(0.02, 0.3, '* Uma das instituições é composta por unidades de moradia',
                 color='red', ha='left', va='bottom', wrap=True)
    plt.xlabel(xlabel)
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

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


def processa_binario(df, coluna, legenda, rename_dict):
    """Processa variáveis binárias para análise."""
    temp = (df[['institution_name', coluna]]
                # Cria uma coluna cujo nome é o valor da variável legenda 
                # populacionando com o mapeamento
                .assign(**{legenda: df[coluna].map(rename_dict)}) 
                .rename(columns={'institution_name': 'ILPI'})
                .drop(columns=coluna)
                )
    return temp

# Exemplo de uso
# rename_dict = {1: 'Sim', 0: 'Não'}
#
#tabela_camas = processa_binario(
#    df,
#    'residents_bedroom',
#    'Camas segundo a Norma',
#    rename_dict
#)

#print(tabela_camas)

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


def processa_multiresposta(df, colunas_dict, legenda):
    """Processa variáveis de múltiplas respostas (checkbox)."""
    resultado = (
        df.assign(**{
            legenda: df.apply(
                lambda row: ', '.join(
                    [desc for col, desc in colunas_dict.items() if row[col] == 1]
                ) if any(row[col] == 1 for col in colunas_dict) else 'Nenhum',
                axis=1
            )
        })[['institution_name', legenda]]
        .rename(columns={'institution_name': 'ILPI'})
    )
    return resultado