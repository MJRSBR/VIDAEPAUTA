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
df = pd.read_csv('../../data/base_ilpi.csv')

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
# %%
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
# ---------------------
# Gráfico 04 - Vínculo Empregatício
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
#disp_counts = disp_chamada["Disponibilidade_dispositivo_chamada"].value_counts()
#
#plot_barh(
#    disp_chamada,
#    'Dispositivo/mecanismo (digital/analógico) de chamada pelo residente',
#    'ILPIs',
#    '09_disp_chamada.png'
#)
# %%
# Contando os valores
counts = disp_chamada["Disponibilidade_dispositivo_chamada"].value_counts()

# Criando o gráfico de barras horizontais
counts.plot(kind='barh', color=['#4E79A7', '#F28E2B'])

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Adicionando título e rótulos
plt.title('Disponibilidade de dispositivo de chamada pelo residente')
plt.xlabel('ILPIS')
plt.ylabel('')

# Exibindo o gráfico
plt.savefig('09_disp_chamada.png')
plt.show()
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

#iluminacao_counts = iluminacao['Iluminacao_adequada'].value_counts()

#plot_barh(
#   iluminacao,
#   'A iluminição é adequada?',
#   'ILPIs',
#   '10_ilumincacao.png'
#

# %%
# Contando os valores
counts = iluminacao["Iluminacao_adequada"].value_counts()

# Criando o gráfico de barras horizontais
counts.plot(kind='barh', color=['#4E79A7', '#F28E2B'])

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Adicionando título e rótulos
plt.title('A iluminação é adequada?')
plt.text(0.02, 1.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIS')
plt.ylabel('')

# Exibindo o gráfico
plt.savefig('10_ilumincacao.png')
plt.show()
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
    color=['#4E79A7', '#F28E2B']
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
#pintura_quartos_counts = pintura_quartos["Pintura_tons_pasteis"].value_counts()
#
#plot_barh(
#    pintura_quartos,
#    "Pintura quartos tons pastéis",
#    "ILPIs",
#    "12_pintura.png"
#)

# %%
# -------------------
# Acessibilidade para o residente
# Quarto

acessib_quarto = (df[["institution_name", "room_access___1", "room_access___2", "room_access___3"]]
                  .assign(
                        acessib_quarto_list=(
                              df["room_access___1"].map(lambda x: 'Portas largas para cadeirante' if x == 1 else '') +
                              df["room_access___2"].map(lambda x: ', Rampas' if x == 1 else '') +
                              df["room_access___3"].map(lambda x: ', Corrimão para apoio' if x == 1 else '')
                        )
                  )
                  .assign(acessib_quarto_list=lambda x: x['acessib_quarto_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "acessib_quarto_list"]]  # Selecionando apenas as colunas finais
)

acessib_quarto
# %%
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
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
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
                              df["bathroom_access___2"].map(lambda x: ', Rampas' if x == 1 else '') +
                              df["bathroom_access___3"].map(lambda x: ', Corrimão para apoio' if x == 1 else '')
                        )
                  )
                  .assign(acessib_banheiro_list=lambda x: x['acessib_banheiro_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "acessib_banheiro_list"]]  # Selecionando apenas as colunas finais
)

acessib_banheiro
# %%
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
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("14_acessib_banheiro.png")
plt.show()
# %%
# Refeitório

acessib_refeitorio = (df[["institution_name", "cafeteria___1", "cafeteria___2", "cafeteria___3"]]
                  .assign(
                        acessib_refeitorio_list=(
                              df["cafeteria___1"].map(lambda x: 'Portas largas para cadeirante' if x == 1 else '') +
                              df["cafeteria___2"].map(lambda x: ', Rampas' if x == 1 else '') +
                              df["cafeteria___3"].map(lambda x: ', Corrimão para apoio' if x == 1 else '')
                        )
                  )
                  .assign(acessib_refeitorio_list=lambda x: x['acessib_refeitorio_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "acessib_refeitorio_list"]]  # Selecionando apenas as colunas finais
)

acessib_refeitorio
# %%
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
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("15_acessib_refeitorio.png")
plt.show()
# %%
# Outras áreas

acessib_outras_areas = (df[["institution_name", "other_areas___1", "other_areas___2", "other_areas___3"]]
                  .assign(
                        acessib_outras_areas_list=(
                              df["other_areas___1"].map(lambda x: 'Portas largas para cadeirante' if x == 1 else '') +
                              df["other_areas___2"].map(lambda x: ', Rampas' if x == 1 else '') +
                              df["other_areas___3"].map(lambda x: ', Corrimão para apoio' if x == 1 else '')
                        )
                  )
                  .assign(acessib_outras_areas_list=lambda x: x['acessib_outras_areas_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "acessib_outras_areas_list"]]  # Selecionando apenas as colunas finais
)

acessib_outras_areas
# %%
# -------------------
# Gráfico 16 - Acessíbilidade de outras áreas
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
acessib_outras_areas.groupby('acessib_outras_areas_list').size().plot(
    kind='barh',
    color=sns.palettes.mpl_palette('Dark2')
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Tipo de acessibilidade ao outras areas do residente')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("16_acessib_outras_areas.png")
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

#uso_epi_counts = uso_epi["Uso_equip_prot_individual"].value_counts()

#plot_barh(
#    uso_epi,
#    "Uso de Equipamento de Proteção Individual",
#    "ILPIs",
#    "17_uso_epi.png"
#)
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
uso_epi.groupby('Uso_equip_prot_individual').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Uso de Equipamento de Proteção Individual')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("17_uso_epi.png")
plt.show()
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

#medic_prazo_val_counts = medic_prazo_val["Medicacao_prazo_validade"].value_counts()
#
#plot_barh(
#    medic_prazo_val,
#    "Medicamento dentro do prazo de validade",
#    "ILPIs",
#    "18_medic_prazo.png"
#)
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
medic_prazo_val.groupby('Medicacao_prazo_validade').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Medicamento dentro do prazo de validade')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("18_medic_prazo")
plt.show()
# %%
# ---------------------
# Embalagem violada

emb_viol = (df[["institution_name", "violeted_pakage"]]
            .assign(df_filtered=df["violeted_pakage"].map({1: "Sim", 2:"Não"}))
            [["institution_name", "df_filtered"]]
            .rename(columns={"institution_name": "ILPI", "df_filtered": "Embalagem_violada"})
)
emb_viol
# %%
# -------------------
# Gráfico 19 - Medicamento com embalagem violada

#emb_viol_counts = emb_viol["Embalagem_violada"].value_counts()
#
#plot_barh(
#    emb_viol,
#    "Medicamento com embalagem violada",
#    "19_medic_emb_violada.png"
#)
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
emb_viol.groupby('Embalagem_violada').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Medicamento com embalagem violada')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("19_medic_emb_violada.png")
plt.show()
# %%
# ------------------
# Geladeira exclusiva ao armazenamento de medicamentos

geladeira_medic = (df[['institution_name', 'medicine_refrigerator']]
                   .assign(df_filtered=df["medicine_refrigerator"].map({1: "Sim", 2: "Não"}))
                   [["institution_name", "df_filtered"]]
                   .rename(columns={"institution_name": "ILPI", "df_filtered": "Geladeira_exclusiva_medicamentos"})
)

geladeira_medic
# %%
# ------------------
# Gráfico 20 - Geladeira exclusiva ao armazenamento de medicamentos

#geladeira_medic_counts = geladeira_medic["Geladeira_exclusiva_medicamentos"].value_counts#()
#
#plot_barh(
#    geladeira_medic,
#    "Geladeira exclusiva ao armazenamento de medicamentos",
#    "20_geladeira_medic.png"
#)
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
geladeira_medic.groupby('Geladeira_exclusiva_medicamentos').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Geladeira exclusiva ao armazenamento de medicamentos')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("20_geladeira_medic.png")
plt.show()
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

#reg_temp_geladeira_counts = reg_temp_geladeira["Registro_temperatura_geladeira"].#value_counts()
#
#plot_barh(
#    reg_temp_geladeira,
#    "Registro temperatura da geladeira",
#    "21_reg_temp_geladeira.png"
#)
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
reg_temp_geladeira.groupby('Registro_temperatura_geladeira').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Registro temperatura da geladeira')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("21_reg_temp_geladeira.png")
plt.show()
# %%
# ----------------------
# Registro de utilização e frequência uso medicação

reg_medic = (df[["institution_name", "medication_register"]]
             .assign(df_filtered=df["medication_register"].map({1: "Sim", 2: "Não"}))
             [["institution_name", "df_filtered"]]
             .rename(columns={"institution_name": "ILPI", "df_filtered": "Registro_uso_medicacao"})
)

reg_medic
# %%
# ---------------------
# Gráfico 22 - Registro de utilização e frequência uso medicação

#reg_medic_counts = reg_medic["Registro_uso_medicacao"].value_counts()
#
#plot_barh(
#    reg_medic,
#    "Registro de utilização e frequência uso medicação",
#    "22_reg_uso_medicacao.png"
#)
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
reg_medic.groupby('Registro_uso_medicacao').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Registro de utilização e frequência uso medicação')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("22_reg_uso_medicacao.png")
plt.show()
# %%
# ---------------------
# Tipo de registro da medicação

tipo_reg_medic = (df[["institution_name", "medication_register_type___1", "medication_register_type___2", "medication_register_type___3"]]
                  .assign(
                        tipo_reg_medic_list=(
                              df["medication_register_type___1"].map(lambda x: 'livro ata' if x == 1 else '') +
                              df["medication_register_type___2"].map(lambda x: ',  registro individual em papel' if x == 1 else '') +
                              df["medication_register_type___3"].map(lambda x: ', registro individual digital' if x == 1 else '')
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
tipo_reg_medic.groupby('tipo_reg_medic_list').size().plot(
    kind='barh',
    color=sns.palettes.mpl_palette('Dark2')
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Tipo de registro da medicação')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
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

med_psico_separado
# %%
# ---------------------
# Gráfico 24 - Substâncias Psicoativas/Psicotrópicas estão guardadas separadamente

#med_psico_separado_counts = med_psico_separado["Subst_psico_segregada"].value_counts()
#
#plot_barh(
#    med_psico_separado,
#    "Substâncias Psicoativas/Psicotrópicas estão guardadas separadamente",
#    "22_subst_psico_segregada.png"
#)
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
med_psico_separado.groupby('Subst_psico_segregada').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Substâncias Psicoativas/Psicotrópicas estão guardadas separadamente')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("24_subst_psico_segregada.png")
plt.show()
# %%
# ------------------------
# Como são armazenadas as substâncias psicoativas

psico_armaz = (df[["institution_name", "psico_drugs_storage"]]
               .rename(columns={"institution_name": "ILPI", "psico_drugs_storage": "Onde_sao_armazenados_psicoativos"})
)

psico_armaz
# %%
# -------------------------
# Gráfico 25 - Como são armazenadas as substâncias psicoativas

#plot_barh(
#    psico_armaz,
#    "Como são armazenadas as substâncias psicoativas",
#    "25_psico_armazenamento.png"
#)
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
psico_armaz.groupby('Onde_sao_armazenados_psicoativos').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Como são armazenadas as substâncias psicoativas')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("25_psico_armazenamento.png")
plt.show()
# %%
# ------------------------
# Profissional que faz a separação da medicação a ser tomada pelos idosos

prof_manip_medic = (df[["institution_name", "medication_manipulation___1", "medication_manipulation___2", "medication_manipulation___3",
                         "medication_manipulation___4", "medication_manipulation___5", "medication_manipulation___6", "medication_manipulation___7"]]
                  .assign(
                        prof_manip_medic_list=(
                              df["medication_manipulation___1"].map(lambda x: 'técnico da farmácia' if x == 1 else '') +
                              df["medication_manipulation___2"].map(lambda x: ', farmacêutico(a)' if x == 1 else '') +
                              df["medication_manipulation___3"].map(lambda x: ', auxiliar de enfermagem' if x == 1 else '') +
                              df["medication_manipulation___4"].map(lambda x: ', técnico de enfermagem' if x == 1 else '') +
                              df["medication_manipulation___5"].map(lambda x: ', enfermeiro(a)' if x == 1 else '') +
                              df["medication_manipulation___6"].map(lambda x: ', cuidador(a)' if x == 1 else '') +
                              df["medication_manipulation___7"].map(lambda x: ', outro' if x == 1 else '') 
                        )
                  )
                  .assign(prof_manip_medic_list=lambda x: x['prof_manip_medic_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "prof_manip_medic_list"]]  # Selecionando apenas as colunas finais
)
prof_manip_medic
# %%
# ---------------------
# Gráfico 26 - Profissional que faz a separação da medicação a ser tomada pelos idosos
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
prof_manip_medic.groupby('prof_manip_medic_list').size().plot(
    kind='barh',
    color=sns.palettes.mpl_palette('Dark2')
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Profissional que faz a separação da medicação a ser tomada pelos idosos')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
         color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('Profissional')

# Exibir gráfico
plt.savefig("26_prof_manipula_medic.png")
plt.show()
# %%
# ----------------------
# Qual é o outro profissional?
outro_profis = (df[["institution_name", "other_meditation_manip"]]
               .rename(columns={"institution_name": "ILPI", "other_meditation_manip": "Outro_prof_dispensa"})
)

outro_profis
# %%
# -------------------------
# Gráfico 27 - Outro profissional dispensa medicamento

plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
outro_profis.groupby('Outro_prof_dispensa').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Qual é o outro profissional?')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("27_outro_prof_dispensa.png")
plt.show()
# %%
# -------------------
# Quadro geral dispensação medicação

quadro_geral_disp = (prof_manip_medic.merge(outro_profis, on="ILPI", how="right"))
quadro_geral_disp

# %%
# ---------------------
# Serviço Lavanderia
# Separação de roupas limpas e sujas

roupa_segreg = (df[["institution_name", "dirty_clothing_segregation"]]
                .assign(df_filtered=df["dirty_clothing_segregation"].map({1: "Sim", 2: "Não"}))
                [["institution_name", "df_filtered"]]
                .rename(columns={"institution_name": "ILPI", "df_filtered": "Separacao_roupas_sujas_limpas"})
)

roupa_segreg
# %%
# -------------------------
# Gráfico 28 - Separação de roupas limpas e sujas

plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
roupa_segreg.groupby('Separacao_roupas_sujas_limpas').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Separação de roupas limpas e sujas')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("28_roupa_segreg.png")
plt.show()
# %%
# Frequência de troca de roupas de cama e toalhas

freq_troca_roupa_cama = (df[["institution_name", "dirty_clothing_change"]]
                  .assign(
                        freq_troca_roupa_cama_list=(
                              df["dirty_clothing_change"].map(lambda x: 'diario' if x == 1 else '') +
                              df["dirty_clothing_change"].map(lambda x: ', semanal' if x == 2 else '') +
                              df["dirty_clothing_change"].map(lambda x: ', quinzenal' if x == 3 else '') +
                              df["dirty_clothing_change"].map(lambda x: ', mensal' if x == 4 else '')
                        )
                  )
                  .assign(freq_troca_roupa_cama_list=lambda x: x['freq_troca_roupa_cama_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "freq_troca_roupa_cama_list"]]  # Selecionando apenas as colunas finais
)

freq_troca_roupa_cama
# %%
# --------------------
# Gráfico 29 - Frequência de troca de roupas de cama e toalhas

plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
freq_troca_roupa_cama.groupby('freq_troca_roupa_cama_list').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Frequência de troca de roupas de cama e toalhas')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("29_freq_troca_roupa_cama.png")
plt.show()

# %%
# Gerenciamento Resíduos
# ---------------------------
# Separação do lixo (orgânico/reciclável)

reciclagem_lixo = (df[["institution_name", "trash_recicling"]]
                   .assign(df_filtered=df["trash_recicling"].map({1: "Sim", 2: "Não"}))
                   [["institution_name", "df_filtered"]]
                .rename(columns={"institution_name": "ILPI", "df_filtered": "Reciclagem_lixo"})
)

reciclagem_lixo
# %%
# Gráfico 30 - Reciclagem de lixo
# --------------------------
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
reciclagem_lixo.groupby('Reciclagem_lixo').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Separação de lixo (orgânico/reciclável)')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("30_reciclagem_lixo.png")
plt.show()
# %%
# Recipientes adequados e devidamente rotulados para descarte dos diferentes tipos de resíduos
# ---------------------------

container_adequados = (df[["institution_name", "trash_container___1", "trash_container___2", "trash_container___3", 
                           "trash_container___4","trash_container___5"]]
                  .assign(
                        container_adequados_list=(
                              df["trash_container___1"].map(lambda x: 'Resíduo infectante' if x == 1 else '') +
                              df["trash_container___2"].map(lambda x: ', Resíduo químico' if x == 1 else '') +
                              df["trash_container___3"].map(lambda x: ', Resíduo radioativo' if x == 1 else '') +
                              df["trash_container___4"].map(lambda x: ', Resíduo perfurocortante' if x == 1 else '') +
                              df["trash_container___5"].map(lambda x: ', Resíduo comum' if x == 1 else '') 
                        )
                  )
                  .assign(container_adequados_list=lambda x: x['container_adequados_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "container_adequados_list"]]  # Selecionando apenas as colunas finais
)

container_adequados
# %%
# --------------------
# Gráfico 31 - Recipientes adequados e devidamente rotulados para descarte dos diferentes
# tipos de resíduos

plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
container_adequados.groupby('container_adequados_list').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Recipientes adequados/rotulados para descarte dos diferentes tipos de resíduos')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("31_container_adequados.png")
plt.show()
# %%
# Processos de Cuidado
# Área para que o residente possa tomar um banho de sol
# ---------------------
banho_sol = (df[["institution_name", "sunbathing"]]
                   .assign(df_filtered=df["sunbathing"].map({1: "Sim", 2: "Não"}))
                   [["institution_name", "df_filtered"]]
                .rename(columns={"institution_name": "ILPI", "df_filtered": "banho_sol"})
)

banho_sol
# %%
# Gráfico 32 - Área banho de sol
# --------------------------
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
banho_sol.groupby('banho_sol').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Área para que o residente possa tomar um banho de sol')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("32_banho_sol.png")
plt.show()
# %%
# Área recebimento de visitas e familiares
# ----------------------
area_vis_familia = (df[["institution_name", "visiting_area"]]
                   .assign(df_filtered=df["visiting_area"].map({1: "Sim", 2: "Não"}))
                   [["institution_name", "df_filtered"]]
                .rename(columns={"institution_name": "ILPI", "df_filtered": "area_vis_familia"})
)

area_vis_familia
# %%
# Gráfico 33 - Área recebimento de visitas e familiares
# --------------------------
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
area_vis_familia.groupby('area_vis_familia').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Área recebimento de visitas e familiares')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("33_area_vis_familia.png")
plt.show()
# %%

# Área de atividades sociais
# ---------------------
area_ativ_social = (df[["institution_name", "social_area"]]
                   .assign(df_filtered=df["social_area"].map({1: "Sim", 2: "Não"}))
                   [["institution_name", "df_filtered"]]
                .rename(columns={"institution_name": "ILPI", "df_filtered": "area_ativ_social"})
)

area_ativ_social
# %%
# Gráfico 34 - Área de atividades sociais
# --------------------------
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
area_ativ_social.groupby('area_ativ_social').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Área de atividades sociais')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("34_area_ativ_social.png")
plt.show()
# %%
# Música ambiente na ILPI
# ---------------------------
musica_ambiente = (df[["institution_name", "ambient_music"]]
                   .assign(df_filtered=df["ambient_music"].map({1: "Sim", 2: "Não"}))
                   [["institution_name", "df_filtered"]]
                .rename(columns={"institution_name": "ILPI", "df_filtered": "musica_ambiente"})
)

musica_ambiente
# %%
# Gráfico 35 - Área de atividades sociais
# --------------------------
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
musica_ambiente.groupby('musica_ambiente').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Área de atividades sociais')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("35_musica_ambiente.png")
plt.show()
# %%
# Cardápio visível para consulta
# ---------------------------
cardapio_visivel = (df[["institution_name", "menu"]]
                   .assign(df_filtered=df["menu"].map({1: "Sim", 2: "Não"}))
                   [["institution_name", "df_filtered"]]
                .rename(columns={"institution_name": "ILPI", "df_filtered": "cardapio_visivel"})
)

cardapio_visivel
# %%
# Gráfico 36 - Cardápio visível para consulta
# --------------------------
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
cardapio_visivel.groupby('cardapio_visivel').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Cardápio visível para consulta')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("36_cardapio_visivel.png")
plt.show()
# %%
# Frequência que o cardápio é atualizado
# ----------------------------------
freq_atualiz_cardapio = (df[["institution_name", "semanal_menu"]]
                   .assign(df_filtered=df["semanal_menu"].map({1: "Sim", 2: "Não"}))
                   [["institution_name", "df_filtered"]]
                .rename(columns={"institution_name": "ILPI", "df_filtered": "atualiz_cardapio"})
)

freq_atualiz_cardapio
# %%
# Gráfico 37 - Cardápio visível para consulta
# --------------------------
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
freq_atualiz_cardapio.groupby('atualiz_cardapio').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Frequência que o cardápio é atualizado')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("37_atualiz_cardapio.png")
plt.show()
# %%
# Realização de oficinas e atividades
# ---------------------------
oficinas_atividades = (df[["institution_name", "recreation_type___1", "recreation_type___2", "recreation_type___3",
                      "recreation_type___4", "recreation_type___5", "recreation_type___6", "recreation_type___7"]]
                  .assign(
                        oficinas_atividades_list=(
                              df["recreation_type___1"].map(lambda x: 'Oficina de jardinagem' if x == 1 else '') +
                              df["recreation_type___2"].map(lambda x: ', Oficina de costura' if x == 1 else '') +
                              df["recreation_type___3"].map(lambda x: ', Oficina de artesanato' if x == 1 else '') +
                              df["recreation_type___4"].map(lambda x: ', Oficina de marcenaria' if x == 1 else '') +
                              df["recreation_type___5"].map(lambda x: ', Dança de salão' if x == 1 else '') +
                              df["recreation_type___6"].map(lambda x: ', Datas comemorativas' if x == 1 else '') +
                              df["recreation_type___7"].map(lambda x: ', Missas/Cultos Ecumênicos' if x == 1 else '')
                        )
                  )
                  .assign(oficinas_atividades_list=lambda x: x['oficinas_atividades_list'].str.lstrip(', '))  # Limpar vírgula no início da string
                  .rename(columns={"institution_name": "ILPI"})  # Renomeando a coluna
                  [["ILPI", "oficinas_atividades_list"]]  # Selecionando apenas as colunas finais
)

oficinas_atividades

# %%
# --------------------
# Gráfico 38 - Realização de oficinas e atividades

plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
oficinas_atividades.groupby('oficinas_atividades_list').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Realização de oficinas e atividades')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("38_oficinas_atividades.png")
plt.show()
# %%

# Verificação aleatória de prontuários/fichas
# ----------------------------
# %%
# Regulação
# UBS que o residente é encaminhado quando necessário
# -----------------------------

ubs = (df[["institution_name", "ubs", "ubs_1", "ubs_2"]]
       .rename(columns={"institution_name": "ILPI"})
)

ubs
# %%
# --------------------
# Gráfico 40 - UBS que o residente é encaminhado quando necessário

plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
ubs.groupby('ubs_list').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('UBS que o residente é encaminhado quando necessário')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("40_ubs.png")
plt.show()
# %%
# -----------------------------
# UPA que o residente é encaminhado quando necessário
upa = (df[["institution_name", "upa", "upa_1", "upa_2"]]
       .rename(columns={"institution_name": "ILPI"})
)
upa
# %%
# Tratar os dados UPA
# ---------------------------

# Função para dividir a coluna `upa` em partes com base nos delimitadores
def split_upa(value):
    if pd.isna(value):
        return []
    # Dividir o valor da coluna usando os delimitadores "/" e ";"
    parts = [part.strip() for part in re.split(r"[;/]", value)]
    return parts

# Aplicar a função para dividir a coluna `upa` em múltiplas colunas
upa_split = upa['upa'].apply(split_upa)

# Expandir a lista resultante em novas colunas
max_splits = upa_split.map(len).max()  # Número máximo de partes para ajustar o número de colunas
upa_cols = pd.DataFrame(upa_split.tolist(), columns=[f"upa_{i}" for i in range(max_splits)])

# Concatenar com o DataFrame original
df_upa = pd.concat([upa[['institution_name']], upa_cols], axis=1)

# Exibir o resultado
df_upa
# %%
# Gráfico 41 - UPA que o residente é encaminhado quando necessário
# --------------------
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
upa.groupby('upa_list').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('UPA que o residente é encaminhado quando necessário')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("41_upa.png")
plt.show()
# %%
# ILPI é campo de estágio
# -------------------------
estagio = (df[["institution_name", "internship"]]
           .assign(df_filtered=df["internship"].map({1:"Sim", 2:"Não"}))
           [["institution_name", "df_filtered"]]
           .rename(columns={"institution_name": "ILPI", "internship" : "campo_estágio"})
)
# %%
# Gráfico 42 - ILPI é campo de estágio
# -------------------------
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
estagio.groupby('campo_estágio').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('ILPI é campo de estágio')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("42_estagio.png")
plt.show()
# %%
# Quais são as instituíções de ensino e cursos
# -------------------------
inst_curso = (df[["institution_name", "internship_institution", "internship_institution_2", "internship_institution_3",
                "internship_institution_4","internship_course","internship_course_2","internship_course_3","internship_course_4"]]
                .rename(columns={"institution_name": "ILPI", "internship_institution" : "Instituíção A", "internship_institution_2" : "Instituíção B",
                                 "internship_institution_3": "Instituíção C", "internship_institution_4":"Instituíção D","internship_course":"Curso A",
                                 "internship_course_2": "Curso B","internship_course_3": "Curso C","internship_course_4": "Curso C"})
)

inst_curso
# %%
# Gráfico 43 - Quais são as instituíções de ensino e cursos
# -------------------------
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
inst_curso.groupby('ILPI').size().plot(
    kind='barh',
    color=['#4E79A7', '#F28E2B']
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Quais são as instituíções de ensino e cursos')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
        color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('ILPIs')
plt.ylabel('')

# Exibir gráfico
plt.savefig("43_inst_curso.png")
plt.show()
# %%