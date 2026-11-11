import ast
import pandas as pd


# Columnas correspondientes al cuestionario
FORM_COLUMNS = [
    "form_a",
    "form_b",
    "form_c",
    "form_f",
    "form_g",
    "form_h",
    "form_i",
    "form_j",
    "form_r",
    "form_rr"
]


def parse_form(value):
    """
    Convierte las respuestas del cuestionario
    de texto a listas de Python.
    """

    # Si no hay respuesta, devolver una lista vacía
    if pd.isna(value):
        return []

    try:
        result = ast.literal_eval(value)

    except (ValueError, SyntaxError) as e:
        raise ValueError(
            f"Formato de respuesta no válido: {value}"
        ) from e

    if not isinstance(result, list):
        raise ValueError(
            f"Se esperaba una lista: {value}"
        )

    return [str(option) for option in result]


def preprocess_forms(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma las respuestas del cuestionario
    en listas de Python.
    """

    df = df.copy()

    for col in FORM_COLUMNS:
        df[col] = df[col].apply(parse_form)

    return df

# Opciones que aparecen en cada pregunta del cuestionario
FORM_OPTIONS = {
    "form_a": ["0", "1", "2", "3"],
    "form_b": ["0", "1", "2", "3"],
    "form_c": ["0", "1", "2", "3"],
    "form_f": [str(i) for i in range(8)],
    "form_g": [str(i) for i in range(8)],
    "form_h": ["0", "1", "2"],
    "form_i": ["0", "1", "2"],
    "form_j": ["0", "1", "2"],
    "form_r": ["0", "1"],
    "form_rr": ["a", "c", "e", "f", "m", "n", "o", "s"]
}

def encode_forms(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte las respuestas del cuestionario en columnas
    numéricas mediante Multi-Hot Encoding.
    """

    df = df.copy()

    for col, options in FORM_OPTIONS.items():

        # Comprobar que existe la columna
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col}")

        # Comprobar que las respuestas sean listas
        if not df[col].apply(lambda x: isinstance(x, list)).all():
            raise ValueError(
                f"La columna {col} debe contener listas."
            )

        # Comprobar que las opciones sean conocidas
        unknown = {
            option
            for answers in df[col]
            for option in answers
            if option not in options
        }

        if unknown:
            raise ValueError(
                f"Opciones desconocidas en {col}: {unknown}"
            )

        # Crear una columna binaria por cada opción
        for option in options:
            new_col = f"{col}_{option}"

            df[new_col] = df[col].apply(
                lambda answers: int(option in answers)
            )

        # Indicar cuándo falta una respuesta
        df[f"{col}_missing"] = df[col].apply(
            lambda answers: int(len(answers) == 0)
        )

    # Eliminar las columnas originales con listas
    df = df.drop(columns=list(FORM_OPTIONS.keys()))

    return df

