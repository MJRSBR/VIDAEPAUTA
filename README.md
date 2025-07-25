# Projeto VIDAEPAUTA
 
## Objeto de pesquisa

Este projeto tem como finalidade além fazer um levantamento do perfil sócioeconômico e demográfico da população idosa (65+)
do município de Aparecida de Goiânia - GO, buscar elementos e achados que possam subsidiar políticas públicas.

# analise_ilpi

Este pacote contém funções para analisar dados de Instituições de Longa Permanência para Idosos (ILPIs), com geração automática de gráficos e processamento de colunas binárias e múltiplas.

## Visão Geral do Projeto
- O VIDAEPAUTA analisa o perfil socioeconômico e demográfico da população idosa (65+) em Aparecida de Goiânia, GO, subsidiando pesquisas em políticas públicas.
- As principais fontes de dados são arquivos CSV em `data/` (subpastas: `SMSAp`, `UFG`).
- A lógica central da análise está no pacote `analise_ilpi/` e em `surveys/SMSAp/src/analise_perfil_epidemio.py`.

## Arquitetura e Fluxo de Dados
- Os dados são carregados de CSVs (consulte `data/SMSAp/base_perfil_epidemiologico.csv`, `data/UFG/base_ilpi.csv`).
- Scripts de análise (por exemplo, `surveys/SMSAp/src/analise_perfil_epidemio.py`, `code_source.py`) processam dados e geram tabelas/gráficos em `surveys/SMSAp/plots/` e `tables/`.
- O módulo `analise_ilpi/core.py` fornece funções reutilizáveis para análise e visualização binária/multicoluna.
- A maioria dos scripts utiliza pandas, matplotlib e seaborn para manipulação e plotagem de dados.

## Principais Padrões e Convenções
- Todos os gráficos e tabelas são salvos em caminhos relativos (`../plots`, `../tables`). Use `criar_diretorios()` para garantir que eles existam.
- Os dataframes são frequentemente encapsulados para exibição usando `textwrap` para formatação de colunas (consulte `salvar_tabela_como_imagem`).
- Os gráficos incluem uma anotação em vermelho: "* Uma das instituições é composta por unidades de moradia".
- As funções para análise e plotagem são definidas em `analise_ilpi/core.py` e importadas em scripts via `from analise_ilpi import ...`.
- Os scripts são organizados por pesquisa/fonte: `surveys/SMSAp/src/`, `surveys/UFG/`.

## Fluxo de Trabalho do Desenvolvedor
- Instalar dependências: `pip install -e .` (da raiz do projeto; consulte `setup.py`).
- Executar scripts de análise diretamente (por exemplo, `python surveys/SMSAp/src/analise_perfil_epidemio.py`).
- Não há suíte de testes ou pipeline de CI/CD presente; a execução manual de scripts é padrão.
- Para novas análises, copie os padrões de `analise_perfil_epidemio.py` ou `code_source.py`.

## Dependências Externas
- pandas, matplotlib, seaborn (consulte `setup.py`).
- Os arquivos de dados devem estar presentes nos locais esperados; os caminhos são relativos e não são robustos a arquivos ausentes.

## Exemplos
- Para gerar um gráfico de colunas binárias: use `gerar_grafico_binario(df, coluna, nome_final, titulo, nome_arquivo)` de `analise_ilpi/core.py`.
- Para salvar uma tabela formatada como PNG: use `salvar_tabela_como_imagem(df, caminho_arquivo, titulo)` de `analise_perfil_epidemio.py`.