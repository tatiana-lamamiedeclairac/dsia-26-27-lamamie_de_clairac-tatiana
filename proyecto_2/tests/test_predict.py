
import numpy as np
import pandas as pd
import pytest

from proyecto_2.citybreak_app.predict import (
    load_model,
    recommend_destinations
)
from proyecto_2.citybreak_app.preprocessing import FORM_COLUMNS


# Modelo simulado para probar las recomendaciones
class FakeModel:

    def predict_proba(self, X):

        # Probabilidades conocidas para cada destino
        scores = X["destination_id"].map({
            "1": 0.2,
            "2": 0.9,
            "3": 0.6
        }).to_numpy()

        return np.column_stack([1 - scores, scores])


@pytest.fixture
def sample_destinations():
    """Crea tres destinos turísticos de ejemplo."""

    return pd.DataFrame({
        "destination_id": [1, 2, 3],
        "destination": ["Lisboa", "Roma", "París"],
        "country": ["Portugal", "Italy", "France"]
    })


@pytest.fixture
def sample_preferences():
    """Crea un perfil con las respuestas del cuestionario."""

    return {
        col: "[]"
        for col in FORM_COLUMNS
    }


def test_recommend_destinations(
    sample_destinations,
    sample_preferences
):
    # Arrange
    model = FakeModel()

    # Act
    result = recommend_destinations(
        model=model,
        preferences=sample_preferences,
        destinations=sample_destinations,
        top_k=2
    )

    # Assert
    assert len(result) == 2
    assert result.iloc[0]["destination"] == "Roma"
    assert result.iloc[1]["destination"] == "París"
    assert result.iloc[0]["probability"] == pytest.approx(0.9)


def test_invalid_top_k(
    sample_destinations,
    sample_preferences
):
    # Arrange
    model = FakeModel()

    # Act + Assert
    with pytest.raises(ValueError):
        recommend_destinations(
            model=model,
            preferences=sample_preferences,
            destinations=sample_destinations,
            top_k=0
        )


def test_load_model_not_found(tmp_path):
    # Arrange
    path = tmp_path / "modelo_inexistente.joblib"

    # Act + Assert
    with pytest.raises(FileNotFoundError):
        load_model(path)
