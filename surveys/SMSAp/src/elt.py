# %%
import pandas as pd
# %%
## ----------------------
## Função para facilitar a análise baseada em CPF, considerando que o DF tem colunas vazias ou NA.
## ----------------------

def etl_df_redcap(df, campos_chave, campo_discriminador='institution_name'):
    """
    Executa o pré-processamento (ETL) no DataFrame exportado do REDCap para análise posterior.
    Propaga campos-chave (ex: cpf, full_name) a partir de linhas onde há valor no campo_discriminador 
    (ex: institution_name).
    Substitui as colunas originais pelas propagadas sem sufixo.

    Uso: 
    campos_para_propagar = ['cpf', 'full_name', 'institution_name']
    df_corrigido = etl_df_redcap(df, campos_para_propagar)
    """
    # Copia o data frame para segurança
    df = df.copy()
    # Identifica início de novos grupos
    novo_grupo = df[campo_discriminador].notna() & (df[campo_discriminador] != 0)
    df['_grupo'] = novo_grupo.cumsum()

    for campo in campos_chave:
        # Cria coluna propagada
        coluna_propagada = df.groupby('_grupo')[campo].transform('first')

        ## Padroniza em caixa alta se for string
        #if pd.api.types.is_string_dtype(propagado):
        #    propagado = propagado.str.upper()
        
        # Remove coluna original e substitui pela propagada sem o sufixo
        df.drop(columns=[campo], inplace=True)
        df[campo] = coluna_propagada

    df.drop(columns=['_grupo'], inplace=True)
   
    return df
# %%
# Ajustar a exibição do pandas para mostrar mais caracteres
#pd.set_option('display.max_rows', None) #para mostrar todas as linhas. 
#
#pd.set_option('display.max_colwidth', None)  # Permite exibir a coluna inteira
# %%
df = pd.read_csv("../../../data/SMSap/PerfilEpidemiolgicos_DATA_2025-06-24_1507.csv",
                 sep=";")
df.head()

# %%
##  Checagem dos tipos de variáveis presentes no data frame
df.dtypes
# %%
## -------------------
## Fazendo o ajuste e propagando o CPF, nome e ILPI para as linha necessárias
## -------------------

campos_para_propagar = ['cpf', 'full_name', 'institution_name']
df_corrigido = etl_df_redcap(df, campos_para_propagar)
df_corrigido
# %%
# ## - Verificando se o CPF foi propagado corretamente e listando as colunas

print(df_corrigido[df_corrigido['cpf'].isna()])

# %%

# Transformando colunas em int
cols_to_convert = ['record_id','redcap_repeat_instance', 'institution_name', 'sex', 'elder_age', 
       'race', 'scholarship', 'institut_time_years', 'institut_time_months', 'family_support', 'dependence_degree', 
       'link_type___1', 'link_type___2', 'link_type___3', 'elder_income_source', 'taken_daily', 'morbidities___1', 
       'morbidities___2', 'morbidities___3', 'morbidities___4', 'morbidities___5', 'morbidities___6', 'morbidities___7',
       'morbidities___8', 'morbidities___9', 'morbidities___10', 'morbidities___11', 'morbidities___12', 'morbidities___13', 
       'morbidities___14', 'morbidities___15', 'morbidities___16', 'morbidities___17', 'morbidities___18', 
       'morbidities___19', 'morbidities___20', 'morbidities___21', 'health_condition', 'elder_visitors', 
       'physical_desabilities___1', 'physical_desabilities___2', 'physical_desabilities___3', 'weight_loss', 
       'amount_weight_loss', 'elder_strenght', 'elder_hospitalized', 'elder_difficulties', 'elder_mobility', 
       'basic_activities_diffic', 'falls_number']

df_corrigido[cols_to_convert] = df_corrigido[cols_to_convert].astype('Int64') 

# %%
## - Eliminado colunas que não são necessárias para a análise
cols_to_drop = ['redcap_survey_identifier', 'identificao_da_ilpi_f650_timestamp', 'institution_type', 
                'identificao_da_ilpi_f650_complete', 'dados_sciodemogrficos_timestamp', 'name', 'surname', 
                'admission_date', 'dados_sciodemogrficos_complete', 'medicamentos_em_uso_timestamp',
                'medicamentos_em_uso_complete', 'morbidades_prvias_timestamp', 'morbidities___nan',
                'morbidades_prvias_complete', 'estado_de_sade_timestamp', 'estado_de_sade_complete', 
                'componentes_de_fragilidade_timestamp', 'physical_desabilities___nan', 
                'componentes_de_fragilidade_complete', 'responsvel_pelo_preenchimento_timestamp', 
                'responsvel_pelo_preenchimento_complete']

df_filtered = df_corrigido.drop(columns=cols_to_drop)

# %%
## - Reordenando as colunas 
df_final = df_filtered[['record_id', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'visit_date', 
                        'latitude', 'longitude', 'institution_name', 'cpf', 'full_name', 'sex', 'date_of_birth', 
                        'elder_age', 'race', 'scholarship', 'institut_time_years', 'time_months', 'institut_time_months', 
                        'family_support', 'dependence_degree', 'link_type___1', 'link_type___2', 'link_type___3', 
                        'elder_income_source', 'med_name', 'dosage', 'recorded', 'combination_of_medicines', 
                        'combination_1', 'combination_dosage', 'combination_2', 'combination_dosage_2', 'combination_3', 
                        'combination_dosage_3', 'combination_4', 'combination_dosage_4', 'combination_5', 
                        'combination_dosage_5', 'combination_6', 'combination_dosage_6', 'taken_daily', 'morbidities___1', 
                        'morbidities___2', 'morbidities___3', 'morbidities___4', 'morbidities___5', 'morbidities___6', 
                        'morbidities___7', 'morbidities___8', 'morbidities___9', 'morbidities___10', 'morbidities___11', 
                        'morbidities___12', 'morbidities___13', 'morbidities___14', 'morbidities___15', 'morbidities___16', 
                        'morbidities___17', 'morbidities___18', 'morbidities___19', 'morbidities___20', 'morbidities___21', 
                        'other_morbidities', 'health_condition', 'elder_visitors', 'physical_desabilities___1', 'physical_desabilities___2', 
                        'physical_desabilities___3', 'weight_loss', 'amount_weight_loss', 'elder_strenght', 'elder_hospitalized', 
                        'elder_difficulties', 'elder_mobility', 'basic_activities_diffic', 'falls_number', 'interviewer_name']]
                        
df_final

# %%

df_final.to_csv("../../../data/SMSAp/base_perfil_epidemiologico.csv",
                   index=False,
                   sep=";")
# %%

#df_medicamentos = df[df['redcap_repeat_instrument'] == 'medicamentos_em_uso'].copy()

# %%




