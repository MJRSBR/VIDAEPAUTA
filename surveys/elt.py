# %%

import pandas as pd

# %%
df = pd.read_csv("../data/MonitoramentoEDiagns_DATA_2024-11-27_1052.csv")
df.head()
# %%
df.columns
# %%
# Suprimindo colunas
df = df.drop(columns=['record_id', 'caracterizao_da_ilpi_complete', 'profissionais_da_ilpi_complete', 'segurana_e_ambiente_complete', 'organizao_da_farmcia_complete',
                      'servio_lavanderia_complete', 'processos_de_cuidado_complete', 'regulao_complete', 'encerramento_complete'])
df.head()

# %%

df.to_csv("../data/base_ilpi.csv")

# %%
