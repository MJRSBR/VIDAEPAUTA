# %%

# Pacotes e bibliotecas 

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sqlite3
from matplotlib.backends.backend_pdf import PdfPages # Salvar como PDF
from matplotlib.ticker import MaxNLocator # Limitar número de ticks
# %%

df = pd.read_csv("/Users/mjrs/Library/CloudStorage/OneDrive-Pessoal/UFG/Projeto_VIDAEPAUTA/Códigos/SMSAp/VIDAEPAUTA/data/survey01.csv")
df.head()
# %%

# Dicionário mapeando os números aos nomes das ILPI's correspondentes
name_mapping = {
    1.0: 'Associação Solar das Acácias',
    2.0: 'Abrigo Comendador Walmor',
    3.0: 'Abrigo Aconchego Dona Norma',
    4.0: 'Associação Núcleo Espírita Amigos para Sempre',
    5.0: 'Casa Silvestre Linhares'
}

# Função map para substituir os valores na coluna 'institution_name'
df['institution_name'] = df['institution_name'].map(name_mapping)

df['institution_name']

# %%

# Lista das colunas do dataset
df.columns
# %%

# Suprimindo colunas
df = df.drop(columns=['record_id', 'visit_day', 'residentes_ilpis_complete',
       'identificao_da_ilpi_complete', 'identificao_do_idoso_complete',
       'medicamentos_em_uso_complete', 'morbidades_prvias_complete',
       'estado_de_sade_complete', 'componentes_de_fragilidade_complete',
       'responsvel_pelo_preenchimento_complete'])
df
# %%

#SELECT
#  institution_name,
#  count(elder_name) AS resident_number
#FROM resident
#GROUP BY institution_name

residents = (df.groupby("institution_name")
             .agg(resident_number=('elder_name', 'count'))
             .reset_index())
residents
# %%

# Dicionário com valores coletados nas ILPI's pela UFG 
updates = {
    'Abrigo Aconchego Dona Norma': 19,
    'Abrigo Comendador Walmor': 72,
    'Associação Núcleo Espírita Amigos para Sempre': 34,
    'Associação Solar das Acácias': 18,
    'Casa Silvestre Linhares': 41
}

# Atualizar o DataFrame com os valores do dicionário
residents["research_number"] = (
    residents['institution_name'].map(updates).fillna(residents['resident_number']).astype(int)
)

# Renomeando colunas
renamed_columns = {"resident_number" : "number_SMSApG", "research_number" : "number_UFG"}
residents = residents.rename(columns=renamed_columns)

# Resultado final
residents
# %%

# Criar gráfico comparativo entre number_SMSApG	 e number_UFG
plt.figure(figsize=(10, 6))
bar_width = 0.4

# Índices para posicionamento das barras
index = range(len(residents))

# Define as divisões de 10 em 10, de 0 até 80
plt.ylim(0, 80)
plt.yticks(np.arange(0, 81, 10))

# Barras originais
original_bars = plt.bar(
    index, residents['number_SMSApG'],
    width=bar_width,
    label='SMS',
    color='blue',
    alpha=0.7
)

# Barras atualizadas
updated_bars = plt.bar(
    [i + bar_width for i in index],
    residents['number_UFG'],
    width=bar_width,
    label='Pesquisa',
    color='orange',
    alpha=0.7
)

# Adicionar valores nas barras originais
for bar in original_bars:
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f'{int(bar.get_height())}',
        ha='center',
        va='bottom',
        fontsize=10,
        color='blue'
    )

# Adicionar valores nas barras atualizadas
for bar in updated_bars:
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f'{int(bar.get_height())}',
        ha='center',
        va='bottom',
        fontsize=10,
        color='orange'
    )

# Configuração dos rótulos e título
plt.ylabel('Residentes', fontsize=12)
plt.title('Comparação entre dados SMS e Pesquisa', fontsize=14)
plt.xticks([i + bar_width / 2 for i in index], residents['institution_name'], rotation=45, ha='right')
plt.legend()

# Exibir o gráfico
plt.tight_layout()
plt.savefig("Comparação de Residentes entre pesquisas")
plt.show()

# %%
