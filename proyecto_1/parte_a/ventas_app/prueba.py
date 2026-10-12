from parte_a.ventas_app.loader import load_sales
from parte_a.ventas_app.validator import is_valid_sale

df = load_sales("parte_a/data/ventas.csv")

print(df.iloc[0])
print(is_valid_sale(df.iloc[0]))