from pathlib import Path
import pandas as pd
from parte_a.ventas_app.exceptions import DataLoadError


# Carga un archivo CSV de ventas y devuelve un DataFrame
def load_sales(path: str | Path) -> pd.DataFrame: # Esperamos que path sea un string o un Path
    try:
        df = pd.read_csv(path)

    except FileNotFoundError as e:
        raise DataLoadError(f"Error {e}. No se ha encontrado el archivo.")

    except pd.errors.EmptyDataError as e:
        raise DataLoadError(f"Error {e}. El archivo está vacío. ")

    except pd.errors.ParserError as e:
        raise DataLoadError(f"Error {e}. El archivo CSV no tiene un formato válido. ")

    return df