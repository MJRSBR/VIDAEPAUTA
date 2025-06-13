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

# %%
# ---------------------
# Análises e Gráficos
# ---------------------

## --- Camas segundo a norma
camas = processa_binario(df, 'residents_bedroom', 'Camas segundo a Norma?', {1: 'Sim', 2: 'Não'})

#salvar_tabela_pdf_reportlab(camas, '../output/camas.pdf')
criar_diretorios()

# Salvando como imagem
salvar_tabela_como_imagem(
    camas,
    '01_tabela_camas.png',
    titulo='Camas segundo a Norma nas ILPIs'
)

# Gráfico 01
camas_counts = camas['Camas segundo a Norma?'].value_counts()

plot_barh(camas_counts, 
          'Distribuição de Camas segundo a Norma', 
          'ILPIs', '01_camas_norma.png'
)

## --- Veículo

veiculo = processa_binario(df, 'vehicle', 'Existe veículo à disposição?', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    veiculo,
    "02_tabela_veiculo.png",
    titulo="Existe veículo à disposição da ILPI?"
)

veiculo_counts = veiculo['Existe veículo à disposição?'].value_counts()

plot_barh(veiculo_counts, 
          'Existe veículo à disposição nas ILPIs', 
          'ILPIs', '02_veiculo.png'
)

## --- Profissionais
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

df_profissionais = pd.concat(
    [
        df[df[col] >= 1][['institution_name', days_col]]
        .assign(profissional=prof)
        .rename(columns={days_col: 'Dias_por_mes', 'institution_name': 'ILPI'})
        .assign(Dias_por_mes=lambda x: x['Dias_por_mes'].round(1))
        [['ILPI', 'profissional', 'Dias_por_mes']]
        for prof, col, days_col in profissionais_mapping
    ]
).dropna(subset=['Dias_por_mes']).sort_values(by=['ILPI', 'profissional']).reset_index(drop=True)

salvar_tabela_como_imagem(df_profissionais, '03_tabela_profissionais.png')

plt.figure(figsize=(10, 6))
sns.barplot(x='profissional', y='Dias_por_mes', data=df_profissionais)
plt.xticks(rotation=45, ha='right')
plt.text(0.02, 24.0, '* Uma das instituições é composta por unidades de moradia',
         color='red', ha='left', va='bottom', wrap=True)
plt.xlabel('Profissão')
plt.ylabel('Dias por Mês')
plt.title('Dias Trabalhados por Mês por Profissão')
plt.tight_layout()
plt.savefig('03_profissionais.png')
plt.show()

## --- Vínculo Empregatício
vinculo_cols = {
    'employment_relatioship___1': 'CLT',
    'employment_relatioship___2': 'Contrato',
    'employment_relatioship___3': 'Voluntário'
}
vinculo = processa_multiresposta(df, vinculo_cols, 'Vinculo_empregaticio')

salvar_tabela_como_imagem(
    vinculo,
    "04_tabela_vinculo.png",
    titulo="Vínculo Empregatício dos Profissionais das ILPIs?"
)

vinculo_counts = vinculo['Vinculo_empregaticio'].value_counts()
plot_barh(vinculo_counts, 'Vínculo Empregatício dos Profissionais das ILPIs', 'ILPIs', '../plots/04_vinculo_empreg.png')

## --- Plano de Reabilitação
plano_cols = {
    'physio_program___1': 'Melhoria do tônus muscular',
    'physio_program___2': 'Equilíbrio funcionalidade motora',
    'physio_program___3': 'Bem-estar geral com indicação do destinatário',
    'physio_program___4': 'Não existe plano'
}
plano = processa_multiresposta(df, plano_cols, 'Plano_Reabilitacao')

salvar_tabela_como_imagem(
    vinculo,
    "../tables/05_tab_plano_reab.png",
    titulo="Plano/programa semanal de atividade física e reabilitação funcional"
)

plano_counts = plano['Plano_Reabilitacao'].value_counts()
plot_barh(plano_counts, 'Plano/programa semanal de atividade física e reabilitação funcional',
          'ILPIs', '05_plano_reabilitacao.png')

## --- Instruções do fisioterapeuta
instr_fisio = processa_binario(df, 'physio_instructions', 'Instrucao_fisioterapeuta', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    instr_fisio,
    "06_tab_instr_fisio.png"

)
instr_counts = instr_fisio['Instrucao_fisioterapeuta'].value_counts()
plot_barh(instr_counts, 'Instruções do fisioterapeuta ao cuidador está documentada?',
          'ILPIs', '06_instrucao_fisioterapeuta.png')


## --- Sistema de Segurança
sist_seg = processa_binario(df, 'secutiry_system', 'Sistemas_segurança', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    sist_seg,
    '07_tab_sist_seg.png'
)
sist_counts = sist_seg['Sistemas_segurança'].value_counts()
plot_barh(sist_counts, 'Existe Sistema de Segurança na ILPI?', 'ILPIs', '07_sistema_seguranca.png')

## --- Tipos de Sistema de Segurança
tipos_sist_cols = {
    'security_device_type___1': 'Alarme (incêndio/violação)',
    'security_device_type___2': 'Câmeras internas',
    'security_device_type___3': 'Câmeras externas',
    'security_device_type___4': 'Segurança (indivíduo)',
    'security_device_type___5': 'Segurança armada (indivíduo)'
}
tipos_sist = processa_multiresposta(df, tipos_sist_cols, 'Tipos_Sist_Seguranca')

salvar_tabela_como_imagem(
    tipos_sist,
    "08_tab_tipos_sist_seg.png"
)

tipos_counts = tipos_sist['Tipos_Sist_Seguranca'].value_counts()
plot_barh(tipos_counts, 'Tipo de Sistema de Segurança', 'ILPIs', '08_tipos_sist_seg.png')

## - Dispositivo/mecanismo (digital/analógico) de chamada
disp_chamada = processa_binario(df, 'safety_device_availability', 'Disponibilidade_disp_chamada', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    disp_chamada,
    '09_tab_disp_chamada.png'
)

disp_chamada_counts = disp_chamada['Disponibilidade_disp_chamada'].value_counts()
plot_barh(disp_chamada_counts, 'Dispositivo/mecanismo (digital/analógico) de chamada', 'ILPIs', '09_disp_chamada.png')

## - Iluminação
iluminacao = processa_binario(df, 'lighting', 'Iluminacao_adequada', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    iluminacao,
    '10_tab_iluminacao.png'
)

iluminacao_counts = iluminacao['Iluminacao_adequada'].value_counts()
plot_barh(iluminacao_counts, 'A iluminação é adequada?', 'ILPIs', '10_iluminacao.png')
# %%
## - Ventilação adequada
ventilacao = processa_binario(df, 'ventilation', 'ventilacao_adequada', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    ventilacao,
    '11_tab_ventilacao.png'
)

ventilacao_counts = ventilacao['ventilacao_adequada'].value_counts()
plot_barh(ventilacao_counts, 'A ventilação é adequada?', 'ILPIs', '11_ventilacao.png')
# %%
## - Pintura do quarto tons pastéis
pintura_quartos=processa_binario(df, 'painting_color', 'pintura_tons_pastel', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    pintura_quartos,
    '12_tab_pintura.png'
)

pintura_quartos_counts = pintura_quartos['pintura_tons_pastel'].value_counts()
plot_barh(
    pintura_quartos_counts, "Quartos pintados em tons pastel", "ILPI",
    '12_pintura.png'
)
# %%
## - Acessibilidade para o residente
## - Quarto

accessib_quarto_cols = {
    "room_access___1" : 'Portas largas para cadeirante', 
    "room_access___2" : 'Rampas', 
    "room_access___3" : 'Corrimão para apoio'
}
acessib_quarto = processa_multiresposta(df, accessib_quarto_cols, 'Acessibildade_quarto')

salvar_tabela_como_imagem(
    acessib_quarto,
    '13_tab_acessib_quarto.png'
)

acessib_quarto_counts = acessib_quarto['Acessibildade_quarto'].value_counts()
plot_barh(acessib_quarto_counts, 'Tipo de acessibilidade ao quarto do residente', 'ILPIs', '13_acessib_quarto.png')
# %%
## - Banheiro
accessib_banheiro_cols = {
    "bathroom_access___1" : 'Portas largas para cadeirante', 
    "bathroom_access___2" : 'Rampas', 
    "bathroom_access___3" : 'Corrimão para apoio'
}
acessib_banheiro = processa_multiresposta(df, accessib_banheiro_cols, 'Acessibildade_banheiro')

salvar_tabela_como_imagem(
    acessib_banheiro,
    '14_tab_acessib_banheiro.png'
)

acessib_banheiro_counts = acessib_banheiro['Acessibildade_banheiro'].value_counts()
plot_barh(acessib_banheiro_counts, 'Tipo de acessibilidade ao banheiro do residente', 'ILPIs', '14_acessib_banheiro.png')
# %%
## - Refeitório
accessib_refeitorio_cols = {
    "cafeteria___1" : 'Portas largas para cadeirante', 
    "cafeteria___2" : 'Rampas', 
    "cafeteria___3" : 'Corrimão para apoio'
}
acessib_refeitorio = processa_multiresposta(df, accessib_refeitorio_cols, 'Acessibildade_refeitorio')

salvar_tabela_como_imagem(
    acessib_refeitorio,
    '15_tab_acessib_refeitorio.png'
)

acessib_refeitorio_counts = acessib_refeitorio['Acessibildade_refeitorio'].value_counts()
plot_barh(acessib_refeitorio_counts, 'Tipo de acessibilidade ao refeitorio do residente', 'ILPIs', '15_acessib_refeitorio.png')
# %%
## - Outras áreas
accessib_outras_areas_cols = {
    "other_areas___1" : 'Portas largas para cadeirante', 
    "other_areas___2" : 'Rampas', 
    "other_areas___3" : 'Corrimão para apoio'
}
acessib_outras_areas = processa_multiresposta(df, accessib_outras_areas_cols, 'Acessibildade_outras_areas')

salvar_tabela_como_imagem(
    acessib_outras_areas,
    '16_tab_acessib_outras_areas.png'
)

acessib_outras_areas_counts = acessib_outras_areas['Acessibildade_outras_areas'].value_counts()
plot_barh(acessib_outras_areas_counts, 'Tipo de acessibilidade ao outras_areas do residente', 'ILPIs', '16_acessib_outras_areas.png')
# %%
## - Os profissionais da ILPI utilizam qualquer tipo de EPI's, durante no cuidado com os idosos
uso_epi =processa_binario(df, 'epi_use', "Uso_equip_seguranca", {1: 'Sim', 2:'Não'})
# %%
salvar_tabela_como_imagem(
    uso_epi,
    '17_tab_uso_epi.png'
)

uso_epi_counts = uso_epi['Uso_equip_seguranca'].value_counts()
plot_barh(uso_epi_counts, 'Uso de Equipamentos de Segurança', 'ILPI', '17_uso_epi.png')

# %