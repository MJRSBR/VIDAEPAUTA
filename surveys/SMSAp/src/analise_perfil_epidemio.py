# %%
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
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

# %%
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

# %%

import re

def extrair_morbidades(df, morbidade_dict, nome_coluna_soma=None):
    """
    Filtra e retorna os dados de morbidades legíveis,
    agrupados por institution_name, full_name, cpf.
    A coluna 'other_morbidities' é normalizada (minúsculas, sem espaços),
    separando múltiplas entradas por vírgula, ponto e vírgula ou barra vertical.
    Soma final inclui morbidades binárias + textuais distintas.
    """

    morbidities_cols = list(morbidade_dict.keys())
    df[morbidities_cols] = df[morbidities_cols].apply(pd.to_numeric, errors='coerce')

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

# %%
## ---------------------
## Análises e Gráficos
## ---------------------

## ---- Gênero

# %%

## Filtra os valores válidos (1 = Masculino, 2 = Feminino)
df_filtered = df[df['sex'].isin([1, 2])].copy()

# Mapeia os valores de sexo para strings
df_filtered['sex'] = df_filtered['sex'].map({1: 'Masculino', 2: 'Feminino'})

# Transformar a coluna 'institution_name' em int    
df_filtered['institution_name'] = df_filtered['institution_name'].astype(int)

# Agrupa por institution_name e sexo e reorganiza com unstack
gender = df_filtered.groupby(['institution_name', 'sex']).size().unstack(fill_value=0).reset_index()

# 

# Remove o nome do eixo de colunas
gender.columns.name = None
gender

# %%
# Calcula a porcentagem de cada sexo por instituição
gender_percent = round(gender[['Feminino', 'Masculino']].div(gender[['Feminino', 'Masculino']].sum(axis=1), axis=0) * 100, 2)
gender_percent.insert(0, 'institution_name', gender['institution_name'])
gender_percent
# %%

# Salvando como imagem
salvar_tabela_como_imagem(
    gender,
    '../tables/01_tabela_genero_abs.png',
    largura_max_coluna=25
)

# Salvando a tabela de porcentagens
salvar_tabela_como_imagem(
    gender_percent,
    '../tables/01_tabela_genero_perc.png',
    largura_max_coluna=25
)
# %%
# Gráfico 01

plot_barh(gender_percent.set_index('institution_name').T, 
          'Gênero dos Residentes da ILPI', 
          'ILPIs', '../plots/01_tabela_genero.png'
)
# %%
## --------------------
##  Morbidades
## -------------------
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
# Extraindo morbidades
df_morbidades = extrair_morbidades(df, morb_dict)
# Exibindo o DataFrame resultante   
df_morbidades.head()
# %%
## --------------------
##  Medicamentos
## --------------------

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

def classificar_risco(df, condicao_critico, condicao_alerta, condicao_atencao, incluir_sem_risco=True):
    """
    Aplica condições de risco em uma cópia do DataFrame e retorna:
    - Um DataFrame com as colunas ['institution_name', 'cpf', 'full_name', 'risco']
    - Um DataFrame resumo com contagem por categoria de risco
    
    Parâmetros:
    - df: DataFrame original
    - condicoes_critico, condicoes_alerta, condicoes_atencao: dicionários de condições
    - incluir_sem_risco: se True, classifica como 'Sem Risco' os registros que não se encaixam em nenhuma categoria
    """

    df_copia = df.copy()
    df_copia['risco'] = None

    def aplicar_classificacao(df_local, condicoes_dict, label):
        cond = pd.Series(True, index=df_local.index)
        for col, func in condicoes_dict.items():
            cond &= df_local[col].apply(func)
        return cond.replace({True: label, False: None})

    for condicoes, label in [
        (condicao_critico, 'Crítico'),
        (condicao_alerta, 'Alerta'),
        (condicao_atencao, 'Atenção')
    ]:
        mask = aplicar_classificacao(df_copia, condicoes, label)
        df_copia.loc[mask.notna() & df_copia['risco'].isna(), 'risco'] = mask

    # Preencher com "Sem Risco", se solicitado
    if incluir_sem_risco:
        df_copia['risco'] = df_copia['risco'].fillna('Sem Risco')


# Define a ordem de severidade
    ordem_prioridade = {'Crítico': 0, 'Alerta': 1, 'Atenção': 2, 'Sem Risco': 3}

    # Agrupamento por CPF: pega a menor prioridade
    df_copia['prioridade'] = df_copia['risco'].map(ordem_prioridade)

    resultado = (
        df_copia
        .sort_values('prioridade')  # menor = mais severo
        .groupby('cpf', as_index=False)
        .first()[['institution_name', 'cpf', 'full_name', 'risco']]
    )

    # Resumo por grupo de risco
    resumo = (
    resultado
    .groupby(['institution_name', 'risco'], as_index=False)
    .size()
    .rename(columns={'size': 'total'})
)


    return resultado, resumo


# %%
from IPython.display import HTML

def classificar_risco(df, condicoes_critico, condicoes_alerta, condicoes_atencao, incluir_sem_risco=True):
    """
    Aplica condições de risco e retorna:
    - DataFrame agrupado por 'cpf' com colunas: institution_name, cpf, full_name, risco (colorido em HTML)
    - Resumo com contagem por nível de risco
    
    OBS: Para visualizar as cores no Jupyter, usar `display(HTML(resultado.to_html(escape=False)))`
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

    resultado = (
        df_copia
        .sort_values('prioridade')
        .groupby('cpf', as_index=False)
        .first()[['institution_name', 'cpf', 'full_name', 'risco']]
    )

    # Resumo por grupo de risco
    resumo = (
    resultado
    .groupby(['institution_name', 'risco'], as_index=False)
    .size()
    .rename(columns={'size': 'total'})  
    )

    # Aplica cor HTML na coluna 'risco'
    def colorir(valor):
        cor = cores_por_risco.get(valor, 'black')
        return f'<span style="color: {cor}; font-weight: bold;">{valor}</span>'

    resultado['risco'] = resultado['risco'].apply(colorir)

    resumo = resultado['risco'].apply(lambda x: x.lower()).value_counts().reset_index()
    resumo.columns = ['risco_', 'total']

    return resultado, resumo

# %%

resultado, resumo = classificar_risco(df, condicao_critica, condicao_alerta, condicao_atencao)

# resultado: DataFrame com ['institution_name', 'cpf', 'full_name', 'risco']
#resultado
from IPython.display import display, HTML
display(HTML(resultado.to_html(escape=False)))
# 

# %%

# resumo: contagem por risco
#resumo

display(HTML(resumo.to_html(escape=False)))
# %%

def classificar_risco(df, condicoes_critico, condicoes_alerta, condicoes_atencao, incluir_sem_risco=True):
    """
    Aplica condições de risco e retorna:
    - DataFrame agrupado por 'cpf' com colunas: institution_name, cpf, full_name, risco (colorido em HTML)
    - Resumo com contagem por nível de risco (rótulos limpos, sem HTML)
    
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

    if incluir_sem_risco:
        df_copia.loc[df_copia['risco'].isna(), 'risco'] = 'Sem Risco'

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

    # Resumo usando rótulos limpos (sem cor/HTML)
    resumo = (
        agrupado
        .groupby(['institution_name', 'risco'], as_index=False)
        .size()
        .rename(columns={'size': 'total'})
    )

    return agrupado.drop(columns=['risco']), resumo

# %%
resultado, resumo = classificar_risco(df, condicao_critica, condicao_alerta, condicao_atencao)

# Exibe o resultado com cores

display(HTML(resultado.to_html(escape=False)))

# Mostra o resumo correto
display(HTML(resumo.to_html(escape=False)))

# %%
salvar_tabela_como_imagem(
    resumo,
    '../tables/01_tabela_resummo_score_fragilidade.png',
    titulo='Score de Fragilidade do Residente por ILPI',
    largura_max_coluna=25
)

# Gráfico 01

plt.bar(x='institution_name', y='rico', height='total')


# %%
