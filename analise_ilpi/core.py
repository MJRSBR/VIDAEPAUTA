import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns

pd.set_option('display.max_colwidth', None)

def gerar_grafico_binario(df, coluna_original, nome_coluna_final, titulo, nome_arquivo):
    df_temp = (
        df[['institution_name', coluna_original]]
        .assign(df_filtered=df[coluna_original].map({1: 'Sim', 2: 'Não'}))
        [['institution_name', 'df_filtered']]
        .rename(columns={'institution_name': 'ILPI', 'df_filtered': nome_coluna_final})
    )

    counts = df_temp[nome_coluna_final].value_counts()
    plt.figure(figsize=(10, 6))
    counts.plot(kind='barh', color=['blue', 'orange'])
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(titulo)
    plt.xlabel('Número de Instituições')
    plt.text(0.02, 1.3, '* Uma das instituições é composta por unidades de moradia',
             color='red', ha='left', va='bottom', wrap=True)
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(nome_arquivo)
    plt.show()

    return df_temp

def processar_multiplas_colunas(df, colunas_opcoes, mapeamento_texto, nova_coluna, nome_final='ILPI'):
    df_resultado = (
        df[['institution_name'] + colunas_opcoes]
        .assign(**{
            nova_coluna: sum(
                df[col].map(lambda x, texto=texto: texto if x == 1 else '') 
                for col, texto in zip(colunas_opcoes, mapeamento_texto)
            )
        })
        .assign(**{
            nova_coluna: lambda x: x[nova_coluna].str.lstrip(', ')
        })
        .rename(columns={'institution_name': nome_final})
        [[nome_final, nova_coluna]]
    )
    return df_resultado

def extrair_profissionais(df, mapeamento):
    return pd.concat([
        df[df[col_prof] >= 1][['institution_name', col_dias]]
        .assign(profissional=prof)
        .rename(columns={'institution_name': 'ILPI', col_dias: 'Dias_por_mes'})
        .assign(Dias_por_mes=lambda x: x['Dias_por_mes'].round(1))
        [['ILPI', 'profissional', 'Dias_por_mes']]
        for prof, col_prof, col_dias in mapeamento
    ]).dropna().sort_values(by=['ILPI', 'profissional']).reset_index(drop=True)

def gerar_barh(df, coluna, titulo, nome_arquivo, cor=['blue', 'orange']):
    plt.figure(figsize=(10, 6))
    df.groupby(coluna).size().plot(kind='barh', color=cor)
    plt.gca().spines[['top', 'right']].set_visible(False)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(titulo)
    plt.xlabel('Número de Instituições')
    plt.text(0.02, 1.3, '* Uma das instituições é composta por unidades de moradia',
             color='red', ha='left', va='bottom', wrap=True)
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(nome_arquivo)
    plt.show()
