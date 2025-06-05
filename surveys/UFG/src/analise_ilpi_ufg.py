# %%
# Bibliotecas
# --------------------
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_pdf import PdfPages # Salvar como PDF
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# %%
# ---------------------
# Leitura dos dados
df = pd.read_csv('../../../data/base_ilpi.csv')

# %%
# ---------------------
# Configurações Globais dos Gráficos
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# %%
# ------------------------------
# Funções utilitárias
# ------------------------------

def criar_diretorios():
    os.makedirs('../output', exist_ok=True)
    os.makedirs('../plots', exist_ok=True)

def salvar_tabela_pdf_reportlab(df, filename, title="Tabela"):
    """
    Salva uma tabela em PDF usando reportlab (visual profissional).
    """
    pdf = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter)
    )

    data = [df.columns.tolist()] + df.values.tolist()

    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4E79A7")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)

    elementos = [table]
    pdf.build(elementos)    


# Garante que use uma fonte bonita e limpa
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


def salvar_tabela_md(df, path):
    df.to_md(path, index=False)    


def plot_barh(data, title, xlabel, filename, color=['#4E79A7', '#F28E2B'], nota=True):
    """Gera um gráfico de barras horizontal."""
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

salvar_tabela_pdf_reportlab(camas, '../output/camas.pdf')

# Salvando como imagem
salvar_tabela_como_imagem(
    camas,
    '../output/tabela_camas.png',
    titulo='Camas segundo a Norma nas ILPIs'
)

camas_counts = camas['Camas segundo a Norma?'].value_counts()
plot_barh(camas_counts, 'Distribuição de Camas segundo a Norma', 'ILPIs', '01_camas_norma.png')
# %%
## --- Veículo
veiculo = processa_binario(df, 'vehicle', 'Existe veículo à disposição?', {1: 'Sim', 2: 'Não'})

salvar_tabela_pdf_reportlab(camas, '../output/camas.pdf')

veiculo_counts = veiculo['Existe veículo à disposição?'].value_counts()
plot_barh(veiculo_counts, 'Existe veículo à disposição nas ILPIs', 'ILPIs', '02_veiculo.png')
# %%
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

salvar_tabela_pdf_reportlab(df_profissionais, '../output/profissionais.pdf')

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
# %%
## --- Vínculo Empregatício
vinculo_cols = {
    'employment_relatioship___1': 'CLT',
    'employment_relatioship___2': 'Contrato',
    'employment_relatioship___3': 'Voluntário'
}
vinculo = processa_multiresposta(df, vinculo_cols, 'Vinculo_empregaticio')
vinculo_counts = vinculo['Vinculo_empregaticio'].value_counts()
plot_barh(vinculo_counts, 'Vínculo Empregatício dos Profissionais das ILPIs', 'ILPIs', '04_vinculo_empreg.png')

## --- Plano de Reabilitação
plano_cols = {
    'physio_program___1': 'Melhoria do tônus muscular',
    'physio_program___2': 'Equilíbrio funcionalidade motora',
    'physio_program___3': 'Bem-estar geral com indicação do destinatário',
    'physio_program___4': 'Não existe plano'
}
plano = processa_multiresposta(df, plano_cols, 'Plano_Reabilitacao')
plano_counts = plano['Plano_Reabilitacao'].value_counts()
plot_barh(plano_counts, 'Plano/programa semanal de atividade física e reabilitação funcional',
          'ILPIs', '05_plano_terapeutico.png')

## --- Instruções do fisioterapeuta
instr_fisio = processa_binario(df, 'physio_instructions', 'Instrucao_fisioterapeuta', {1: 'Sim', 2: 'Não'})
instr_counts = instr_fisio['Instrucao_fisioterapeuta'].value_counts()
plot_barh(instr_counts, 'Instruções do fisioterapeuta ao cuidador está documentada?',
          'ILPIs', '06_instrucao_fisioterapeuta.png')

## --- Sistema de Segurança
sist_seg = processa_binario(df, 'secutiry_system', 'Sistemas_segurança', {1: 'Sim', 2: 'Não'})
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
tipos_counts = tipos_sist['Tipos_Sist_Seguranca'].value_counts()
plot_barh(tipos_counts, 'Contagem por Tipo de Sistema de Segurança', 'ILPIs', '08_tipos_sist_seg.png')


# %%
