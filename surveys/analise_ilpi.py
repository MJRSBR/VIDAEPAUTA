# %%
# --------------------
# Bibliotecas
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
# %%
# ---------------------
# Leitura dos dados
df = pd.read_csv('../data/base_ilpi.csv')
# %%
# ---------------------
# Configurações Globais dos Gráficos
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
# %%
# ---------------------
# Função para plotar gráficos de barras horizontais de binários (Sim ou Não)
def plot_barh(data, title, xlabel, filename, color=['#4E79A7', '#F28E2B']):
    data.plot(kind='barh', color=color)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(title)
    plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
         color='red',ha='left', va='bottom', wrap=True)
    plt.xlabel(xlabel)
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()
# %%
# -----------------------------------------------------------------
# DISPOSIÇÃO DAS CAMAS DOS RESIDENTES DE ACORDO COM A NORMA
# Criando e mapeando as colunas diretamente, com renomeação incluída para camas segundo norma
camas = (df[['institution_name', 'residents_bedroom']]
                        .assign(df_filtered=df['residents_bedroom'].map({1: 'Sim', 2: 'Não'}))  # Mapeando 'residents_bedroom'
                        [['institution_name', 'df_filtered']]  # Selecionando as colunas necessárias
                        .rename(columns={'institution_name': 'ILPI', 'df_filtered': 'Camas segundo a Norma?'})  # Renomeando as colunas
)

# Exibindo o resultado
camas
# %%
# ---------------------
# Gráfico 1 - Camas segundo a Norma
# Contando os valores de 'Camas segundo a Norma?' (Sim e Não)
camas_counts = camas['Camas segundo a Norma?'].value_counts()

plot_barh(
    camas_counts,
    'Distribuição de Camas segundo a Norma',
    'ILPIs',
    '01_camas_norma.png'
)
# ---------------------------------------------------------------------
# VEÍCULOS
# Criando e mapeando as colunas diretamente, com renomeação incluída para veículos
veiculo = (df[['institution_name', 'vehicle']]
                        .assign(df_filtered=df['vehicle'].map({1: 'Sim', 2: 'Não'}))  # Mapeando 'residents_bedroom'
                        [['institution_name', 'df_filtered']]  # Selecionando as colunas necessárias
                        .rename(columns={'institution_name': 'ILPI', 'df_filtered': 'Existe veículo à disposição?'})  # Renomeando as colunas
)

# Exibindo o resultado
veiculo
# %%
#----------------------
# Gráfico 2 - Veículos à disposição da ILPI
# Contando os valores (Sim e Não)
veiculo_counts = veiculo['Existe veículo à disposição?'].value_counts()

plot_barh(
    veiculo_counts,
    'Existe veículo à disposição nas ILPIs',
    'ILPIs',
    '02_veiculo.png'
)
# %%
# ---------------------
# PROFISSIONAIS
# Lista de mapeamento dos profissionais e as colunas correspondentes
profissionais_mapping = [
    ('Aux.Enfermagem', 'nurse_aux', 'days_per_month_na'),
    ('Téc.Enfermagem', 'nurse_tech', 'days_per_month_nt'),
    ('Enfermeiro(a)', 'nurse', 'days_per_month_n'),
    ('Fisio', 'physiotherapist', 'days_per_month_physio'),
    ('Nutricionista', 'nutritionist', 'days_per_month_nutrit'),
    ('Psicologo(a)', 'psicologist', 'days_per_month_psicol'),
    ('Médico(a)', 'physician', 'days_per_month_physician'),
    ('Ter.Ocupacional', 'occup_therapist', 'days_per_month_occup'),
    ('Cuidador(a)', 'caregiver', 'days_per_month_caregiver'),
    ('Outros_prof_saúde', 'other_health_prof', 'd_p_month_oth_health_prof'),
    ('Serv.Gerais', 'housekeeping', 'days_per_month_housekeep'),
    ('Administrativo', 'staff', 'days_per_month_staff')
]

# Construir o DataFrame 
df_profissionais = pd.concat(
    [
        df[df[col] >= 1][['institution_name', days_col]]
        .assign(profissional=prof)
        .rename(columns={days_col: 'Dias_por_mes', 'institution_name': 'ILPI'})
        .assign(Dias_por_mes=lambda x: x['Dias_por_mes'].round(1))  # Corrigido aqui
        [['ILPI', 'profissional', 'Dias_por_mes']]
        for prof, col, days_col in profissionais_mapping
    ]
).dropna(subset=['Dias_por_mes']) # Remover valores nulos

# Ordenar os dados e resetar index
df_profissionais = df_profissionais.sort_values(by=['ILPI', 'profissional']).reset_index(drop=True)

# Visualizar o resultado
df_profissionais

# %%
# Gráfico 03 - Profissionais nas ILPIs
plt.figure(figsize=(10, 6))
sns.barplot(x='profissional', y='Dias_por_mes', data=df_profissionais)
plt.xticks(rotation=45, ha='right') # Rotate x-axis labels for better readability
plt.text(0.02, 24.0,'* Uma das instituíções é composta por unidades de moradia',
         color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('Profissão')
plt.ylabel('Dias por Mês')
plt.title('Dias Trabalhados por Mês por Profissão')
plt.tight_layout()

plt.savefig('03_profissionais.png')
plt.show()
# %%
#-------------------------------------------------------------
# VINCULO
# Criando e mapeando as colunas diretamente, com renomeação incluída para vinculo empregaticio
# %%
vinculo_empreg = (
    df[['institution_name', 'employment_relatioship___1', 'employment_relatioship___2', 'employment_relatioship___3']]
    .assign(
        Vinculo_empregaticio= (
            df['employment_relatioship___1'].map(lambda x: 'CLT' if x == 1 else '') +
            df['employment_relatioship___2'].map(lambda x: ', Contrato' if x == 1 else '') +
            df['employment_relatioship___3'].map(lambda x: ', Voluntário' if x == 1 else '')
        )
    )
    .assign(Vinculo_empregaticio=lambda x: x['Vinculo_empregaticio'].str.lstrip(', '))  # Limpa a vírgula extra no começo
    .rename(columns={'institution_name': 'ILPI'})  # Renomeando a coluna institution_name para ILPI
    [['ILPI', 'Vinculo_empregaticio']]  # Selecionando apenas as colunas desejadas
)

# Visualizando o DataFrame resultante
vinculo_empreg
# %%

# Gráfico 04 - Vínculo Empregatício
# ---------------------
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
vinculo_empreg.groupby('Vinculo_empregaticio').size().plot(
    kind='barh',
    color=sns.palettes.mpl_palette('Dark2')
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Vínculo Empregatício dos Profissionais das ILPIs')
plt.text(2.5, 2.3,'* Uma das instituíções é composta por unidades de moradia',
         color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIS')
plt.ylabel('Tipo de Vínculo')

# Exibir gráfico
plt.savefig("04_vinculo_empreg.png")
plt.show()
# %%
# -------------

# Criando e mapeando as colunas diretamente, com renomeação incluída para 
# Plano/programa semanal de atividade física e reabilitação funcional

# Ajustar a exibição do pandas para mostrar mais caracteres
pd.set_option('display.max_colwidth', None)  # Permite exibir a coluna inteira

plano_reab = (
    df[["institution_name", "physio_program___1", "physio_program___2", "physio_program___3", "physio_program___4"]]
    .assign(
        plano_reabilitacao= (
            df["physio_program___1"].map(lambda x: 'melhoria do tônus muscular' if x == 1 else '') +
            df["physio_program___2"].map(lambda x: ', equilíbrio funcionalidade motora' if x == 1 else '') +
            df["physio_program___3"].map(lambda x: ', bem-estar geral com indicação do destinatário' if x == 1 else '') +
            df["physio_program___4"].map(lambda x: ', não existe plano' if x == 1 else '')
        )
    )
    .assign(plano_reabilitacao=lambda x: x['plano_reabilitacao'].str.lstrip(', '))  # Limpar vírgula no início da string
    .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
    [["ILPI", "plano_reabilitacao"]]  # Selecionando apenas as colunas finais
)

# Visualizando o resultado
plano_reab
# %%
# ----------------------
# Gráfico 5 - Plano Reabilitação

plano_counts = plano_reab['plano_reabilitacao'].value_counts()

plot_barh(
    plano_counts,
    'Plano/programa semanal de atividade física e reabilitação funcional',
    'ILPIs',
    '05_plano_terapeutico.png'
)
# %%
# ---------------------
# Criando e mapeando as colunas diretamente, com renomeação incluída para 
# Instruções do fisioterapeuta ao cuidador está documentada

instr_fisio = (df[['institution_name', 'physio_instructions']]
                        .assign(df_filtered=df['physio_instructions'].map({1: 'Sim', 2: 'Não'}))  # Mapeando 'residents_bedroom'
                        [['institution_name', 'df_filtered']]  # Selecionando as colunas necessárias
                        .rename(columns={'institution_name': 'ILPI', 'df_filtered': 'Instrucao_fisioterapeuta'})  # Renomeando as colunas
)

# Exibindo o resultado
instr_fisio
# %%
# ---------------------
# Gráfico 6 - Instruções do Fisioterapeuta
instr_counts = instr_fisio['Instrucao_fisioterapeuta'].value_counts()

plot_barh(
    instr_counts,
    'Instruções do fisioterapeuta ao cuidador está documentada?',
    'ILPIs',
    '06_instrucao_fisioterapeuta.png'
)
# %%
# ---------------------
# SEGURANÇA E MEIO AMBIENTE
# Serviço/sistema de segurança para sua proteção e dos idosos

sist_seg = (df[['institution_name', 'secutiry_system']]
                        .assign(df_filtered=df['secutiry_system'].map({1: 'Sim', 2: 'Não'}))  # Mapeando 'residents_bedroom'
                        [['institution_name', 'df_filtered']]  # Selecionando as colunas necessárias
                        .rename(columns={'institution_name': 'ILPI', 'df_filtered': 'Sistemas_segurança'})  # Renomeando as colunas
)

# Exibindo o resultado
sist_seg
# %%
# ---------------------
# Gráfico 7 - Sistema de Segurança
sist_counts = sist_seg['Sistemas_segurança'].value_counts()

plot_barh(
    sist_counts,
    'Existe Sistema de Segurança na ILPI?',
    'ILPIs',
    '07_sistema_seguranca.png'
)
# %%
# ---------------------
# Tipos de Serviço/sistema de segurança para sua proteção e dos idosos

# Ajustar a exibição do pandas para mostrar mais caracteres
pd.set_option('display.max_colwidth', None)  # Permite exibir a coluna inteira

tipos_sist_seg = (
    df[["institution_name", "security_device_type___1", "security_device_type___2", "security_device_type___3", "security_device_type___4", "security_device_type___5"]]
    .assign(
        tipos_sist_seguranca= (
            df["security_device_type___1"].map(lambda x: 'Alarme (incêndio/violação)' if x == 1 else ', Não tem alarmes') +
            df["security_device_type___2"].map(lambda x: ', Cameras interno' if x == 1 else ', Não tem cameras internas') +
            df["security_device_type___3"].map(lambda x: ', Cameras externo' if x == 1 else ', Não tem cameras externas') +
            df["security_device_type___4"].map(lambda x: ', Segurança (individuo)' if x == 1 else ', Não tem seguraça (indivíduo)') +
            df["security_device_type___5"].map(lambda x: ', Segurança armada (indivíduo)' if x == 1 else ', Não tem segurança armada (indivíduo)') 
        )
    )
    .assign(tipos_sist_seguranca=lambda x: x['tipos_sist_seguranca'].str.lstrip(', '))  # Limpar vírgula no início da string
    .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
    [["ILPI", "tipos_sist_seguranca"]]  # Selecionando apenas as colunas finais
)

tipos_sist_seg
# %%
# ---------------------
# Gráfico 8 - Tipos de Sistema de Segurança

# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
tipos_sist_seg.groupby('tipos_sist_seguranca').size().plot(
    kind='barh',
    color=sns.palettes.mpl_palette('Dark2')
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Contagem por Tipo de Sistema de Segurança')
plt.text(-2.5, 2.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIS')
plt.ylabel('Tipo de Sistema de Segurança')

# Exibir gráfico
plt.savefig("08_tipos_sist_seg.png")
plt.show()

#tipos_sist_seg_counts = tipos_sist_seg['tipos_sist_seguranca'].value_counts()

#plot_barh(
#    tipos_sist_seg,
#    'Tipos de Sistemas de Segurança',
#    'ILPIs',
#    'tipos_sist_seg.png'
#)
# %%
# ----------------------------
# Dispositivo/mecanismo (digital/analógico) de chamada que o 
# residente/acolhido na cama possa chamar em caso de necessidade
# de atendimento

disp_chamada = (df[["institution_name", "safety_device_availability"]]
                .assign(df_filtered=df["safety_device_availability"].map({1 :"Sim", 2 :"Não"})) # Mapeando safety_device_availability
                [["institution_name", "df_filtered"]]  # Selecionando colunas necessárias
                .rename(columns={'institution_name': 'ILPI', 'df_filtered': 'Disponibilidade_dispositivo_chamada'})  # Renomeando as colunas
)

disp_chamada
# %%
# Gráfico 9 Dispositivo/mecanismo (digital/analógico) de chamada
disp_chamada_counts = disp_chamada["Disponibilidade_dispositivo_chamada"].value_counts()

plot_barh(
    disp_chamada,
    'Dispositivo/mecanismo (digital/analógico) de chamada pelo residente',
    'ILPIs',
    '09_disp_chamada.png'
)
# -------------------
# %%
# Iluminação adequada

iluminacao = (df[["institution_name", "lighting"]]
              .assign(df_filtered=df["lighting"].map({1 : "Sim", 2 : "Não"})) # Mapeando lighting
              [["institution_name", "df_filtered"]] # Selecionando colunas
              .rename(columns={"institution_name": "ILPI", "df_filtered": "Iluminacao_adequada"})
)

iluminacao
# %%
# -------------------
# Gráfico 10 - iluminação adequada

iluminacao_counts = iluminacao['Iluminacao_adequada'].value_counts()

plot_barh(
    iluminacao,
    'A iluminição é adequada?',
    'ILPIs',
    '10_ilumincacao.png'
)
# %%
# --------------------

# Ventilação adequada

ventilacao = (df[["institution_name", "ventilation"]]
             .assign(df_filtered=df["ventilation"].map({1:"Sim", 2:"Não"}))
             [["institution_name", "df_filtered"]]
             .rename(columns={"insitution_name": "ILPI", "df_filtered": "Ventilacao_adequada"})

)

ventilacao
# %%
# ------------------
# Gráfico 11 - Ventilação Adequada
# Tamanho da figura
plt.figure(figsize=(10,6))

# Agrupar e plotar o g'rafico de barras horizontais
ventilacao.groupby("Ventilacao_adequada").size().plot(
    kind="barh",
    color=["blue", "orange"]
)

# Ajustar as bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo x seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Títulos e rótulos
plt.title("A ventilação é adequada?")
plt.text(0.02, 1.3, '* Uma das institíções é composta por unidades de moradia',
         color='red', ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir o gráfico
plt.savefig("11_ventilacao.png")
plt.show()
# %%
# -----------------------
# Pintura do quarto tons pastéis

pintura_quartos = (df[["institution_name", "painting_color"]]
                   .assign(df_filtered=df["painting_color"].map({1: "Sim", 2: "Não"}))
                   [["institution_name", "df_filtered"]]
                   .rename(columns={"institution_name": "IPLI", "df_filtered": "Pintura_tons_pasteis"})
)

pintura_quartos
# %%
# ---------------------
# Gráfico 12 - Pintura quartos tons pastéis
pintura_quartos_counts = pintura_quartos["Pintura_tons_pasteis"].value_counts()

plot_barh(
    pintura_quartos,
    "Pintura quartos tons pastéis",
    "ILPIs"
    "12_pintura.png"
)

# %%
# -------------------
# Acessibilidade para o residente
# Quarto

acessib_quarto = (df[["institution_name", "room_access___1", "room_access___2", "room_access___3"]]
                  .assign(
                        acessib_quarto_list=(
                              df["room_access___1"].map(lambda x: 'Portas largas para cadeirante' if x == 1 else '') +
                              df["room_access___2"].map(lambda x: 'Rampas' if x == 1 else '') +
                              df["room_access___3"].map(lambda x: 'Corrimão para apoio' if x == 1 else '')
                        )
                  )
                  .assign(acessib_quarto_list=lambda x: x['acessib_quarto_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "acessib_quarto_list"]]  # Selecionando apenas as colunas finais
)

acessib_quarto

# -------------------
# Gráfico 13 - Acessíbilidade do quarto
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
acessib_quarto.groupby('acessib_quarto_list').size().plot(
    kind='barh',
    color=sns.palettes.mpl_palette('Dark2')
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Tipo de acessibilidade ao quarto do residente')
plt.text(-2.5, 2.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("13_acessib_quarto.png")
plt.show()
# %%
# --------------------
# Banheiro

acessib_banheiro = (df[["institution_name", "bathroom_access___1", "bathroom_access___2", "bathroom_access___3"]]
                  .assign(
                        acessib_banheiro_list=(
                              df["bathroom_access___1"].map(lambda x: 'Portas largas para cadeirante' if x == 1 else '') +
                              df["bathroom_access___2"].map(lambda x: 'Rampas' if x == 1 else '') +
                              df["bathroom_access___3"].map(lambda x: 'Corrimão para apoio' if x == 1 else '')
                        )
                  )
                  .assign(acessib_banheiro_list=lambda x: x['acessib_banheiro_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "acessib_banheiro_list"]]  # Selecionando apenas as colunas finais
)

acessib_banheiro

# -------------------
# Gráfico 14 - Acessíbilidade do banheiro
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
acessib_banheiro.groupby('acessib_banheiro_list').size().plot(
    kind='barh',
    color=sns.palettes.mpl_palette('Dark2')
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Tipo de acessibilidade ao banheiro do residente')
plt.text(-2.5, 2.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("14_acessib_banheiro.png")
plt.show()
# %%
# Refeitório

acessib_refeitorio = (df[["institution_name", "cafeteria_access___1", "cafeteria_access___2", "cafeteria_access___3"]]
                  .assign(
                        acessib_refeitorio_list=(
                              df["cafeteria_access___1"].map(lambda x: 'Portas largas para cadeirante' if x == 1 else '') +
                              df["cafeteria_access___2"].map(lambda x: 'Rampas' if x == 1 else '') +
                              df["cafeteria_access___3"].map(lambda x: 'Corrimão para apoio' if x == 1 else '')
                        )
                  )
                  .assign(acessib_refeitorio_list=lambda x: x['acessib_refeitorio_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "acessib_refeitorio_list"]]  # Selecionando apenas as colunas finais
)

acessib_refeitorio

# -------------------
# Gráfico 15 - Acessíbilidade do refeitório
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
acessib_refeitorio.groupby('acessib_refeitorio_list').size().plot(
    kind='barh',
    color=sns.palettes.mpl_palette('Dark2')
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Tipo de acessibilidade ao refeitorio do residente')
plt.text(-2.5, 2.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("13_acessib_refeitorio.png")
plt.show()
# %%
# Outras áreas

acessib_outras_areas = (df[["institution_name", "other_areas_access___1", "other_areas_access___2", "other_areas_access___3"]]
                  .assign(
                        acessib_outras_areas_list=(
                              df["other_areas_access___1"].map(lambda x: 'Portas largas para cadeirante' if x == 1 else '') +
                              df["other_areas_access___2"].map(lambda x: 'Rampas' if x == 1 else '') +
                              df["other_areas_access___3"].map(lambda x: 'Corrimão para apoio' if x == 1 else '')
                        )
                  )
                  .assign(acessib_outras_areas_list=lambda x: x['acessib_outras_areas_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "acessib_outras_areas_list"]]  # Selecionando apenas as colunas finais
)

acessib_outras_areas

# -------------------
# Gráfico 16 - Acessíbilidade de outras áreas
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
acessib_outras_areas.groupby('tipos_sist_seguranca').size().plot(
    kind='barh',
    color=sns.palettes.mpl_palette('Dark2')
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Tipo de acessibilidade ao outras areas do residente')
plt.text(-2.5, 2.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("13_acessib_outras_areas.png")
plt.show()
# %%
# ------------------------
# Quadro geral acessibilidade

quadro_geral_acessib = (acessib_quarto.merge(acessib_banheiro, on="ILPI", how="right") \
                        .merge(acessib_refeitorio, on="ILPI", how="right")\
                        .merge(acessib_outras_areas, on="ILPI", how="right")
)
quadro_geral_acessib

# %%
# -----------------------
# Os profissionais da ILPI utilizam qualquer tipo de EPI's, durante no cuidado com os idosos

uso_epi = (df[["institution_name", "epi_use"]]
           .assign(df_filtered= df["epi_use"].map({1: "Sim", 2: "Não"}))
           [["institution_name", "df_filtered"]]
           .rename(columns={"institution_name": "ILPI", "df_filtered": "Uso_equip_prot_individual"})
)

uso_epi
# %%
# ----------------
# Gráfico 17 - Uso de Equipamento de Proteção Individual

uso_epi_counts = uso_epi["Uso_equip_prot_individual"].value_counts()

plot_barh(
    uso_epi,
    "Uso de Equipamento de Proteção Individual",
    "17_uso_epi.png"
)
# %%
# -------------------
# Medicamentos
# dentro do prazo de validade

medic_prazo_val = (df[["institution_name", "medication_val_date"]]
                   .assign(df_filtered=df["medication_val_date"].map({1: "Sim", 2: "Não"}))
                   [["institution_name", "df_filtered"]]
                   .rename(columns={"institution_name": "ILPI", "df_filtered": "Medicacao_prazo_validade"})
)

medic_prazo_val
# %%
# -------------------
# Gráfico 18 - Medicamento dentro do prazo de validade

medic_prazo_val_counts = medic_prazo_val["Medicacao_prazo_validade"].value_counts()

plot_barh(
    medic_prazo_val,
    "Medicamento dentro do prazo de validade",
    "18_medic_prazo.png"
)
# %%
# ---------------------
# Embalagem violada

emb_viol = (df[["institution_name", "violeted_pakage"]]
            .assign(df_filtered=df["violeted_pakage"].map({1: "Sim", 2:"Não"}))
            [["institution_name", "df_filtered"]]
            .rename(columns={"institution_name": "ILPI", "df_filtered": "Embalagem_violada"})
)
# %%
# -------------------
# Gráfico 19 - Medicamento com embalagem violada

emb_viol_counts = emb_viol["Embalagem_violada"].value_counts()

plot_barh(
    emb_viol,
    "Medicamento com embalagem violada",
    "19_medic_emb_violada.png"
)
# %%
# ------------------
# Geladeira exclusiva ao armazenamento de medicamentos

geladeira_medic = (df[['institution_name', 'medicine_refrigerator']]
                   .assign(df_filtered=df["medicine_refrigerator"].map({1: "Sim", 2: "Não"}))
                   [["institution_name", "df_filtered"]]
                   .rename(columns={"institution_name": "ILPI", "df_filtered": "Geladeira_exclusiva_medicamentos"})
)

geladeira_medic
# ------------------
# Gráfico 20 - Geladeira exclusiva ao armazenamento de medicamentos

geladeira_medic_counts = geladeira_medic["Geladeira_exclusiva_medicamentos"].value_counts()

plot_barh(
    geladeira_medic,
    "Geladeira exclusiva ao armazenamento de medicamentos",
    "20_geladeira_medic.png"
)
# %%
# ----------------------
# Registro temperatura da geladeira

reg_temp_geladeira = (df[["institution_name", "refrigerator_temp_log"]]
             .assign(df_filtered=df["refrigerator_temp_log"].map({1: "Sim", 2: "Não"}))
             [["institution_name", "df_filtered"]]
             .rename(columns={"institution_name": "ILPI", "df_filtered": "Registro_temperatura_geladeira"})
)

reg_temp_geladeira
# %%
# ---------------------
# Gráfico 21 - Registro temperatura da geladeira

reg_temp_geladeira_counts = reg_temp_geladeira["Registro_temperatura_geladeira"].value_counts()

plot_barh(
    reg_temp_geladeira,
    "Registro temperatura da geladeira",
    "21_reg_temp_geladeira.png"
)
# %%
# ----------------------
# Registro de utilização e frequência uso medicação

reg_medic = (df[["institution_name", "medication_register"]]
             .assign(df_filtered=df["medication_register"].map({1: "Sim", 2: "Não"}))
             [["institution_name", "df_filtered"]]
             .rename(columns={"institution_name": "ILPI", "df_filtered": "Registro_uso_medicacao"})
)
# %%
# ---------------------
# Gráfico 22 - Registro de utilização e frequência uso medicação

reg_medic_counts = reg_medic["Registro_uso_medicacao"].value_counts()

plot_barh(
    reg_medic,
    "Registro de utilização e frequência uso medicação",
    "22_reg_uso_medicacao.png"
)
# %%
# ---------------------
# Tipo de registro da medicação

tipo_reg_medic = (df[["institution_name", "medication_register_type___1", "medication_register_type___2", "medication_register_type___3"]]
                  .assign(
                        tipo_reg_medic_list=(
                              df["medication_register_type___1"].map(lambda x: 'livro ata' if x == 1 else '') +
                              df["medication_register_type___2"].map(lambda x: 'registro individual em papel' if x == 1 else '') +
                              df["medication_register_type___3"].map(lambda x: 'registro individual digital' if x == 1 else '')
                        )
                  )
                  .assign(tipo_reg_medic_list=lambda x: x['tipo_reg_medic_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "tipo_reg_medic_list"]]  # Selecionando apenas as colunas finais
)

tipo_reg_medic
# %%
# --------------------
# Gráfico 23 - Tipo de registro da medicação
# ---------------------
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
tipo_reg_medic.groupby('tipo_reg_medicaticio').size().plot(
    kind='barh',
    color=sns.palettes.mpl_palette('Dark2')
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Tipo de registro da medicação')
plt.text(2.5, 2.3,'* Uma das instituíções é composta por unidades de moradia',
         color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('Tipo de Registro')

# Exibir gráfico
plt.savefig("23_tipo_reg_medic.png")
plt.show()
# %%
# -------------------------
# Substâncias Psicoativas/Psicotrópicas estão guardadas separadamente

med_psico_separado = (df[["institution_name", "psico_drugs_segregation"]]
             .assign(df_filtered=df["psico_drugs_segregation"].map({1: "Sim", 2: "Não"}))
             [["institution_name", "df_filtered"]]
             .rename(columns={"institution_name": "ILPI", "df_filtered": "Subst_psico_segregada"})
)
# %%
# ---------------------
# Gráfico 24 - Substâncias Psicoativas/Psicotrópicas estão guardadas separadamente

med_psico_separado_counts = med_psico_separado["Subst_psico_segregada"].value_counts()

plot_barh(
    med_psico_separado,
    "Substâncias Psicoativas/Psicotrópicas estão guardadas separadamente",
    "22_subst_psico_segregada.png"
)
# %%
# Como são armazenadas as substâncias psicoativas