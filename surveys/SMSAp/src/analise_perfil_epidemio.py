# %%
import os
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

# %%
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


def plot_barh(data, title, xlabel, ylabel, filename, obs=2, show_text=True):
    """
    Gera um gráfico de barras horizontal.

    Parâmetros:
    - data: DataFrame do pandas (colunas devem corresponder às notas).
    - title: string com o título da tabela.
    - xlabel: string com a legenda eixo x.
    - ylabel: string com a legenda eixo y.
    - filename: string com o caminho e nome do arquivo (ex: 'plots/exemplo.png')
    - obs: número de observações (ex: 4).
    - show_text: se True, exibe observação adicional no gráfico.
    """
    # Paleta de cores personalizada (adicionar mais se precisar)
    all_colors = ["#4E5EA7", '#F28E2B', "#AF3739", '#76B7B2', '#59A14F', '#EDC948']
    
    # Seleciona cores de acordo com o número de notas
    color = all_colors[:obs] if isinstance(all_colors, list) else all_colors
    
    data.plot(kind='barh', color=color)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(title)
    
    if show_text:
        plt.text(0.02, 0.3, '* Uma das instituições é composta por unidades de moradia',
                 color='red', ha='left', va='bottom', wrap=True)
        
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
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
## ---- Gênero
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
gender_prop
# %%

# Salvando como imagem
salvar_tabela_como_imagem(
    gender,
    '../tables/01_tabela_genero_abs.png',
    largura_max_coluna=25
)

# Salvando a tabela de porcentagens
salvar_tabela_como_imagem(
    gender_prop,
    '../tables/01_tabela_genero_prop.png',
    largura_max_coluna=25
)
# %%
# Gráfico 01 -- Gênero dos Residentes da ILPI

plot_barh(gender_prop.set_index('institution_name'), 
          title='Gênero dos Residentes da ILPI', 
          xlabel='Proporção', ylabel='ILPIs',
          filename='../plots/01_grafico_genero_perc.png')

# %%

## --------------------
## ---- Idade 
## -------------------

# Cria um DataFrame para a idade dos residentes
df_idade = df[['institution_name', 'elder_age']]

# Filtra apenas as linhas com idade dos residentes
df_idade = df_idade[df_idade['elder_age'].notna()].astype({'elder_age': 'int64'})
df_idade
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
idade
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

# Plot
pivot_df.plot(kind='bar', stacked=True, figsize=(12, 6), color=custom_colors)

# Eixos e legenda
plt.xlabel('ILPI')
plt.ylabel('Número de Residentes')
plt.title('Distribuição de Faixa Etária por ILPI')
plt.xticks(rotation=0)
plt.legend(title='Faixa Etária', bbox_to_anchor=(1.05, 1), loc='upper left')

# Adiciona legenda para a linha média
#plt.text(len(pivot_df) - 0.6, media_residentes + 0.5, f'Média = {media_residentes:.1f}', color='black')

# Salvar e exibir
plt.tight_layout()
plt.savefig('../plots/02_grafico_faixa_etaria_por_ilpi.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico de Faixa Etária por ILPI salvo como imagem.")
plt.show()
# %%
## --------------------
## ---- Raça e Cor
## -------------------

# Cria um DataFrame para a raça dos residentes
df_raca = df[['institution_name', 'race']]
df_raca
# %%
# Filtra apenas as linhas com raça dos residentes       
df_raca = df_raca[df_raca['race'].notna()].astype({'race': 'int64'})
df_raca
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
    '../tables/04_tabela_raca_geral.png', 
    largura_max_coluna=25,
)                             
# %%

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
# %%
# Criando gráfico de raça geral
plt.figure(figsize=(10, 6))
plt.bar(df_raca_grouped['race'], df_raca_grouped['total'], color=custom_colors)
plt.title('Número de Residentes por Raça')
plt.xlabel('Raça')
plt.ylabel('Total de Residentes')
plt.tight_layout()
print("✅ Gráfico de Raça dos Residentes salvo como imagem.")
plt.savefig('../plots/04_grafico_raca_geral.png', dpi=300, bbox_inches='tight')
plt.show()
          
# Criando gráfico proporção de raça 
plt.figure(figsize=(10, 6))
plt.bar(df_raca_grouped['race'], df_raca_grouped['proporcao'], color=custom_colors)
plt.title('Número de Residentes por Raça')
plt.xlabel('Raça')
plt.ylabel('Total de Residentes')
plt.tight_layout()
print("✅ Gráfico de Proporção por Raça dos Residentes salvo como imagem.")
plt.savefig('../plots/04_grafico_proporcao_raca_geral.png', dpi=300, bbox_inches='tight')
plt.show()
# %%
# Cria um DataFrame raça por ILPI
df_raca_inst = df_raca.groupby(['institution_name', 'race']).size().reset_index(name='total')
df_raca_inst
# %%
# Calcula proporção dentro de cada instituição
df_raca_inst['proporcao'] = df_raca_inst['total'] / df_raca_inst['total'].sum()
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
    6: 'Não Informado',
})

df_raca_inst
# %%
# Salvando a tabela de raça 
# A tabela df_raca_grouped contém a proporção de raça geral
salvar_tabela_como_imagem(
    df_raca_inst,
    '../tables/04_tabela_raca_por_ILPI.png', 
    largura_max_coluna=25,
)                             
# %%
import seaborn as sns

# Configura o tamanho do gráfico
plt.figure(figsize=(10, 6))

# Gráfico de barras com seaborn
sns.barplot(
    data=df_raca_inst,
    x='institution_name',
    y='total',
    hue='race', 
)

# Eixos e rótulos
plt.xticks(rotation=0, ha='right')
plt.xlabel('Instituição')
plt.ylabel('Número de Residentes')
plt.title('Residentes por raça por instituição')
plt.legend(title='Raça')
#
plt.tight_layout()
print("✅ Gráfico Raça dos Residentes por ILPI salvo como imagem.")
plt.savefig('../plots/04_grafico_geral_raca_por_ILPI.png', dpi=300, bbox_inches='tight')
plt.show()
# %%          
# Criando gráfico proporção de raça 

plt.figure(figsize=(10, 6))

# Gráfico de barras com seaborn
sns.barplot(
    data=df_raca_inst,
    x='institution_name',
    y='proporcao',
    hue='race', 
)

# Eixos e rótulos
plt.xticks(rotation=0, ha='right')
plt.xlabel('Instituição')
plt.ylabel('Proporção')
plt.title('Proporção por raça por instituição')
plt.legend(title='Raça')

plt.tight_layout()
print("✅ Gráfico Raça dos Residentes por ILPI salvo como imagem.")
plt.savefig('../plots/04_grafico_proporcao_raca_por_ILPI.png', dpi=300, bbox_inches='tight')
plt.show()

# %%
## --------------------
## ---- Escolaridade
## -------------------

# Cria um DataFrame para a escolaridade dos residentes
df_escolaridade = df[['institution_name', 'scholarship']]
df_escolaridade
# %%
# Filtra apenas as linhas com escolaridade dos residentes
df_escolaridade = df_escolaridade[df_escolaridade['scholarship'].notna()].astype({'scholarship': 'int64'})
df_escolaridade
# %%
# Agrupa por 'scholarshiphip, usa .size() para contar quantas vezes cada escolaridade aparece e
# renomeia a coluna de contagem para 'total'
df_escolaridade_grouped = df_escolaridade.groupby('scholarship').size().reset_index(name='total')
df_escolaridade_grouped
# %%
# Calcula proporção de cada escolaridade
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
    '../tables/05_tabela_escolaridade_geral.png',
    largura_max_coluna=25,
                          )
# %%
# Configura o tamanho do gráfico
plt.figure(figsize=(10, 6))

# Gráfico de barras com seaborn
sns.barplot(
    data=df_escolaridade_grouped,
    x='scholarship',
    y='total',
    palette="coolwarm",
    hue='scholarship', 
)

# Eixos e rótulos
plt.xticks(rotation=45, ha='right')
plt.xlabel('Tempo de estudo')
plt.ylabel('Número de Residentes')
plt.title('Escolaridade Geral dos Residentes')

#
plt.tight_layout()
print("✅ Gráfico Escolaridade dos Residentes por ILPI salvo como imagem.")
plt.savefig('../plots/05_grafico_escolaridade_residente_por_ILPI.png', dpi=300, bbox_inches='tight')
plt.show()
# %%
# Cria um Data Frame escolaridade por ILPI
df_escolar_inst = df_escolaridade.groupby(['institution_name', 'scholarship']).size().reset_index(name='total')
df_escolar_inst
# %%
# Calcula a proporção de cada escolaridade
df_escolar_inst['proporcao'] = df_escolar_inst['total'] /  df_escolar_inst['total'].sum() 
df_escolar_inst['proporcao'] = df_escolar_inst['proporcao'].round(2)
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
     '../tables/05_tabela_escolaridade_por_ILPI.png',
    largura_max_coluna=25,
)
# %%
# Criando gráfico proporção de raça 

plt.figure(figsize=(10, 6))

# Gráfico de barras com seaborn
sns.barplot(
    data=df_escolar_inst,
    x='scholarship',
    y='proporcao',
    palette="coolwarm",
    hue='scholarship', 
)

# Eixos e rótulos
plt.xticks(rotation=0)
plt.xlabel('Tempo de estudo')
plt.ylabel('Proporção')
plt.title('Proporção por escolaridade por instituição')
#plt.legend(title='Tempo de estudo')

plt.tight_layout()
print("✅ Gráfico Escolaridade dos Residentes por ILPI salvo como imagem.")
plt.savefig('../plots/05_grafico_proporcao_escolaridade_por_ILPI.png', dpi=300, bbox_inches='tight')
plt.show()
# %%

## --------------------
## Tempo institucionalizado
## --------------------
# Estatística básica
df['institut_time_years'].describe()
# %%
# Acha os registros que provavelmente estejam errados
df.loc[df['institut_time_years'] > 30]
# %%
temp_instit = df[['institution_name', 'institut_time_years']]
temp_instit
# %%
# Filtra apenas as linhas com tempo de institucionalização
temp_instit = temp_instit[temp_instit['institut_time_years'].notna()].astype({'institut_time_years':'int64'})
temp_instit
# %%
# Agrupa por 'institut_time_years', usa .size() para contar quantas vezes cada escolaridade aparece e
# renomeia a coluna de contagem para 'total'
temp_instit_grouped = temp_instit.groupby('institut_time_years').size().reset_index(name='total')
temp_instit_grouped 
# %%
# Calcula proporcao de tempo de institucionalização
temp_instit_grouped['proporcao'] = temp_instit_grouped['total'] / temp_instit_grouped['total'].sum()
temp_instit_grouped['proporcao'] = temp_instit_grouped['proporcao'].round(2)
temp_instit_grouped
# %%
salvar_tabela_como_imagem(
    temp_instit_grouped,
    '../tables/06_tabela_tempo _institucionalização.png',
    largura_max_coluna=25,
)
# %%
# Configura o tamanho do gráfico
plt.figure(figsize=(10, 6))

# Cria gráfico de barras 

sns.barplot(
    data=temp_instit_grouped,
    x='institut_time_years',
    y='total',
    palette="coolwarm",
    hue='institut_time_years', 

)

# Remove a legenda
plt.legend().remove()

plt.title('Tempo de Institucionalização dos Residentes')
plt.xlabel('Tempo de instituíção')
plt.ylabel('Número de residentes')
plt.tight_layout()
print("✅ Gráfico Tempo de Institucão dos Residentes salvo como imagem.")
plt.savefig('../plots/06_grafico_tempo_geral_instit.png', dpi=300, bbox_inches='tight')
plt.show()

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
    '../tables/06_tabela_faixa_tempo_institucionalização.png',
    largura_max_coluna=25
)

# %%

# Pivot da tabela para formato wide (um DataFrame por faixa etária por ILPI)
pivot_df = temp_instit.pivot(index='ILPI', columns='Faixa Tempo Instituíção', values='Número de Residentes')

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
for container in ax.containers: # ax.containers percorre cada grupo de barras empilhadas
    for bar in container:
        height = bar.get_height()
        if height > 0:
            x = bar.get_x() + bar.get_width() / 2 # centraliza o texto no segmento.
            y = bar.get_y() + height / 2 # posiciona o texto no meio vertical.
            font_size = max(7, min(12, height * 0.25))  # Ajuste conforme necessário
            ax.text(
                x, y,
                f'{int(height)}',
                ha='center',
                va='center',
                color='white',
                fontweight='bold',
                fontsize=font_size
            )

# Eixos e legenda
plt.xlabel('ILPI')
plt.ylabel('Número de Residentes')
plt.title('Distribuição de Faixa Tempo de Instituíção por ILPI')
plt.xticks(rotation=0)
plt.legend(title='Faixa Tempo Instituíção', bbox_to_anchor=(1.0, 1), loc='upper left')

# Salvar e exibir
plt.tight_layout()
plt.savefig('../plots/06_grafico_faixa_tempo_instituicao_por_ilpi.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico de Faixa Tempo de Instituíção por ILPI salvo como imagem.")
plt.show()
# %%
#  Calcula os percentuais por ILPI (linha)
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
for bars, col in zip(ax.containers, pivot_df.columns): # ax.containers percorre cada grupo de barras empilhadas
    for bar, (ilpi, percent) in zip(bars, pivot_percent[col].items()):
        height = bar.get_height()
        if height > 0 and not pd.isna(percent):
            x = bar.get_x() + bar.get_width() / 2 # centraliza o texto no segmento.
            y = bar.get_y() + height / 2 # posiciona o texto no meio vertical.
            font_size = max(8, min(12, height * 0.25))  # Ajuste conforme necessário
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
plt.title('Distribuição de Faixa Tempo de Instituíção por ILPI (% por ILPI)')
plt.xticks(rotation=0)
plt.legend(title='Faixa Tempo Instituíção', bbox_to_anchor=(1.0, 1), loc='upper left')

# Salvar e exibir
plt.tight_layout()
plt.savefig('../plots/06_grafico_faixa_tempo_instituicao_por_ilpi_percentual.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico Percentual por Faixa Tempo de Instituíção por ILPI salvo como imagem.")
plt.show()
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
##  Medicamentos
## --------------------


# %%
extrair_medicamentos(df)
# %%
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
    '../tables/03_tabela_resummo_score_fragilidade.png',
    titulo='Score de Fragilidade do Residente por ILPI',
    largura_max_coluna=25
)
# %%
# Gráfico 01

plt.bar(x='institution_name', y='risco', height='total')






# %%
