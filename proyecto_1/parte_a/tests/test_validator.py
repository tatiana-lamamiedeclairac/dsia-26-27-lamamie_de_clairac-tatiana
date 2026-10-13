# - Una función puede tener varios tests, porque queremos comprobar
# cómo se comporta en distintas situaciones.
# - No es obligatorio hacer un test por cada función, pero sí que es
# buena práctica comprobar todas las funciones importantes del programa

from parte_a.ventas_app.validator import is_valid_sale, validate_sales

import pytest
import pandas as pd

# Comprueba que una venta correcta se considera válida
def test_valid_sale():
    venta = {
        "unidades": 5,
        "precio_unitario": 10
    }

    resultado = is_valid_sale(venta)

    assert resultado == True

# Para comprobar diferentes casos de ventas inválidas
# parametrize espera dos argumentos: el primer alrgumento son los 
# nombre de las variables que queremos utilizar, juntos en una cadena de texto.
# El segundo argumento es la lista de combinaciones de valores que queremos probar
@pytest.mark.parametrize("unidades, precio", [
    (0,10),
    (-5, 10),
    (5, 0),
    (5, -10),
    (None, 10),
    (5, None),
    ("hola", 10),
    (5, "hola")
])

# Los parámetros unidades y precio reciben auntomáticamente los valores
# que hemos definido en parametrize. Pytest ejecuta la función tantas veces 
# como elementos haya en parametrize
# No tenemos que llamar a la función 8 veces, pytest lo hace automáticamente.
def test_invalid_sale(unidades, precio):
    venta = {
        "unidades": unidades, 
        "precio_unitario": precio
    }

    resultado = is_valid_sale(venta)

    assert resultado == False

def test_validate_sales():
    df = pd.DataFrame({
        "unidades": [5, 0, 3, -2],
        "precio_unitario": [10, 20, 0, 15]
    })

    valid_sales, invalid_sales = validate_sales(df)

    assert len(valid_sales) == 1
    assert len(invalid_sales) == 3