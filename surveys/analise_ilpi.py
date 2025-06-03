# %%
# Bibliotecas
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
# %%
# Leitura dos dados
df = pd.read_csv('../data/base_ilpi.csv')
# %%
# Configurações Globais dos Gráficos
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
# %%
# Função para plotar gráficos de barras horizontais
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
    'camas_norma.png'
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
    'Existe veículo à disposição?',
    'ILPIs',
    'veiculo.png'
)
# %%
# ---------------------
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
# Gráfico 3 - Plano Reabilitação

plano_counts = plano_reab['plano_reabilitacao'].value_counts()

plot_barh(
    plano_counts,
    'Plano/programa semanal de atividade física e reabilitação funcional',
    'ILPIs',
    'plano_terapeutico.png'
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
# Gráfico 4 - Instruções do Fisioterapeuta
instr_counts = instr_fisio['Instrucao_fisioterapeuta'].value_counts()

plot_barh(
    instr_counts,
    'Instruções do fisioterapeuta ao cuidador está documentada?',
    'ILPIs',
    'instrucao_fisioterapeuta.png'
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
# Gráfico 5 - Sistema de Segurança
sist_counts = sist_seg['Sistemas_segurança'].value_counts()

plot_barh(
    sist_counts,
    'Existe Sistema de Segurança na ILPI?',
    'ILPIs',
    'sistema_seguranca.png'
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
# Gráfico 6 - Tipos de Sistema de Segurança

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
plt.xlabel('Número de Instituições')
plt.ylabel('Tipo de Sistema de Segurança')

# Exibir gráfico
plt.savefig("tipos_sist_seg.png")
plt.show()
tipos_sist_seg_counts = tipos_sist_seg['tipos_sist_seguranca'].value_counts()

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
# Gráfico 7 Dispositivo/mecanismo (digital/analógico) de chamada
disp_chamada_counts = disp_chamada["Disponibilidade_dispositivo_chamada"].value_counts()

plot_barh(
    disp_chamada,
    'Dispositivo/mecanismo (digital/analógico) de chamada pelo residente',
    'ILPIs',
    'disp_chamada.png'
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

# Gráfico 8  iluminação adequada

iluminacao_counts = iluminacao['Iluminacao_adequada'].value_counts()

plot_barh(
    iluminacao,
    'A iluminição é adequada?',
    'ILPIs',
    'ilumincacao.png'
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

# Gráfico Ventilação Adequada
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
plt.xlabel('Intituíção')
plt.ylabel('')

# Exibir o gráfico
plt.savefig("ventilacao.png")
plt.show()
# %%
