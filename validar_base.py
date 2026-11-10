from pathlib import Path
import pandas as pd

arquivo = Path(__file__).parent / "dados" / "Financial Sample.xlsx"
vendas = pd.read_excel(arquivo)
vendas.columns = vendas.columns.str.strip()

print(f"Linhas lidas: {len(vendas)}")
print(f"Vendas totais: {vendas['Sales'].sum():,.2f}")
print(f"Lucro total: {vendas['Profit'].sum():,.2f}")