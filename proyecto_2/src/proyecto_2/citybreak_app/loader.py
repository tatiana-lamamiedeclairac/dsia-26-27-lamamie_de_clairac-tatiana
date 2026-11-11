from pathlib import Path
import pandas as pd

from .exceptions import DataLoadError


# Localizar la raíz del repositorio
REPO_ROOT = Path(__file__).resolve().parents[4]

# Ruta del dataset del Proyecto I
DATA_PATH = (
    REPO_ROOT
    / "proyecto_1"
    / "parte_b"
    / "data"
    / "stravl_citybreak_subset.csv"
)


def load_citybreaks(path: str | Path = DATA_PATH) -> pd.DataFrame:
    """
    Carga el CSV de destinos turísticos y devuelve un DataFrame.
    """

    try:
        df = pd.read_csv(path)

    except FileNotFoundError as e:
        raise DataLoadError(
            f"No se ha encontrado el archivo: {path}"
        ) from e

    except pd.errors.EmptyDataError as e:
        raise DataLoadError(
            f"El archivo está vacío: {path}"
        ) from e

    except pd.errors.ParserError as e:
        raise DataLoadError(
            f"El archivo CSV no tiene un formato válido: {path}"
        ) from e

    return df