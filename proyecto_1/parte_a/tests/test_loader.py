import pandas as pd
import pytest

from parte_a.ventas_app.loader import load_sales
from parte_a.ventas_app.exceptions import DataLoadError

# pytest reconocce auntomáticamente las funciones que empiezan 
# por test_
# Comprueba que el csv se carga correctamente
def test_load_sales():
    df = load_sales("parte_a/data/ventas.csv")

    # isinstance(df, pd.DataFrame) comprueba si df es un objeto
    # de tipo DataFrame
    # assert comprueba que la condición sea verdadera
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 150 # Comprueba que el df tenga exactamente 150 filas


# Comprueba que se lanza un error si el archivo no existe
def test_load_sales_file_not_found():
    with pytest.raises(DataLoadError):
        load_sales("archivo_inexistente.csv") # Como este archivo no existe, nuestra función debería lanzar una excepción

# pytest.raises() sirve para comprobar que una parte de nuestro
# código lanza una excepción determinada. En este caso, significa:
# voy a ejecutar load_sales() y espero que lance una excepción
# de tipo DataLoadError. Si la lanza, el test para. Si no la lanza,
# el test falla. 