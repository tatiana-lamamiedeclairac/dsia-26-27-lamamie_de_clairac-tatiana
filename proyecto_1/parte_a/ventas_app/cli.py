import argparse # Sirve para leer argumentos desde la terminal

from parte_a.ventas_app.loader import load_sales
from parte_a.ventas_app.validator import validate_sales
from parte_a.ventas_app.metrics import (
    total_amount,
    amount_by_product,
    amount_by_region
)

def main():
    # crear un objeto que va a interpretar lo que escribamos
    # en la terminal
    parser = argparse.ArgumentParser(
        description="Analiza un archivo CSV de ventas"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Ruta al archivo CSV de ventas. "
    )

    # Esta línea analiza lo que se ha escrito en la terminal
    args = parser.parse_args()

    # Si se ejecuta: uv run python -m parte_a.ventas_app.cli --input parte_a/data/ventas.csv
    # entonces args.input contendrá: parte_a/data/ventas.csv
    # args.input es la ruta que el usuario ha escrito
    df = load_sales(args.input)

    valid_sales, invalid_sales = validate_sales(df)

    print(f"Ventas válidas: {len(valid_sales)}")
    print(f"Ventas inválidas: {len(invalid_sales)}")

    print("\nImporte total:")
    print(total_amount(valid_sales))

    print("\nImporte por región:")
    print(amount_by_region(valid_sales))

    print("\nImporte por producto:")
    print(amount_by_product(valid_sales))

if __name__ == "__main__":
    main()