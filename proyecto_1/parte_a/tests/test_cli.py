import sys

from parte_a.ventas_app.cli import main


# Comprueba que el programa principal funciona correctamente
def test_main(monkeypatch, capsys):

    monkeypatch.setattr(
        sys,
        "argv",
        ["cli", "--input", "parte_a/data/ventas.csv"]
    )

    main()

    resultado = capsys.readouterr()

    assert "Ventas válidas: 140" in resultado.out
    assert "Ventas inválidas: 10" in resultado.out
    assert "Importe total:" in resultado.out