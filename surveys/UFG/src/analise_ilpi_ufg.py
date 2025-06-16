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
df = pd.read_csv('../../../data/base_ilpi.csv')
# %%
# --------------------
# Configurações Globais dos Gráficos
# ---------------------
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
# Ajustar a exibição do pandas para mostrar mais caracteres
pd.set_option('display.max_colwidth', None)  # Permite exibir a coluna inteira

# %%
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
import textwrap

def salvar_tabela_como_imagem(df, caminho_arquivo, titulo=None, largura_max_coluna=30):
    import matplotlib.pyplot as plt
    import textwrap

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


def criar_df_com_soma_por_prefixo(df, prefixo, nome_coluna_soma=None):
    """
    Retorna um novo DataFrame com as colunas que começam com o prefixo e uma coluna de soma.

    Parâmetros:
    - df: DataFrame original.
    - prefixo: Prefixo das colunas a incluir.
    - nome_coluna_soma: Nome da nova coluna de soma. Se None, será 'soma_' + prefixo.

    Retorna:
    - Novo DataFrame com as colunas selecionadas + coluna de soma.
    """
    # Filtra colunas com o prefixo
    colunas = [col for col in df.columns if col.startswith(prefixo)]

    # Garante que os dados sejam numéricos
    df_filtrado = df[colunas].apply(pd.to_numeric, errors='coerce')

    # Nome da nova coluna de soma
    if nome_coluna_soma is None:
        nome_coluna_soma = f'soma_{prefixo.rstrip("_")}'

    # Adiciona a soma por linha
    df_filtrado[nome_coluna_soma] = df_filtrado.sum(axis=1, numeric_only=True)

    return df_filtrado


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
    '../tables/01_tabela_camas.png',
    titulo='Camas segundo a Norma nas ILPIs',
    largura_max_coluna=25
)

# Gráfico 01
camas_counts = camas['Camas segundo a Norma?'].value_counts()

plot_barh(camas_counts, 
          'Distribuição de Camas segundo a Norma', 
          'ILPIs', '../plots/01_tabela_cama.png'
)
# %%
## --- Veículo

veiculo = processa_binario(df, 'vehicle', 'Existe veículo à disposição?', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    veiculo,
    "../tables/02_tabela_veiculo.png",
    titulo="Existe veículo à disposição da ILPI?"
)

veiculo_counts = veiculo['Existe veículo à disposição?'].value_counts()

plot_barh(veiculo_counts, 
          'Existe veículo à disposição nas ILPIs', 
          'ILPIs', '../plots/02_veiculo.png'
)
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

salvar_tabela_como_imagem(df_profissionais, '../tables/03_tabela_profissionais.png')

plt.figure(figsize=(10, 6))
sns.barplot(x='profissional', y='Dias_por_mes', data=df_profissionais)
plt.xticks(rotation=45, ha='right')
plt.text(0.02, 24.0, '* Uma das instituições é composta por unidades de moradia',
         color='red', ha='left', va='bottom', wrap=True)
plt.xlabel('Profissão')
plt.ylabel('Dias por Mês')
plt.title('Dias Trabalhados por Mês por Profissão')
plt.tight_layout()
plt.savefig('../plots/03_profissionais.png')
plt.show()
# %%
## --- Vínculo Empregatício
vinculo_cols = {
    'employment_relatioship___1': 'CLT',
    'employment_relatioship___2': 'Contrato',
    'employment_relatioship___3': 'Voluntário'
}
vinculo = processa_multiresposta(df, vinculo_cols, 'Vinculo_empregaticio')

salvar_tabela_como_imagem(
    vinculo,
    "../tables/04_tabela_vinculo.png",
    titulo="Vínculo Empregatício dos Profissionais das ILPIs?"
)

vinculo_counts = vinculo['Vinculo_empregaticio'].value_counts()
plot_barh(vinculo_counts, 'Vínculo Empregatício dos Profissionais das ILPIs', 'ILPIs', '../plots/04_vinculo_empreg.png')
# %%
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
          'ILPIs', '../plots/05_plano_reabilitacao.png')
# %%
## --- Instruções do fisioterapeuta
instr_fisio = processa_binario(df, 'physio_instructions', 'Instrucao_fisioterapeuta', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    instr_fisio,
    "../tables/06_tab_instr_fisio.png"

)
instr_counts = instr_fisio['Instrucao_fisioterapeuta'].value_counts()
plot_barh(instr_counts, 'Instruções do fisioterapeuta ao cuidador está documentada?',
          'ILPIs', '../plots/06_instrucao_fisioterapeuta.png')

# %%
## --- Sistema de Segurança
sist_seg = processa_binario(df, 'secutiry_system', 'Sistemas_segurança', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    sist_seg,
    '../tables/07_tab_sist_seg.png'
)
sist_counts = sist_seg['Sistemas_segurança'].value_counts()
plot_barh(sist_counts, 'Existe Sistema de Segurança na ILPI?', 'ILPIs', '../plots/07_sistema_seguranca.png')
# %%
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
    "../tables/08_tab_tipos_sist_seg.png"
)

tipos_counts = tipos_sist['Tipos_Sist_Seguranca'].value_counts()
plot_barh(tipos_counts, 'Contagem por Tipo de Sistema de Segurança', 'ILPIs', '../plots/08_tipos_sist_seg.png')
# %%
## - Dispositivo/mecanismo (digital/analógico) de chamada
disp_chamada = processa_binario(df, 'safety_device_availability', 'Disponibilidade_disp_chamada', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    disp_chamada,
    '../tables/09_tab_disp_chamada.png'
)

disp_chamada_counts = disp_chamada['Disponibilidade_disp_chamada'].value_counts()
plot_barh(disp_chamada_counts, 'Dispositivo/mecanismo (digital/analógico) de chamada', 'ILPIs', '../plots/09_disp_chamada.png')
# %%
## - Iluminação
iluminacao = processa_binario(df, 'lighting', 'Iluminacao_adequada', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    iluminacao,
    '../tables/10_tab_iluminacao.png'
)

iluminacao_counts = iluminacao['Iluminacao_adequada'].value_counts()
plot_barh(iluminacao_counts, 'A iluminação é adequada?', 'ILPIs', '../plots/10_iluminacao.png')
# %%
## - Ventilação adequada
ventilacao = processa_binario(df, 'ventilation', 'ventilacao_adequada', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    ventilacao,
    '../tables/11_tab_ventilacao.png'
)

ventilacao_counts = ventilacao['ventilacao_adequada'].value_counts()
plot_barh(ventilacao_counts, 'A ventilação é adequada?', 'ILPIs', '../plots/11_ventilacao.png')
# %%
## - Pintura do quarto tons pastéis
pintura_quartos=processa_binario(df, 'painting_color', 'pintura_tons_pastel', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    pintura_quartos,
    '../tables/12_tab_pintura.png'
)

pintura_quartos_counts = pintura_quartos['pintura_tons_pastel'].value_counts()
plot_barh(pintura_quartos_counts, "Quartos pintados em tons pastel", "ILPI",'../plots/12_pintura.png'
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
    '../tables/13_tab_acessib_quarto.png'
)

acessib_quarto_counts = acessib_quarto['Acessibildade_quarto'].value_counts()
plot_barh(acessib_quarto_counts, 'Tipo de acessibilidade ao quarto do residente', 'ILPIs', '../plots/13_acessib_quarto.png')
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
    '../tables/14_tab_acessib_banheiro.png'
)

acessib_banheiro_counts = acessib_banheiro['Acessibildade_banheiro'].value_counts()
plot_barh(acessib_banheiro_counts, 'Tipo de acessibilidade ao banheiro do residente', 'ILPIs', '../plots/14_acessib_banheiro.png')
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
    '../tables/15_tab_acessib_refeitorio.png'
)

acessib_refeitorio_counts = acessib_refeitorio['Acessibildade_refeitorio'].value_counts()
plot_barh(acessib_refeitorio_counts, 'Tipo de acessibilidade ao refeitorio do residente', 'ILPIs', '../plots/15_acessib_refeitorio.png')
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
    '../tables/16_tab_acessib_outras_areas.png'
)

acessib_outras_areas_counts = acessib_outras_areas['Acessibildade_outras_areas'].value_counts()
plot_barh(acessib_outras_areas_counts, 'Tipo de acessibilidade ao outras_areas do residente', 'ILPIs', '../plots/16_acessib_outras_areas.png')
# %%
## - Os profissionais da ILPI utilizam qualquer tipo de EPI's, durante no cuidado com os idosos
uso_epi =processa_binario(df, 'epi_use', "Uso_equip_seguranca", {1: 'Sim', 2:'Não'})

salvar_tabela_como_imagem(
    uso_epi,
    '../tables/17_tab_uso_epi.png'
)
 # CORRIGIR NAN
uso_epi_counts = uso_epi['Uso_equip_seguranca'].value_counts()
plot_barh(uso_epi_counts, 'Uso de Equipamentos de Segurança', 'ILPI',
          '../plots/17_uso_epi.png')

# %%
## - Medicamentos
## - Dentro prazo de validade
medic_prazo_val = processa_binario(df,'medication_val_date', 'Medicamento_prazo_validade',{1: 'Sim', 2:'Não'})

salvar_tabela_como_imagem(
    medic_prazo_val,
    '../tables/18_tab_medic_prazo.png'
)

medic_prazo_val_counts= medic_prazo_val['Medicamento_prazo_validade'].value_counts()
plot_barh(
    medic_prazo_val_counts,'Medicamento dentro do prazo de validade', 'ILPI',
    '../plots/18_medic_prazo.png'
)
# %%
## - Embalagem violada

emb_viol = processa_binario(df, 'violeted_pakage', 'Embalagem_violada', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    emb_viol,
    '../tables/19_tab_medic_emb_violada.png'
)

emb_viol_counts = emb_viol['Embalagem_violada'].value_counts()
plot_barh(
    emb_viol_counts,'Medicação com embalagem violada', 'ILPI',
    '../plots/19_medic_emb_violada.png'
)
# %%
## - Geladeira exclusiva ao armazenamento de medicamentos

geladeira_medic = processa_binario(df, 'medicine_refrigerator', 'Geladeira_exclusiva_medicamento', {1: 'Sim', 2: 'Não'})  

salvar_tabela_como_imagem(
    geladeira_medic,
    '../tables/20_tab_geladeira.png'
)

geladeira_medic_counts = geladeira_medic['Geladeira_exclusiva_medicamento'].value_counts()
plot_barh(
    geladeira_medic_counts,'Geladeira exclusiva para medicamentos', 'ILPI',
    '../plots/20_geladeira.png'
)
# %%
## - # Registro temperatura da geladeira

reg_temp_geladeira = processa_binario(df, 'refrigerator_temp_log', 'Registro_temperatura_geladeira', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    reg_temp_geladeira,
    '../tables/21_tab_reg_temp_geladeira.png'
)

reg_temp_geladeira_counts = reg_temp_geladeira['Registro_temperatura_geladeira'].value_counts()
plot_barh(
    reg_temp_geladeira_counts, 'Registro controle de temperatura da geladeira', 'ILPI',
    '../plots/21_reg_temp_geladeira.png'
)
# %%
## - Registro de utilização e frequência uso medicação

reg_medic = processa_binario(df, 'medication_register', 'Registro_uso_medicacao', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    reg_medic,
    '../tables/22_tab_reg_uso_medicamento.png'
)

reg_medic_counts = reg_medic['Registro_uso_medicacao'].value_counts()
plot_barh(
    reg_medic_counts, 'Registro do uso de medicação', 'ILPI',
    '../plots/22_reg_uso_medicamentos.png'
)
# %%
## - Tipo de registro da medicação

tipo_reg_medic_cols = {
    "medication_register_type___1" : 'Livro ata', 
    "medication_register_type___2" : 'Registro individual em papel',
    "medication_register_type___3" : 'Registro individual digital'
}

tipo_reg_medic = processa_multiresposta(df, tipo_reg_medic_cols, 'Tipo_registro_medicacao')

salvar_tabela_como_imagem(
    tipo_reg_medic,
    '../tables/23_tab_tipo_reg_medicacao.png'
)

tipo_reg_medic_counts = tipo_reg_medic['Tipo_registro_medicacao'].value_counts()
plot_barh(
    tipo_reg_medic_counts, 'Tipo de registro de medicamentos', 'ILPI',
    '../plots/23_tipo_reg_medicacao.png'
)
# %%
## - Substâncias Psicoativas/Psicotrópicas estão guardadas separadamente

med_psico_separado = processa_binario(df, 'psico_drugs_segregation', 'Subst_psico_segregada', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    med_psico_separado,
    '../tables/24_tab_subst_psico_segregada.png'
)

med_psico_separado_counts = med_psico_separado['Subst_psico_segregada'].value_counts()
plot_barh(
    med_psico_separado_counts, 'Substância psicoativa são segregadas', 'ILPI',
    '../plots/24_subst_psico_segregada.png'
)
# %%
## - Como são armazenadas as substâncias psicoativas

psico_armaz = processa_uma_variavel(df, {
    "institution_name": "ILPI",
    "psico_drugs_storage": "Onde_sao_armazenados_psicoativos"}
)
psico_armaz

salvar_tabela_como_imagem(
    psico_armaz,
    '../tables/25_tab_psico_armazenagem.png'
)

psico_armaz_counts = psico_armaz['Onde_sao_armazenados_psicoativos'].value_counts()
plot_barh(
    psico_armaz_counts, 'Onde são armazenados os psicoativos', 'ILPI',
    '../plots/25_psico_armazenagem.png'
)
# %%
## - Profissional que faz a separação da medicação a ser tomada pelos idosos
prof_manip_medic_cols = {
    "medication_manipulation___1" : 'técnico da farmácia', 
    "medication_manipulation___2" : 'farmacêutico(a)', 
    "medication_manipulation___3" : 'auxiliar de enfermagem',
    "medication_manipulation___4" : 'técnico de enfermagem', 
    "medication_manipulation___5" : 'enfermeiro(a)', 
    "medication_manipulation___6" : 'cuidador(a)', 
    "medication_manipulation___7" : 'outro'
}

prof_manip_medic = processa_multiresposta(df, prof_manip_medic_cols, 'Prof_manipula_medic_residente')

salvar_tabela_como_imagem(
    prof_manip_medic,
    '../tables/26_tab_prof_manipula_medic.png'
)

prof_manip_medic_counts = prof_manip_medic['Prof_manipula_medic_residente'].value_counts()
plot_barh(
    prof_manip_medic_counts, 'Profissional que faz a dispensação da medicação', 'ILPI',
    '../plots/26_prof_dispensa_medic.png'
)
# %%
## - Outro profissional
outro_profis = processa_uma_variavel(df,{
    'institution_name': "ILPI",
    'other_meditation_manip': 'Outro_prof_dispensa_medicamento'
})

salvar_tabela_como_imagem(
    outro_profis,
    '../tables/27_tab_outros_prof_dispensa.png'
)

outro_profis_counts = outro_profis['Outro_prof_dispensa_medicamento'].value_counts()
plot_barh(
    outro_profis_counts, 'Outro Profissional que faz a dispensação da medicação', 'ILPI',
    '../plots/27_outro_prof_dispensa_medic.png'

)
# %%
## - Quadro geral dispensação medicação

quadro_geral_disp = (prof_manip_medic.merge(outro_profis, on="ILPI", how="right"))

salvar_tabela_como_imagem(
    quadro_geral_disp,
    '../tables/28_tab_geral_outro_prof.png'
)
# %%
## - Serviço Lavanderia
## - Separação de roupas limpas e sujas

roupa_segreg = processa_binario(df, 'dirty_clothing_segregation', 'Separacao_roupas_sujas_limpas', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    roupa_segreg,
        '../tables/29_tab_roupa_segregada.png'
)

roupa_segreg_counts = roupa_segreg['Separacao_roupas_sujas_limpas'].value_counts()
plot_barh(
    roupa_segreg_counts, 'Segregação de roupas limpas/sujas', 'ILPI',
    '../plots/29_roupa_segregada.png'
)
# %%
## - Frequência de troca de roupas de cama e toalhas
mapa = {
    1: 'diário',
    2: 'semanal',
    3: 'quinzenal',
    4: 'mensal'
}

freq_troca_roupa_cama = processa_uma_variavel_com_opcoes(
    df,
    "dirty_clothing_change",
    "freq_troca_roupa_cama_list",
    mapa
)

salvar_tabela_como_imagem(
    freq_troca_roupa_cama,
    '../tables/30_tab_freq_troca_roupa.png'
)

freq_troca_roupa_cama_counts = freq_troca_roupa_cama['freq_troca_roupa_cama_list'].value_counts()
plot_barh(freq_troca_roupa_cama_counts, 'Frequência da troca de roupa de cama', 'ILPI', '../plots/30_freq_troca_roupa.png')
# %%
# Gerenciamento Resíduos
# ---------------------------
# Separação do lixo (orgânico/reciclável)

reciclagem_lixo = processa_binario(df, 'trash_recicling', 'Reciclagem_lixo', {1: 'Sim', 2: 'Não'})

salvar_tabela_como_imagem(
    reciclagem_lixo,
    '../tables/31_tab_reciclagem_lixo.png'
)

reciclagem_lixo_counts = reciclagem_lixo['Reciclagem_lixo'].value_counts()
plot_barh(
    reciclagem_lixo_counts, 'Reciclagem de lixo', 'ILPI',
    '../plots/31_reciclagem de lixo.png'
)
# %%
# Recipientes adequados e devidamente rotulados para descarte dos diferentes tipos de resíduos
# ---------------------------
container_adequados_cols = {
    "trash_container___1" : 'Resíduo infectante', 
    "trash_container___2" : 'Resíduo químico', 
    "trash_container___3" : 'Resíduo radioativo', 
    "trash_container___4" : 'Resíduo perfurocortante',
    "trash_container___5" : 'Resíduo comum'
}

container_adequados = processa_multiresposta(df, container_adequados_cols, 'container_adequados_list')

salvar_tabela_como_imagem(
    container_adequados,
    '../tables/32_tab_container_adeq.png'
)

container_adequados_counts = container_adequados['container_adequados_list'].value_counts()
plot_barh(
    container_adequados_counts, 'Os conteiners de lixo são adequados', 'ILPI',
    '../plots/32_container_adequado.png'
)
# %%
## - Processos de Cuidado
## - Área para que o residente possa tomar um banho de sol

banho_sol = processa_binario(df, 'sunbathing', 'Area_banho_sol', {1: 'Sim', 2:'Não'})

salvar_tabela_como_imagem(
    banho_sol,
    '../tables/33_tab_banho_sol.png'
)

banho_sol_counts = banho_sol['Area_banho_sol'].value_counts()
plot_barh(
    banho_sol_counts, 'Area de banho de sol', 'ILPI',
    '../plots/33_banho_sol.png'
)
# %%
## - Área recebimento de visitas e familiares
# ----------------------
area_vis_familia = processa_binario(df, 'visiting_area', 'Area_visitacao_familia', {1: 'Sim', 2:'Não'})

salvar_tabela_como_imagem(
    area_vis_familia,
    '../tables/34_tab_visit_familia.png'
)

area_vis_familia_counts = area_vis_familia['Area_visitacao_familia'].value_counts()
plot_barh(
    area_vis_familia_counts, 'Area para visitação familiar', 'ILPI',
    '../plots/34_visit_familia'
)
# %%
## - Área de atividades sociais
area_ativ_social = processa_binario(df, 'social_area', 'Area_ativ_social', {1: 'Sim', 2:'Não'})

salvar_tabela_como_imagem(
    area_ativ_social,
    '../tables/35_tab_area_social.png'
)

area_ativ_social_counts = area_ativ_social['Area_ativ_social'].value_counts()
plot_barh(
    area_ativ_social_counts, 'Area para atividades sociais', 'ILPI',
    '../plots/35_area_social'
)
# %%
## - Música ambiente na ILPI
musica_ambiente = processa_binario(df, 'ambient_music', 'Musica_ambiente', {1: 'Sim', 2:'Não'})

salvar_tabela_como_imagem(
    musica_ambiente,
    '../tables/36_tab_musica_ambiente.png'
)

musica_ambiente_counts = musica_ambiente['Musica_ambiente'].value_counts()
plot_barh(
    musica_ambiente_counts, 'Musica ambiente', 'ILPI',
    '../plots/36_musica_ambiente.png'
)
# %%
## - Cardápio visível para consulta
cardapio_visivel = processa_binario(df, 'menu', 'Cardapio_visivel', {1: 'Sim', 2:'Não'})

salvar_tabela_como_imagem(
    cardapio_visivel,
    '../tables/37_tab_cardapio_visivel.png'
)

cardapio_visivel_counts = cardapio_visivel['Cardapio_visivel'].value_counts()
plot_barh(
    cardapio_visivel_counts, 'Cardápio está visível', 'ILPI',
    '../plots/37_cardapio_visivel.png'
)
# %%
## - Frequência que o cardápio é atualizado
mapa = {
    1: 'diário',
    2: 'semanal',
    3: 'quinzenal',
    4: 'mensal'
}

freq_atualiz_cardapio = processa_uma_variavel_com_opcoes(
    df,
    'semanal_menu',
    'freq_atualiz_cadapio_list',
    mapa
)

salvar_tabela_como_imagem(
    freq_atualiz_cardapio,
    '../tables/38_tab_freq_atual_cardapio.png'
)

freq_atualiz_cardapio_counts = freq_atualiz_cardapio['freq_atualiz_cadapio_list'].value_counts()
plot_barh(
    freq_atualiz_cardapio_counts, 'Frequência de atualização do cardápio', 'ILPI',
    '../plots/38_freq_atualiz_cardapio.png'
)
# %%
## - Realização de oficinas e atividades
oficinas_atividades_cols = {
    "recreation_type___1" : 'Oficina de jardinagem',
    "recreation_type___2" : 'Oficina de costura', 
    "recreation_type___3" : 'Oficina de artesanato',
    "recreation_type___4" : 'Oficina de marcenaria', 
    "recreation_type___5" : 'Dança de salão', 
    "recreation_type___6" : 'Datas comemorativas', 
    "recreation_type___7" : 'Missas/Cultos Ecumênicos'
}

oficinas_atividades = processa_multiresposta(df, oficinas_atividades_cols, 'Oficinas_ atividades')

salvar_tabela_como_imagem(
    oficinas_atividades,
    '../tables/39_tab_oficinas_atividades.png'
)

oficinas_atividades_counts = oficinas_atividades['Oficinas_ atividades'].value_counts()
plot_barh(
    oficinas_atividades_counts, 'Existência oficinas ou atividades para os residentes', 'ILPI',
    '../plots/39_oficinas_atividades.png'
)
# %%

## - Verificação aleatória de pelo menos 5 prontuários/fichas e/ou documentação de saúde e enfermagem

verif_reg = df[[
    'institution_name', 'medical_record___1', 'medical_record___2',	'medical_record___3', 'medical_record___4',
    'medical_record___5', 'medical_record___6',	'admission_file_signed___1', 'admission_file_signed___2', 
    'admission_file_signed___3', 'admission_file_signed___4', 'admission_file_signed___5', 'admission_file_signed___6',
    'patient_bath___1', 'patient_bath___2',	'patient_bath___3',	'patient_bath___4','patient_bath___5', 'patient_bath___6',
    'imc_index___1','imc_index___2', 'imc_index___3', 'imc_index___4', 'imc_index___5', 'imc_index___6', 
    'physical_cont_record___1',	'physical_cont_record___2',	'physical_cont_record___3',	'physical_cont_record___4',
    'physical_cont_record___5', 'physical_cont_record___6',	'mem_scale___1', 'mem_scale___2', 'mem_scale___3', 
    'mem_scale___4', 'mem_scale___5', 'mem_scale___6', 'mem_prev_actions___1', 'mem_prev_actions___2', 'mem_prev_actions___3',
    'mem_prev_actions___4',	'mem_prev_actions___5',	'mem_prev_actions___6',	'pain_register___1', 'pain_register___2',	
    'pain_register___3', 'pain_register___4', 'pain_register___5', 'pain_register___6',	'meem_care_actions___1',
    'meem_care_actions___2', 'meem_care_actions___3', 'meem_care_actions___4', 'meem_care_actions___5',	'meem_care_actions___6',
    'rehab_activities_register___1', 'rehab_activities_register___2', 'rehab_activities_register___3', 'rehab_activities_register___4',
    'rehab_activities_register___5', 'rehab_activities_register___6', 'rehab_activities___1', 'rehab_activities___2', 
    'rehab_activities___3',	'rehab_activities___4',	'rehab_activities___5',	'rehab_activities___6']]

verif_reg
# %%

dic_renomear_med_rec = {
    'institution_name': 'ILPI',
    'medical_record___1': 'Não se aplica'
}

df_medical_record = verif_reg[['institution_name']].copy()
df_medical_record = (df_medical_record.join(criar_df_com_soma_por_prefixo(verif_reg, "medical_record___"))
                     .rename(columns=dic_renomear_med_rec))

df_medical_record

salvar_tabela_como_imagem(
    df_medical_record,
    '../tables/40_tab_verif_reg_medic.png'
)
# %%

dic_renomear_admiss_file = {
    'institution_name': 'ILPI',
    'admission_file_signed___1': 'Não se aplica'
}

df_admiss_file = verif_reg[['institution_name']].copy()
df_admiss_file = (df_admiss_file.join(criar_df_com_soma_por_prefixo(verif_reg, 'admission_file_signed___'))
                  .rename(columns=dic_renomear_admiss_file))

salvar_tabela_como_imagem(
    df_admiss_file,
    '../tables/41_tab_verif_ficha_admissao.png'
)
# %%

dic_renomear_banho = {
    'institution_name': 'ILPI',
    'patient_bath___1': 'Não se aplica'
}

df_banho = verif_reg[['institution_name']].copy()
df_banho = (df_banho.join(criar_df_com_soma_por_prefixo(verif_reg, "patient_bath___"))
            .rename(columns=dic_renomear_banho))

salvar_tabela_como_imagem(
    df_banho,
    '../tables/42_tab_verif_banho_resid.png'
)
# %%
dic_renomear_imc_index = {
    'institution_name': 'ILPI',
    'imc_index___1': 'Não se aplica'
}

df_imc_index = verif_reg[['institution_name']].copy()
df_imc_index = (df_imc_index.join(criar_df_com_soma_por_prefixo(verif_reg, "imc_index___"))
            .rename(columns=dic_renomear_imc_index))

salvar_tabela_como_imagem(
    df_imc_index,
    '../tables/43_tab_verif_imc_index_resid.png'
)
# %%
dic_renomear_reg_fisico = {
    'institution_name': 'ILPI',
    'physical_cont_record___1': 'Não se aplica'
}

df_reg_fisico = verif_reg[['institution_name']].copy()
df_reg_fisico = (df_reg_fisico.join(criar_df_com_soma_por_prefixo(verif_reg, "physical_cont_record___"))
            .rename(columns=dic_renomear_reg_fisico))

salvar_tabela_como_imagem(
    df_reg_fisico,
    '../tables/44_tab_verif_reg_fisico_resid.png'
)
# %%
dic_renomear_escala_mem = {
    'institution_name': 'ILPI',
    'mem_scale___1': 'Não se aplica'
}

df_escala_mem = verif_reg[['institution_name']].copy()
df_escala_mem = (df_escala_mem.join(criar_df_com_soma_por_prefixo(verif_reg, "mem_scale___"))
            .rename(columns=dic_renomear_escala_mem))

salvar_tabela_como_imagem(
    df_escala_mem,
    '../tables/45_tab_verif_escala_mem.png'
)
# %%
dic_renomear__mem_ac_prev = {
    'institution_name': 'ILPI',
    'mem_prev_actions___1': 'Não se aplica'
}

df_mem_ac_prev = verif_reg[['institution_name']].copy()
df_mem_ac_prev = (df_mem_ac_prev.join(criar_df_com_soma_por_prefixo(verif_reg, "mem_prev_actions___"))
            .rename(columns=dic_renomear__mem_ac_prev))

salvar_tabela_como_imagem(
    df_mem_ac_prev,
    '../tables/45_tab_verif__mem_ac_prev.png'
)
# %%
dic_renomear_reg_dor = {
    'institution_name': 'ILPI',
    'pain_register___1': 'Não se aplica'
}

df_reg_dor = verif_reg[['institution_name']].copy()
df_reg_dor = (df_reg_dor.join(criar_df_com_soma_por_prefixo(verif_reg, "pain_register___"))
            .rename(columns=dic_renomear_reg_dor))

salvar_tabela_como_imagem(
    df_reg_dor,
    '../tables/46_tab_verif_reg_dor.png'
)
# %%

dic_renomear_mem_acao_cuid = {
    'institution_name': 'ILPI',
    'meem_care_actions___1': 'Não se aplica'
}

df_mem_acao_cuid = verif_reg[['institution_name']].copy()
df_mem_acao_cuid = (df_mem_acao_cuid.join(criar_df_com_soma_por_prefixo(verif_reg, "meem_care_actions___"))
            .rename(columns=dic_renomear_mem_acao_cuid))

salvar_tabela_como_imagem(
    df_mem_acao_cuid,
    '../tables/47_tab_verif_mem_acao_cuid.png'
)
# %%

dic_renomear_reg_ativ_reab = {
    'institution_name': 'ILPI',
    'rehab_activities_register___1': 'Não se aplica'
}

df_reg_ativ_reab = verif_reg[['institution_name']].copy()
df_reg_ativ_reab = (df_reg_ativ_reab.join(criar_df_com_soma_por_prefixo(verif_reg, "rehab_activities_register___"))
            .rename(columns=dic_renomear_reg_ativ_reab))

salvar_tabela_como_imagem(
    df_reg_ativ_reab,
    '../tables/48_tab_verif_reg_ativ_reab.png'
)
# %%

dic_renomeaf_ativ_reab = {
    'institution_name': 'ILPI',
    'rehab_activities___1': 'Não se aplica'
}

df_ativ_reab = verif[['institution_name']].copy()
df_ativ_reab = (df_ativ_reab.join(criar_df_com_soma_por_prefixo(verif, "rehab_activities___"))
            .rename(columns=dic_renomeaf_ativ_reab))

salvar_tabela_como_imagem(
    df_ativ_reab,
    '../tables/49_tab_verif_ativ_reab.png'
)
# %%
## - Regulação
## - UBS que o residente é encaminhado quando necessário
ubs = (
    df[["institution_name", "ubs", "ubs_1", "ubs_2"]]
    .rename(columns={
        "institution_name": "ILPI",
        "ubs": "UBS",
        "ubs_1": "UBS_1",
        "ubs_2": "UBS_2"
    })
)

# Remove colunas onde todos os valores são None/NaN
ubs = ubs.dropna(axis=1, how='all')
ubs
# %%
salvar_tabela_como_imagem(
    ubs,
    '../tables/50_tab_ubs.png'
)

# %%
## - UPA que o residente é encaminhado quando necessário
upa = (
    df[["institution_name", "upa", "upa_1", "upa_2"]]
    .rename(columns={
        "institution_name": "ILPI", 
        'upa': 'UPA', 
        'upa_1': 'UPA_1', 
        'upa_2': 'UPA_2'})
)

upa

# %%
## -  Tratar os dados UPA

import re 
# Função para dividir a coluna `UPA` em partes com base nos delimitadores
def split_upa(value):
    if pd.isna(value):
        return []
    parts = [part.strip() for part in re.split(r"[;/]", value)]
    return parts

# Aplicar a função na coluna correta
upa_split = upa['UPA'].apply(split_upa)

# Expandir a lista resultante em novas colunas
max_splits = upa_split.map(len).max()
upa_cols = pd.DataFrame(upa_split.tolist(), columns=[f"UPA_{i}" for i in range(max_splits)])

# Concatenar com o DataFrame original
df_upa = pd.concat([upa[['ILPI']], upa_cols], axis=1)

# Exibir o resultado
df_upa


salvar_tabela_como_imagem(
    df_upa,
    '../tables/51_tab_upa.png'
)
# %%

## - Quadro Geral UBS e UPA

quadro_geral_ubs_upa = (ubs.merge(df_upa, on="ILPI", how="right"))
quadro_geral_ubs_upa
# %%
salvar_tabela_como_imagem(

    quadro_geral_ubs_upa,
    '../tables/52_tab_quadro_geral_ubs_upa.png'
)
# %%
## - ILPI é campo de estágio

estagio = processa_binario(df, 'internship', 'Campo_estagio', {1: 'Sim', 2:'Não'})

salvar_tabela_como_imagem(
    estagio,
    '../tables/53_tab_campo_estagio.png'
)

estagio_counts = estagio['Campo_estagio'].value_counts()
plot_barh(
    estagio_counts, 'A ILPI é campo de estágio', 'ILPI',
    '../plots/53_campo_estagio.png'
)
# %%
## - Quais são as instituíções de ensino e cursos
# -------------------------
inst_curso = (
    df[["institution_name", "internship_institution", "internship_institution_2", 
    "internship_institution_3", "internship_institution_4", "internship_course",
    "internship_course_2","internship_course_3","internship_course_4"]]
    .rename(columns={
        "institution_name": "ILPI", "internship_institution" : "Instituíção A", 
        "internship_institution_2" : "Instituíção B", "internship_institution_3": "Instituíção C", 
        "internship_institution_4":"Instituíção D","internship_course":"Curso A",
        "internship_course_2": "Curso B","internship_course_3": "Curso C",
        "internship_course_4": "Curso C"
        })
)

inst_curso
# %%
inst_curso = inst_curso.replace({
    'Não se aplica': '-',
    'NaN': '-',
    'nan': '-'}
)

inst_curso
# %%

inst_curso = inst_curso.replace({
    'NAN': '-'}
)

inst_curso
# %%
salvar_tabela_como_imagem(
    inst_curso,
    '../tables/54_tab_inst_cursos.png'
)
# %%
