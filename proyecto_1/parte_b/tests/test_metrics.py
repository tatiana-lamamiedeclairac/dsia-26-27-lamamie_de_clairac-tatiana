import pandas as pd

from parte_b.citybreak_app.metrics import (
    total_likes,
    likes_by_country,
    likes_by_destination
)


# Comprobar que se calcula correctamente el total de likes
def test_total_likes():

    df = pd.DataFrame({
        "liked": [1, 0, 1, 1, 0]
    })

    resultado = total_likes(df)

    assert resultado == 3


# Comprobar que se calculan correctamente los likes por país
def test_likes_by_country():

    df = pd.DataFrame({
        "country": ["Spain", "France", "Spain", "Italy"],
        "liked": [1, 0, 1, 1]
    })

    resultado = likes_by_country(df)

    assert resultado["Spain"] == 2
    assert resultado["France"] == 0
    assert resultado["Italy"] == 1


# Comprobar que se calculan correctamente los likes por destino
def test_likes_by_destination():

    df = pd.DataFrame({
        "destination": ["Barcelona", "Paris", "Barcelona", "Rome"],
        "liked": [1, 0, 1, 1]
    })

    resultado = likes_by_destination(df)

    assert resultado["Barcelona"] == 2
    assert resultado["Paris"] == 0
    assert resultado["Rome"] == 1