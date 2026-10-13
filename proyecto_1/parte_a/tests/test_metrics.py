import pandas as pd

from parte_a.ventas_app.metrics import calculate_amount, amount_by_product, amount_by_region, total_amount

# Comprueba que se calcula correctamente el importe de cada venta
def test_calculate_amount():
    df = pd.DataFrame({
        "unidades": [2, 3, 4],
        "precio_unitario": [10, 5, 20]
    })

    resultado = calculate_amount(df)

    assert resultado["importe"].tolist() == [20, 15, 80]

# Comprueba que se calcula correctamente el importe total
def test_total_amount():

    df = pd.DataFrame({
        "unidades": [2, 3, 4],
        "precio_unitario": [10, 5, 20]
    })

    resultado = total_amount(df)

    assert resultado == 115


# Comprueba que se calcula correctamente el importe por región
def test_amount_by_region():

    df = pd.DataFrame({
        "unidades": [2, 3, 4],
        "precio_unitario": [10, 5, 20],
        "region": ["Norte", "Sur", "Norte"]
    })

    resultado = amount_by_region(df)

    assert resultado["Norte"] == 100
    assert resultado["Sur"] == 15


# Comprueba que se calcula correctamente el importe por producto
def test_amount_by_product():

    df = pd.DataFrame({
        "unidades": [2, 3, 4],
        "precio_unitario": [10, 5, 20],
        "producto": ["A", "B", "A"]
    })

    resultado = amount_by_product(df)

    assert resultado["A"] == 100
    assert resultado["B"] == 15