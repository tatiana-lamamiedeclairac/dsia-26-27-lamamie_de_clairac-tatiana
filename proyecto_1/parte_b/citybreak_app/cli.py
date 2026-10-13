import argparse

from parte_b.citybreak_app.loader import load_citybreaks
from parte_b.citybreak_app.validator import validate_swipes
from parte_b.citybreak_app.metrics import (
    total_likes,
    likes_by_country,
    likes_by_destination
)


def main():
    # Crear el objeto para interpretar los argumentos de la terminal
    parser = argparse.ArgumentParser(
        description="Analiza un archivo CSV de destinos turísticos"
    )

    # Indicar que el usuario debe proporcionar la ruta del CSV
    parser.add_argument(
        "--input",
        required=True,
        help="Ruta al archivo CSV de destinos turísticos"
    )

    # Leer los argumentos de la terminal
    args = parser.parse_args()

    df = load_citybreaks(args.input)

    valid_swipes, invalid_swipes = validate_swipes(df)

    print(f"Valoraciones válidas: {len(valid_swipes)}")
    print(f"Valoraciones inválidas: {len(invalid_swipes)}")


    print("\nTotal de likes:")
    print(total_likes(valid_swipes))

    print("\nLikes por país:")
    print(likes_by_country(valid_swipes))

    print("\nLikes por destino:")
    print(likes_by_destination(valid_swipes))


if __name__ == "__main__":
    main()