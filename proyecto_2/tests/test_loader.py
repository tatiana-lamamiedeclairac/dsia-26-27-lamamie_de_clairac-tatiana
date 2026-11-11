
import pandas as pd
import pytest

from proyecto_2.citybreak_app.loader import load_citybreaks
from proyecto_2.citybreak_app.exceptions import DataLoadError


def test_load_citybreaks(tmp_path):
    """Comprueba la carga correcta de un CSV."""

    # Arrange
    path = tmp_path / "destinos.csv"

    expected = pd.DataFrame({
        "destination": ["Roma", "Lisboa"],
        "liked": [1, 0]
    })

    expected.to_csv(path, index=False)

    # Act
    result = load_citybreaks(path)

    # Assert
    pd.testing.assert_frame_equal(result, expected)


def test_load_citybreaks_not_found(tmp_path):
    """Comprueba el error cuando no existe el archivo."""

    # Arrange
    path = tmp_path / "inexistente.csv"

    # Act + Assert
    with pytest.raises(DataLoadError):
        load_citybreaks(path)


def test_load_citybreaks_empty(tmp_path):
    """Comprueba el error cuando el CSV está vacío."""

    # Arrange
    path = tmp_path / "vacio.csv"
    path.write_text("", encoding="utf-8")

    # Act + Assert
    with pytest.raises(DataLoadError):
        load_citybreaks(path)
