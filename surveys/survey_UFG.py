# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
# %%
df = pd.read_csv("../data/base_ilpi.csv")
df.head()

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

# Contando os valores de 'Camas segundo a Norma?' (Sim e Não)
counts = camas['Camas segundo a Norma?'].value_counts()

# Criando o gráfico de barras horizontais
counts.plot(kind='barh', color=['blue', 'orange'])

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Adicionando título e rótulos
plt.title('Distribuição de Camas segundo a Norma')
plt.xlabel('Número de Instituições')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
         color='red',ha='left', va='bottom', wrap=True)
plt.ylabel('')

# Exibindo o gráfico
plt.savefig('camas_norma.png')
plt.show()

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

# Contando os valores de veículos a disposição (Sim e Não)
counts = veiculo['Existe veículo à disposição?'].value_counts()

# Criando o gráfico de barras horizontais
counts.plot(kind='barh', color=['blue', 'orange'])

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Adicionando título e rótulos
plt.title('Existe veículo à disposição da ILPI?')
plt.text(0.02, 1.3,'* Uma das instituíções é composta por unidades de moradia',
         color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('Número de Instituições')
plt.ylabel('')

# Exibindo o gráfico
plt.savefig('veiculo.png')
plt.show()

# %%
# ------------------------------------------------------------------------------
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
# Criando gráfico
plt.figure(figsize=(10, 6))
sns.barplot(x='profissional', y='Dias_por_mes', data=df_profissionais)
plt.xticks(rotation=45, ha='right') # Rotate x-axis labels for better readability
plt.text(0.02, 24.0,'* Uma das instituíções é composta por unidades de moradia',
         color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('Profissão')
plt.ylabel('Dias por Mês')
plt.title('Dias Trabalhados por Mês por Profissão')
plt.tight_layout()

plt.savefig('profissionais.png')
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

# Gráfico Vínculo Empregatício
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
plt.xlabel('Número de Instituições')
plt.ylabel('Tipo de Vínculo')

# Exibir gráfico
plt.savefig("vinculo_empreg.png")
plt.show()

# %%
#--------------------------------------------------------------------------------------------------
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
            df["physio_program___3"].map(lambda x: ', bem-estar geral com indicação dos destinatário' if x == 1 else '') +
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
# Gráfico Planos de Reabilitaçao

# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
plano_reab.groupby('plano_reabilitacao').size().plot(
    kind='barh',
    color=sns.palettes.mpl_palette('Dark2')
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Plano/programa semanal de atividade física e reabilitação funcional')
plt.text(-4, 1.3,'* Uma das instituíções é composta por unidades de moradia',
         color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('Número de Instituições')
plt.ylabel('Atividades')

# Exibir gráfico
plt.savefig("plano_reab.png")
plt.show()

# %%
#-------------------------------------------------------------------------------------------------------

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

# Contando os valores de 'Instrucao_fisioterapeuta' (Sim e Não)
#instr_fisio = instr_fisio['Instrucao_fisioterapeuta'].value_counts().isna()
counts = instr_fisio['Instrucao_fisioterapeuta'].value_counts()

# Criando o gráfico de barras horizontais
counts.plot(kind='barh', color=['blue', 'orange'])


# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Adicionando título e rótulos
plt.title('Instruções do fisioterapeuta ao cuidador está documentada?')
plt.xlabel('Número de Instituições')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
         color='red',ha='left', va='bottom', wrap=True)
plt.ylabel('')

# Exibindo o gráfico
plt.savefig('instr_fisio.png')
plt.show()
# %%
#---------------------------------------------------------------------------------------
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

# Contando os valores de 'Sistemas_segurança' (Sim e Não)
sist_seg = sist_seg['Sistemas_segurança'].value_counts()

# Criando o gráfico de barras horizontais
counts.plot(kind='barh', color=['blue', 'orange'])

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Adicionando título e rótulos
plt.title('Existe Sistema de Segurança na ILPI?')
plt.xlabel('Número de Instituições')
plt.text(0.02, 1.3,'* Uma das instituíções é composta por unidades de moradia',
         color='red',ha='left', va='bottom', wrap=True)
plt.ylabel('')

# Exibindo o gráfico
plt.savefig('sist_seg.png')
plt.show()
# %%

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

# Visualizando o resultado
tipos_sist_seg
#%%

# Gráfico Tipos de Sistemas de Segurança

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
# %%
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

# Gráfico Dispositivos de Chamada 
# Tamanho da figura
plt.figure(figsize=(10, 6))

# Agrupar e plotar o gráfico de barras horizontais
disp_chamada.groupby('Disponibilidade_dispositivo_chamada').size().plot(
    kind='barh',
    color=["blue", "orange"]
)

# Ajustar bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo X seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Título e rótulos
plt.title('Dispositivo/mecanismo (digital/analógico) de chamada pelo residente')
plt.text(0.02, 0.3,'* Uma das instituíções é composta por unidades de moradia',
         color='red',ha='left', va='bottom', wrap=True)
plt.xlabel('Número de Instituições')
plt.ylabel('')

# Exibir gráfico
plt.savefig("disp_chamada.png")
plt.show()
# %%

# Iluminação adequada

iluminacao = (df[["institution_name", "lighting"]]
              .assign(df_filtered=df["lighting"].map({1 : "Sim", 2 : "Não"})) # Mapeando lighting
              [["institution_name", "df_filtered"]] # Selecionando colunas
              .rename(columns={"institution_name": "ILPI", "df_filtered": "Iluminacao_adequada"})
)

iluminacao
# %%

# Gráfico iluminação adequada

# Tamanho da figura
plt.figure(figsize=(10,6))

# Agrupar e plotar o gráfico de barras horizontais
iluminacao.groupby("Iluminacao_adequada").size().plot(
    kind='barh',
    color=["blue", "orange"]
)

# Ajustar as bordas
plt.gca().spines[['top', 'right']].set_visible(False)

# Garantir que o eixo x seja inteiro
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Títulos e rótulos
plt.title("A iluminição é adequada?")
plt.text(0.02, 1.3, '* Uma das institíções é composta por unidades de moradia',
         color='red', ha='left', va='bottom', wrap=True)
plt.xlabel('Intituíção')
plt.ylabel('')

# Exibir o gráfico
plt.savefig("iluminacao.png")
plt.show()
# %%

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
# Pintura do quarto tons pastéis