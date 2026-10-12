# unidades -> debe ser numérico, no nulo y > 0
# precio_unitario -> debe ser numérico, no nulo y > 0

import pandas as pd

# Comprueba si una venta es válida
import pandas as pd


def is_valid_sale(row):
    """Comprueba si una venta es válida."""

    try:
        unidades = float(row["unidades"])
        precio = float(row["precio_unitario"])

    except (ValueError, TypeError):
        return False

    if pd.isna(unidades) or pd.isna(precio):
        return False

    if unidades <= 0:
        return False

    if precio <= 0:
        return False

    return True

# Separa las ventas válidas de las inválidas
def validate_sales(df):
    valid_rows = []
    invalid_rows = []

    for _, row in df.iterrows():
        if is_valid_sale(row):
            valid_rows.append(row)
        else:
            invalid_rows.append(row)

    valid_sales = pd.DataFrame(valid_rows)
    invalid_sales = pd.DataFrame(invalid_rows)

    return valid_sales, invalid_sales