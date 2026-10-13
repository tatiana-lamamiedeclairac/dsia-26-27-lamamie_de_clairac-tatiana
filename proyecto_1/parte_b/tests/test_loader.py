import pandas as pd
import pytest

from parte_b.citybreak_app.loader import load_citybreaks
from parte_b.citybreak_app.exceptions import DataLoadError

# Comprobar que el csv carga correctamente
def test_load():
    df = load_citybreaks("parte_b/data/stravl_citybreak_subset.csv")

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 12005

def test_load_file_not_found():
    with pytest.raises(DataLoadError):
        load_citybreaks("archivo_inexistente.csv")