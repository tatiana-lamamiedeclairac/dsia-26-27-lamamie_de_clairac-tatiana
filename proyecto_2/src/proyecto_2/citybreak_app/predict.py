
import argparse
import logging
from pathlib import Path

import joblib
import pandas as pd

from .genai_client import generate_explanation, AIServiceError
from .loader import load_citybreaks, DATA_PATH
from .validator import validate_swipes
from .preprocessing import (
    FORM_COLUMNS,
    preprocess_forms,
    encode_forms
)
from .features import build_predictors
from .train import MODEL_PATH


logger = logging.getLogger(__name__)


def load_model(path: str | Path = MODEL_PATH):
    """
    Carga un modelo de Machine Learning ya entrenado.
    """

    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(
            f"No se ha encontrado el modelo: {path}"
        )

    return joblib.load(path)


def recommend_destinations(
    model,
    preferences: dict,
    destinations: pd.DataFrame,
    top_k: int = 5
) -> pd.DataFrame:
    """
    Recomienda los destinos con mayor probabilidad
    de gustar a un usuario según sus preferencias.
    """

    if top_k < 1:
        raise ValueError("top_k debe ser mayor que cero")

    # Comprobar que tenemos todas las respuestas
    missing_columns = [
        col for col in FORM_COLUMNS
        if col not in preferences
    ]

    if missing_columns:
        raise ValueError(
            f"Faltan respuestas: {missing_columns}"
        )

    # Construir el catálogo de destinos sin duplicados
    candidates = destinations[
        ["destination_id", "destination", "country"]
    ].drop_duplicates(
        subset="destination_id"
    ).copy()

    if candidates.empty:
        raise ValueError("No hay destinos disponibles")

    # Combinar las preferencias con cada destino
    for col in FORM_COLUMNS:

        value = preferences[col]

        # Convertir listas al formato esperado
        # por preprocess_forms()
        if isinstance(value, list):
            value = repr([str(option) for option in value])

        candidates[col] = value

    # Aplicar el mismo procesamiento que en entrenamiento
    processed = preprocess_forms(candidates)
    processed = encode_forms(processed)

    X = build_predictors(processed)

    # Calcular la probabilidad estimada de like
    probabilities = model.predict_proba(X)[:, 1]

    candidates["probability"] = probabilities

    # Seleccionar las mejores recomendaciones
    recommendations = candidates.nlargest(
        top_k,
        "probability"
    )

    return recommendations[
        ["destination", "country", "probability"]
    ].reset_index(drop=True)



def main(argv=None):
    """
    Genera recomendaciones utilizando las preferencias
    de un usuario del dataset y, opcionalmente,
    una explicación mediante IA generativa.
    """

    parser = argparse.ArgumentParser(
        description="Recomendar destinos con CityBreak App"
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DATA_PATH,
        help="Ruta del CSV de Stravl"
    )

    parser.add_argument(
        "--model",
        type=Path,
        default=MODEL_PATH,
        help="Ruta del modelo entrenado"
    )

    parser.add_argument(
        "--profile-row",
        type=int,
        default=0,
        help="Fila del dataset utilizada como perfil de prueba"
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Número de destinos recomendados"
    )

    parser.add_argument(
        "--ai-provider",
        choices=["none", "mock", "nvidia"],
        default="none",
        help="Proveedor de IA para explicar las recomendaciones"
    )

    args = parser.parse_args(argv)

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s"
    )

    # 1. Cargar los datos
    df = load_citybreaks(args.input)

    # 2. Validar los registros
    valid, invalid = validate_swipes(df)

    logger.info(
        "Registros validos: %d | invalidos: %d",
        len(valid),
        len(invalid)
    )

    if valid.empty:
        raise ValueError("No hay registros validos")

    # 3. Obtener un perfil de ejemplo
    if not 0 <= args.profile_row < len(valid):
        parser.error("La fila de perfil indicada no existe")

    profile = valid.iloc[args.profile_row]

    preferences = {
        col: profile[col]
        for col in FORM_COLUMNS
    }

    # 4. Cargar el modelo entrenado
    model = load_model(args.model)

    # 5. Generar las recomendaciones
    recommendations = recommend_destinations(
        model=model,
        preferences=preferences,
        destinations=valid,
        top_k=args.top_k
    )

    # 6. Mostrar las ciudades recomendadas
    print("\nCITYBREAK APP - TOP DESTINOS\n")

    for position, row in enumerate(
        recommendations.itertuples(index=False),
        start=1
    ):
        print(
            f"{position}. {row.destination} "
            f"- {row.probability:.2%}"
        )

    # 7. Generar una explicación mediante IA generativa
    if args.ai_provider != "none":

        destinations = recommendations["destination"].tolist()

        try:
            explanation = generate_explanation(
                destinations=destinations,
                provider=args.ai_provider
            )

            print("\nEXPLICACION GENERADA POR IA\n")
            print(explanation)

        except AIServiceError as e:
            logger.error(
                "No se ha podido generar la explicación: %s",
                e
            )

            print(
                "\nLas recomendaciones están disponibles, "
                "pero no se ha podido generar la explicación."
            )


if __name__ == "__main__":
    main()
