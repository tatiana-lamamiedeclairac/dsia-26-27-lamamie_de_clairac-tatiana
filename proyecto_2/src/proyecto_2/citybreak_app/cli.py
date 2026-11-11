
import argparse
import logging
from pathlib import Path

from .loader import DATA_PATH
from .train import main as train_main, MODEL_PATH
from .predict import main as predict_main
from .exceptions import DataLoadError


logger = logging.getLogger(__name__)


def add_recommend_arguments(parser, default_provider="none"):
    """
    Añade los argumentos necesarios para generar
    recomendaciones.
    """

    parser.add_argument(
        "--input",
        type=Path,
        default=DATA_PATH,
        help="Ruta del dataset"
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
        help="Fila utilizada como perfil de prueba"
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
        default=default_provider,
        help="Proveedor de IA generativa"
    )


def main():
    """
    Punto de entrada de CityBreak App.

    Permite ejecutar entrenamiento, inferencia
    o el pipeline completo.
    """

    parser = argparse.ArgumentParser(
        description="CityBreak App - Pipeline de recomendación"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # Comando de entrenamiento
    train_parser = subparsers.add_parser(
        "train",
        help="Entrenar y guardar el modelo"
    )

    train_parser.add_argument(
        "--input",
        type=Path,
        default=DATA_PATH
    )

    train_parser.add_argument(
        "--output",
        type=Path,
        default=MODEL_PATH
    )

    # Comando de recomendaciones
    recommend_parser = subparsers.add_parser(
        "recommend",
        help="Generar recomendaciones con el modelo guardado"
    )

    add_recommend_arguments(recommend_parser)

    # Comando del pipeline completo
    pipeline_parser = subparsers.add_parser(
        "pipeline",
        help="Ejecutar entrenamiento, predicción e IA"
    )

    add_recommend_arguments(
        pipeline_parser,
        default_provider="mock"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s"
    )

    logger.info("CityBreak App - Comando: %s", args.command)

    try:

        # Entrenar el modelo
        if args.command == "train":

            train_main([
                "--input", str(args.input),
                "--output", str(args.output)
            ])

        else:

            # Ejecutar entrenamiento si se pide pipeline
            if args.command == "pipeline":

                logger.info("Iniciando pipeline completo")

                train_main([
                    "--input", str(args.input),
                    "--output", str(args.model)
                ])

            # Generar las recomendaciones
            predict_main([
                "--input", str(args.input),
                "--model", str(args.model),
                "--profile-row", str(args.profile_row),
                "--top-k", str(args.top_k),
                "--ai-provider", args.ai_provider
            ])

        logger.info("Ejecución finalizada correctamente")

    except (DataLoadError, FileNotFoundError, ValueError) as e:

        logger.error(
            "Error durante la ejecución: %s",
            e
        )

        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
