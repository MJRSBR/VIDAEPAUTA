# Copilot Instructions for VIDAEPAUTA

## Project Overview
- VIDAEPAUTA analyzes the socioeconomic and demographic profile of the elderly population (65+) in Aparecida de Goiânia, GO, supporting public policy research.
- Main data sources are CSV files in `data/` (subfolders: `SMSAp`, `UFG`).
- Core analysis logic is in the `analise_ilpi/` package and `surveys/SMSAp/src/analise_perfil_epidemio.py`.

## Architecture & Data Flow
- Data is loaded from CSVs (see `data/SMSAp/base_perfil_epidemiologico.csv`, `data/UFG/base_ilpi.csv`).
- Analysis scripts (e.g., `surveys/SMSAp/src/analise_perfil_epidemio.py`, `code_source.py`) process data and generate tables/plots in `surveys/SMSAp/plots/` and `tables/`.
- The `analise_ilpi/core.py` module provides reusable functions for binary/multi-column analysis and visualization.
- Most scripts use pandas, matplotlib, seaborn for data manipulation and plotting.

## Key Patterns & Conventions
- All plots and tables are saved to relative paths (`../plots`, `../tables`). Use `criar_diretorios()` to ensure these exist.
- Dataframes are often wrapped for display using `textwrap` for column formatting (see `salvar_tabela_como_imagem`).
- Graphs include a red annotation: "* Uma das instituições é composta por unidades de moradia".
- Functions for analysis and plotting are defined in `analise_ilpi/core.py` and imported in scripts via `from analise_ilpi import ...`.
- Scripts are organized by survey/source: `surveys/SMSAp/src/`, `surveys/UFG/`.

## Developer Workflow
- Install dependencies: `pip install -e .` (from project root; see `setup.py`).
- Run analysis scripts directly (e.g., `python surveys/SMSAp/src/analise_perfil_epidemio.py`).
- No test suite or CI/CD pipeline is present; manual script execution is standard.
- For new analyses, copy patterns from `analise_perfil_epidemio.py` or `code_source.py`.

## External Dependencies
- pandas, matplotlib, seaborn (see `setup.py`).
- Data files must be present in the expected locations; paths are relative and not robust to missing files.

## Examples
- To generate a binary column plot: use `gerar_grafico_binario(df, coluna, nome_final, titulo, nome_arquivo)` from `analise_ilpi/core.py`.
- To save a formatted table as PNG: use `salvar_tabela_como_imagem(df, caminho_arquivo, titulo)` from `analise_perfil_epidemio.py`.

## Recommendations for AI Agents
- Always check/create output directories before saving files.
- Follow the existing function signatures and output formats for consistency.
- When adding new analysis, mimic the structure and style of existing scripts.
- Document new functions inline with docstrings and comments, as seen in current codebase.

---

If any section is unclear or missing, please provide feedback for further refinement.
