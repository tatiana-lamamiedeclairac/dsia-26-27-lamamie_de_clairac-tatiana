"""
Crea un subconjunto manejable de Stravl para el proyecto CityBreak AI.

Necesita, en la misma carpeta:
    - Stravl_Travel_Preference_Data.csv
    - destination_ids.txt

Genera:
    - stravl_citybreak_subset.csv

Qué hace:
1. Lee los viajeros de Stravl.
2. Traduce los IDs de destino a "Ciudad, País".
3. Conserva únicamente destinos europeos.
4. Convierte las listas yes_swipes/no_swipes en una fila por interacción.
5. Elimina respuestas ambiguas (un mismo destino aparece en más de una lista).
6. Descarta "Maybe" para dejar un target binario limpio:
       liked = 1 -> Yes
       liked = 0 -> No
7. Mantiene solo usuarios con al menos 5 interacciones europeas.
8. Selecciona usuarios completos, con semilla fija, hasta obtener
   aproximadamente 12.000-15.000 interacciones.

La selección por usuario evita partir arbitrariamente el historial de una persona.
"""

from pathlib import Path
import ast

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------

TRAVELLERS_FILE = Path("Stravl_Travel_Preference_Data.csv")
DESTINATIONS_FILE = Path("destination_ids.txt")
OUTPUT_FILE = Path("stravl_citybreak_subset.csv")

MIN_ROWS = 12_000
MAX_ROWS = 15_000
MIN_INTERACTIONS_PER_USER = 5
RANDOM_SEED = 42


EUROPE_COUNTRIES = {
    "Albania",
    "Andorra",
    "Austria",
    "Belarus",
    "Belgium",
    "Bosnia and Herzegovina",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Iceland",
    "Ireland",
    "Italy",
    "Latvia",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Moldova",
    "Monaco",
    "Montenegro",
    "Netherlands",
    "Norway",
    "Poland",
    "Portugal",
    "Romania",
    "Russia",
    "San Marino",
    "Serbia",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "Switzerland",
    "Turkey",
    "Ukraine",
    "United Kingdom",
}


# Columnas de preferencias que conservamos del dataset original.
# No incluimos las columnas Model/Retrieval/DynaMatch/Rating_*/Rec_* porque
# corresponden a resultados/recomendaciones ya generadas y no queremos
# introducir información que pueda provocar data leakage en el futuro modelo.
PROFILE_COLUMNS = [
    "form_a",
    "form_b",
    "form_c",
    "form_f",
    "form_g",
    "form_h",
    "form_i",
    "form_j",
    "form_r",
    "form_rr",
]


# ---------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------

def parse_list(value):
    """Convierte una cadena como '[1, 2, 3]' o "['0', '2']" en una lista."""
    if pd.isna(value):
        return []

    try:
        parsed = ast.literal_eval(str(value))
    except (ValueError, SyntaxError):
        return []

    return parsed if isinstance(parsed, list) else []


def get_country(destination):
    """
    Extrae el país tomando el último elemento del texto del destino.

    Ejemplos:
        'Madrid, Spain' -> 'Spain'
        'Bath, England, United Kingdom' -> 'United Kingdom'
    """
    return destination.rsplit(",", 1)[-1].strip()


# ---------------------------------------------------------------------
# 1. CARGA DE DATOS
# ---------------------------------------------------------------------

travellers = pd.read_csv(TRAVELLERS_FILE)

destinations = [
    line.strip()
    for line in DESTINATIONS_FILE.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

print(f"Viajeros originales: {len(travellers):,}")
print(f"Destinos disponibles: {len(destinations):,}")


# ---------------------------------------------------------------------
# 2. IDENTIFICAR LOS DESTINOS EUROPEOS
# ---------------------------------------------------------------------

europe_destination_ids = {
    destination_id
    for destination_id, destination in enumerate(destinations)
    if get_country(destination) in EUROPE_COUNTRIES
}

print(f"Destinos europeos: {len(europe_destination_ids):,}")


# ---------------------------------------------------------------------
# 3. PASAR DE UNA FILA POR VIAJERO A UNA FILA POR INTERACCIÓN
# ---------------------------------------------------------------------

records = []

for _, row in travellers.iterrows():

    yes_ids = {int(x) for x in parse_list(row["yes_swipes"])}
    no_ids = {int(x) for x in parse_list(row["no_swipes"])}
    maybe_ids = {int(x) for x in parse_list(row["maybe_swipes"])}

    # Si el mismo destino aparece en dos respuestas distintas para un usuario,
    # no sabemos cuál considerar correcta. Lo eliminamos.
    ambiguous_ids = (
        (yes_ids & no_ids)
        | (yes_ids & maybe_ids)
        | (no_ids & maybe_ids)
    )

    yes_ids -= ambiguous_ids
    no_ids -= ambiguous_ids

    # Nos quedamos solo con destinos europeos.
    yes_ids &= europe_destination_ids
    no_ids &= europe_destination_ids

    # Información del perfil del viajero que repetiremos en cada interacción.
    user_profile = {
        "user_id": row["id"],
        **{column: row[column] for column in PROFILE_COLUMNS},
    }

    # Yes -> liked = 1
    for destination_id in yes_ids:
        destination = destinations[destination_id]

        records.append(
            {
                **user_profile,
                "destination_id": destination_id,
                "destination": destination,
                "country": get_country(destination),
                "swipe": "yes",
                "liked": 1,
            }
        )

    # No -> liked = 0
    for destination_id in no_ids:
        destination = destinations[destination_id]

        records.append(
            {
                **user_profile,
                "destination_id": destination_id,
                "destination": destination,
                "country": get_country(destination),
                "swipe": "no",
                "liked": 0,
            }
        )


interactions = pd.DataFrame(records)

print(f"Interacciones europeas Yes/No: {len(interactions):,}")


# ---------------------------------------------------------------------
# 4. QUEDARNOS CON USUARIOS QUE TENGAN HISTORIAL SUFICIENTE
# ---------------------------------------------------------------------

interactions_per_user = interactions.groupby("user_id").size()

eligible_users = interactions_per_user[
    interactions_per_user >= MIN_INTERACTIONS_PER_USER
].index.to_numpy()

print(
    "Usuarios con al menos "
    f"{MIN_INTERACTIONS_PER_USER} interacciones europeas: "
    f"{len(eligible_users):,}"
)


# ---------------------------------------------------------------------
# 5. CREAR UNA MUESTRA REPRODUCIBLE DE ~12K-15K FILAS
# ---------------------------------------------------------------------

rng = np.random.default_rng(RANDOM_SEED)
rng.shuffle(eligible_users)

selected_users = []
selected_rows = 0

for user_id in eligible_users:
    n_rows = int(interactions_per_user.loc[user_id])

    # Añadimos el usuario entero solo si no superamos MAX_ROWS.
    if selected_rows + n_rows <= MAX_ROWS:
        selected_users.append(user_id)
        selected_rows += n_rows

    if selected_rows >= MIN_ROWS:
        break


subset = interactions[
    interactions["user_id"].isin(selected_users)
].copy()

# Mezclamos las filas únicamente para que el CSV no quede ordenado por usuario.
# random_state hace que el resultado sea siempre reproducible.
subset = subset.sample(
    frac=1,
    random_state=RANDOM_SEED,
).reset_index(drop=True)


# ---------------------------------------------------------------------
# 6. ORDENAR COLUMNAS Y GUARDAR
# ---------------------------------------------------------------------

first_columns = [
    "user_id",
    "destination_id",
    "destination",
    "country",
    "swipe",
    "liked",
]

other_columns = [
    column
    for column in subset.columns
    if column not in first_columns
]

subset = subset[first_columns + other_columns]

subset.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8",
)


# ---------------------------------------------------------------------
# 7. RESUMEN FINAL
# ---------------------------------------------------------------------

print("\n--- DATASET FINAL ---")
print(f"Filas: {len(subset):,}")
print(f"Usuarios: {subset['user_id'].nunique():,}")
print(f"Destinos: {subset['destination_id'].nunique():,}")
print(f"Países: {subset['country'].nunique():,}")

print("\nDistribución del target:")
print(subset["swipe"].value_counts())

print(f"\nGuardado en: {OUTPUT_FILE.resolve()}")
