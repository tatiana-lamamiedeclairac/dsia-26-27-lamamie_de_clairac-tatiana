import pandas as pd
from pathlib import Path
from parte_b.citybreak_app.exceptions import DataLoadError

# Cargar el archivo CSV de destinos turísticos y devolver un dataframe
def load_citybreaks(path: str | Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)

    except FileNotFoundError as e:
        raise DataLoadError(f"Error {e}. No se ha encontrado el archivo. ")

    except pd.errors.EmptyDataError as e:
        raise DataLoadError(f"Error {e}. El archivo está vacío. ")

    except pd.errors.ParserError as e:
        raise DataLoadError(f"Error {e}. El archivo CSV no tiene un formato válido. ")

    return df