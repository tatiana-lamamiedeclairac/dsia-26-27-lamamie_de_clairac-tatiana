
import pandas as pd
import pytest

from proyecto_2.citybreak_app.validator import (
    is_valid_swipe,
    validate_swipes
)


@pytest.fixture
def valid_row():
    """
    Crea una valoración válida para utilizar
    como base en los tests.
    """

    return pd.Series({
        "user_id": "user_1",
        "destination_id": 10,
        "destination": "Roma",
        "country": "Italy",
        "swipe": "yes",
        "liked": 1
    })


# 1. Comprobar una valoración positiva válida
def test_valid_positive_swipe(valid_row):

    # Act
    result = is_valid_swipe(valid_row)

    # Assert
    assert result is True


# 2. Comprobar una valoración negativa válida
def test_valid_negative_swipe(valid_row):

    # Arrange
    valid_row["swipe"] = "no"
    valid_row["liked"] = 0

    # Act
    result = is_valid_swipe(valid_row)

    # Assert
    assert result is True


# 3. Comprobar los diferentes errores de validación
@pytest.mark.parametrize(
    "column, invalid_value",
    [
        # Valores nulos
        ("user_id", None),
        ("destination", None),
        ("country", None),

        # Textos vacíos
        ("user_id", ""),
        ("destination", "   "),
        ("country", ""),

        # Identificador de destino incorrecto
        ("destination_id", None),
        ("destination_id", "abc"),
        ("destination_id", -1),

        # Valoración incorrecta
        ("swipe", "maybe"),
        ("swipe", ""),
        ("liked", 2),
        ("liked", -1)
    ]
)
def test_invalid_swipe(
    valid_row,
    column,
    invalid_value
):
    """
    Comprueba que se rechazan registros
    que incumplen las reglas de validación.
    """

    # Arrange
    valid_row[column] = invalid_value

    # Act
    result = is_valid_swipe(valid_row)

    # Assert
    assert result is False


# 4. Comprobar incoherencia entre swipe y liked
@pytest.mark.parametrize(
    "swipe, liked",
    [
        ("yes", 0),
        ("no", 1)
    ]
)
def test_inconsistent_swipe(valid_row, swipe, liked):

    # Arrange
    valid_row["swipe"] = swipe
    valid_row["liked"] = liked

    # Act
    result = is_valid_swipe(valid_row)

    # Assert
    assert result is False


# 5. Comprobar la separación de registros
def test_validate_swipes():

    # Arrange
    df = pd.DataFrame([
        {
            "user_id": "user_1",
            "destination_id": 1,
            "destination": "Roma",
            "country": "Italy",
            "swipe": "yes",
            "liked": 1
        },
        {
            "user_id": "user_2",
            "destination_id": 2,
            "destination": "Lisboa",
            "country": "Portugal",
            "swipe": "no",
            "liked": 0
        },
        {
            "user_id": "user_3",
            "destination_id": -1,
            "destination": "París",
            "country": "France",
            "swipe": "yes",
            "liked": 1
        }
    ])

    # Act
    valid, invalid = validate_swipes(df)

    # Assert
    assert len(valid) == 2
    assert len(invalid) == 1

    assert set(valid["destination"]) == {
        "Roma",
        "Lisboa"
    }

    assert invalid.iloc[0]["destination"] == "París"


# 6. Comprobar que se acepta un ID numérico como texto
def test_destination_id_as_string(valid_row):

    # Arrange
    valid_row["destination_id"] = "10"

    # Act
    result = is_valid_swipe(valid_row)

    # Assert
    assert result is True
