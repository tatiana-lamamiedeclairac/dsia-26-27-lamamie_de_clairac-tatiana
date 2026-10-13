import pandas as pd
import pytest

from parte_b.citybreak_app.validator import (
    is_valid_swipe,
    validate_swipes
)


# Comprobar que una valoración correcta se considera válida
def test_valid_swipe():

    valoracion = {
        "user_id": "user_1",
        "destination_id": 5,
        "destination": "Barcelona",
        "country": "Spain",
        "swipe": "yes",
        "liked": 1
    }

    resultado = is_valid_swipe(valoracion)

    assert resultado == True


# Comprobar diferentes casos de valoraciones inválidas
@pytest.mark.parametrize("user_id, destination_id, destination, country, swipe, liked", [
    (None, 5, "Barcelona", "Spain", "yes", 1),
    ("user_1", -1, "Barcelona", "Spain", "yes", 1),
    ("user_1", 5, None, "Spain", "yes", 1),
    ("user_1", 5, "Barcelona", None, "yes", 1),
    ("user_1", 5, "Barcelona", "Spain", "maybe", 1),
    ("user_1", 5, "Barcelona", "Spain", "yes", 2),
    ("user_1", 5, "Barcelona", "Spain", "yes", 0),
    ("user_1", 5, "Barcelona", "Spain", "no", 1)
])
def test_invalid_swipe(user_id, destination_id, destination, country, swipe, liked):

    valoracion = {
        "user_id": user_id,
        "destination_id": destination_id,
        "destination": destination,
        "country": country,
        "swipe": swipe,
        "liked": liked
    }

    resultado = is_valid_swipe(valoracion)

    assert resultado == False


# Comprobar que las valoraciones se separan correctamente
def test_validate_swipes():

    df = pd.DataFrame({
        "user_id": ["user_1", "user_2", "user_3", "user_4"],
        "destination_id": [1, 2, 3, 4],
        "destination": ["Barcelona", "Paris", "Rome", "Berlin"],
        "country": ["Spain", "France", "Italy", "Germany"],
        "swipe": ["yes", "no", "yes", "maybe"],
        "liked": [1, 0, 0, 1]
    })

    valid_swipes, invalid_swipes = validate_swipes(df)

    assert len(valid_swipes) == 2
    assert len(invalid_swipes) == 2