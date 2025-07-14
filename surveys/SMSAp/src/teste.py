# %%
import matplotlib.pyplot as plt
import pandas as pd
#from fpdf import FPDF
import io

# Dados para o gráfico de comparação de índices
#anos = ['2021', '2022', '2023', '2024', '2025']
#fipezap = [7.5, 15.1, 18.0, 13.5, 12.5]
#ipca = [10.1, 5.8, 4.5, 4.8, 4.0]
#igpm = [-10.7, -7.7, 2.4, 3.9, 4.0]
#
## Gráfico 1: FipeZap vs IPCA vs IGP-M
#plt.figure(figsize=(8, 5))
#plt.plot(anos, fipezap, marker='o', label='FipeZap (Aluguel)')
#plt.plot(anos, ipca, marker='o', label='IPCA')
#plt.plot(anos, igpm, marker='o', label='IGP-M')
#plt.title('Variação Anual (%) - Aluguel x Inflação (2021–2025)')
#plt.ylabel('% de Variação')
#plt.grid(True)
#plt.legend('')
#plt.tight_layout()
#plt.savefig("grafico_indice.png")
#plt.close()


# Dados de variação anual
anos = ['2021', '2022', '2023', '2024', '2025*']
fipezap = [7.5, 15.1, 18.0, 13.5, 12.5]
ipca = [10.1, 5.8, 4.5, 4.8, 4.0]
igpm = [-10.7, -7.7, 2.4, 3.9, 4.0]

# Criar gráfico
plt.figure(figsize=(10, 6))
plt.plot(anos, fipezap, marker='o', label='FipeZap (Aluguel)', color='blue')
plt.plot(anos, ipca, marker='o', label='IPCA', color='green')
plt.plot(anos, igpm, marker='o', label='IGP-M', color='red')

# Adicionar rótulos nos pontos
for i in range(len(anos)):
    plt.text(anos[i], fipezap[i] + 0.8, f'{fipezap[i]:.1f}%', ha='center', color='blue', fontsize=9)
    plt.text(anos[i], ipca[i] + 0.8, f'{ipca[i]:.1f}%', ha='center', color='green', fontsize=9)
    plt.text(anos[i], igpm[i] + 0.8, f'{igpm[i]:.1f}%', ha='center', color='red', fontsize=9)

# Estilização
plt.title('Variação Anual (%) – Aluguel (FipeZap) vs Inflação (IPCA e IGP-M)', fontsize=14)
plt.ylabel('% de Variação')
plt.xlabel('Ano')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()

# Fontes no rodapé
plt.figtext(0.5, 0.01, "Fontes: FipeZap, IBGE (IPCA), FGV (IGP-M) – 2021 a 2025",
            wrap=True, horizontalalignment='center', fontsize=9, color='gray')

# Salvar imagem
plt.savefig("grafico_variacao_anual_indices_legenda.png")
plt.show()


# Dados de aluguel por m² em Goiânia (bairros nobres)
bairros = ['Marista', 'Jardim Goiás', 'Bueno', 'Oeste']
precos = [53.7, 50.7, 40.2, 32.3]

# Criar gráfico
plt.figure(figsize=(10, 6))
bars = plt.bar(bairros, precos, color=['gold', 'green', 'orange', 'blue'])

# Título e eixos
plt.title('Preço médio do aluguel por m² (dez/2024 – mai/2025) – Goiânia', fontsize=14)
plt.ylabel('R$/m²')

# Rótulos nas barras
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f'R$ {yval:.2f}', ha='center', va='bottom', fontsize=10)

# Adicionar fontes no rodapé do gráfico
fontes = ("Fonte: InfoMoney")
plt.figtext(0.5, 0.01, fontes, wrap=True, horizontalalignment='center', fontsize=9, color='gray')

# Salvar como imagem
plt.tight_layout()
plt.savefig("grafico_setores_gyn_fontes.png")
plt.show()


#bairros = ['Marista', 'Jardim Goiás', 'Bueno', 'Oeste']
#precos = [53.7, 50.7, 40.2, 32.3]
#
#plt.figure(figsize=(8,5))
#plt.bar(bairros, precos, color=['gold','green','orange','blue'])
#plt.title('Preço médio do aluguel por m² (dez/2024‑mai/2025)')
#plt.ylabel('R$/m²')
#plt.tight_layout()
#plt.savefig("grafico_setores_gyn.png")
#plt.close()


# Criar o PDF
#pdf = FPDF()
#pdf.add_page()
#pdf.set_font("Arial", 'B', 14)
#pdf.cell(0, 10, "Dados Comparativos de Mercado para Reajuste de Aluguel", ln=True, align='C')
#
#pdf.ln(10)
#pdf.set_font("Arial", 'B', 12)
#pdf.cell(0, 10, "1. Variação Anual - Aluguel (FipeZap) x IPCA x IGP-M", ln=True)
#pdf.image("grafico_indice.png", x=10, w=180)
#
#pdf.ln(10)
#pdf.set_font("Arial", 'B', 12)
#pdf.cell(0, 10, "2. Preço médio do aluguel por m² em capitais (dez/2024)", ln=True)
#pdf.image("grafico_m2.png", x=10, w=180)
#
#pdf.output("comparativo_reajuste_aluguel_mercado.pdf")

# %%
