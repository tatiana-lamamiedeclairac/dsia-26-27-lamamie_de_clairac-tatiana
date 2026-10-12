# MÉTRICAS:
# Importe total vendido
# Importe vendido por región
# Importe vendido por producto

# Importe = unidades x precio_unitario


import pandas as pd

# Añade a las ventas una columna con el importe de cada venta
def calculate_amount(df):
    sales = df.copy()

    # sales["unidades"] es una Serie de pandas en el que se encuentran
    # todos los valores de "unidades" en el df. Conceptualmente se puede
    # pensar en una Serie como una columna
    sales["unidades"] = pd.to_numeric(sales["unidades"])
    sales["precio_unitario"] = pd.to_numeric(sales["precio_unitario"])

    # Hace una multiplicación fila por fila para todas las filas del DataFrame
    importe = sales["unidades"] * sales["precio_unitario"]

    # sales["importe"] es una Serie con todos los valores de importe
    # que hay en el dataframe
    # Si hacemos sales["importe"] pero en en el df sales no había ninguna 
    # columna llamada importe, la crea, que es lo que hace aquí. 
    sales["importe"] = importe

    return sales

# Calcula el importe total de todas las ventas
def total_amount(df):
    sales= calculate_amount(df)
    total = sales["importe"].sum()

    return total

# Calcula el importe total vendido en cada región
def amount_by_region(df):
    sales = calculate_amount(df)
    result = sales.groupby("region")["importe"].sum()
    
    return result

# Calcula el importe total vendido de cada producto
def amount_by_product(df):
    sales = calculate_amount(df)
    result = sales.groupby("producto")["importe"].sum()

    return result