# src/analise_ilpi_ufg.py
# %%
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator

# Configurações globais
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
# %%

# ------------------------------
# Funções utilitárias
# ------------------------------

def criar_diretorios():
    os.makedirs('../output', exist_ok=True)
    os.makedirs('../plots', exist_ok=True)


def plot_barh(data, title, xlabel, filename, note=None, color=['#4E79A7', '#F28E2B']):
    data.plot(kind='barh', color=color)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(title)
    if note:
        plt.text(0.02, 0.3, note, color='red', ha='left', va='bottom', wrap=True)
    plt.xlabel(xlabel)
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(f'../plots/{filename}')
    plt.show()


# ------------------------------
# Funções de Processamento
# ------------------------------

def processar_binario(df, coluna, titulo_coluna):
    df_binario = (
        df[['institution_name', coluna]]
        .assign(mapeado=df[coluna].map({1: 'Sim', 2: 'Não'}))
        [['institution_name', 'mapeado']]
        .rename(columns={'institution_name': 'ILPI', 'mapeado': titulo_coluna})
    )
    return df_binario

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


def contar_e_plotar(data, coluna, titulo, xlabel, filename, note=None, color=['#4E79A7', '#F28E2B']):
    contagem = data[coluna].value_counts()

    contagem.plot(kind='barh', color=color)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(titulo)

    if note:
        plt.text(
            0.02, 0.3, note,
            color='red', ha='left', va='bottom', wrap=True
        )

    plt.xlabel(xlabel)
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(f'../output/{filename}')
    plt.show()

# ------------------------------
# Função principal
# ------------------------------

# %%
df = pd.read_csv('../../../data/base_ilpi.csv')

camas = processar_binario(df, 'residents_bedroom', 'Camas segundo a Norma?')

camas.to_markdown('../output/camas.md', index=False)

contar_e_plotar(
    camas,
    'Camas segundo a Norma?',
    'Distribuição de Camas segundo a Norma',
    'ILPIs',
    '01_camas_norma.png',
    note='* Uma das instituições é composta por unidades de moradia'
)
# Outras análises seguem o mesmo padrão...
print("Análises concluídas!")
# %%
