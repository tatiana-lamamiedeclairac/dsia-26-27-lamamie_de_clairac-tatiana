import sys
import pytest

from parte_b.citybreak_app.cli import main


# Comprobar que el programa principal funciona correctamente
@pytest.mark.integration
def test_main(monkeypatch, capsys):

    monkeypatch.setattr(
        sys,
        "argv",
        ["cli", "--input", "parte_b/data/stravl_citybreak_subset.csv"]
    )

    main()

    resultado = capsys.readouterr()

    assert "Valoraciones válidas:" in resultado.out
    assert "Valoraciones inválidas:" in resultado.out
    assert "Total de likes:" in resultado.out
    assert "Likes por país:" in resultado.out
    assert "Likes por destino:" in resultado.out