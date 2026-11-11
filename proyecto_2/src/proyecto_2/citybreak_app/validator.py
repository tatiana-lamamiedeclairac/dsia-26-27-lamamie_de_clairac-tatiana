# Columna           Regla de validación

# user_id           No puede ser nulo ni estar vacío
# destination_id    Debe ser un número entero mayor o igual que 0
# destination       No puede ser nulo ni estar vacío
# country           No puede ser nulo ni estar vacío
# swipe             Solo puede ser "yes" o "no"
# liked             Solo puede ser 0 o 1

# Además, hay que comprobar que swipe y liked sean coherentes:
# Si swipe es "yes", liked debe ser 1, y si swipe es "no", liked debe ser 0

import pandas as pd

# Comprueba si una valoración de un destino es válida
def is_valid_swipe(row):
    # Comprobar que no haya valores nulos
    if pd.isna(row["user_id"]):
        return False

    if pd.isna(row["destination"]):
        return False

    if pd.isna(row["country"]):
        return False

    # Comprobar que los textos no estén vacíos
    if str(row["user_id"]).strip() == "":
        return False

    if str(row["destination"]).strip() == "":
        return False

    if str(row["country"]).strip() == "":
        return False

    # Comprobar que destination_id sea un int >= 0
    try:
        destination_id = int(row["destination_id"])
    except (ValueError, TypeError):
        return False

    if pd.isna(row["destination_id"]):
        return False

    if destination_id < 0:
        return False

    # Comprobar que swipe sea yes o no
    if row["swipe"] not in ["yes", "no"]:
        return False

    # Comprobar que liked sea 0 o 1
    if row["liked"] not in [0, 1]:
        return False

    # Comprobar que swipe y liked sean coherentes
    if row["swipe"] == "yes" and row["liked"] != 1:
        return False

    if row["swipe"] == "no" and row["liked"] != 0:
        return False

    return True


# Separar las valoraciones válidas de las inválidas
def validate_swipes(df):
    valid_rows = []
    invalid_rows = []

    for i, row in df.iterrows():
        if is_valid_swipe(row):
            valid_rows.append(row)

        else:
            invalid_rows.append(row)

    valid_swipes = pd.DataFrame(valid_rows)
    invalid_swipes = pd.DataFrame(invalid_rows)

    return valid_swipes, invalid_swipes