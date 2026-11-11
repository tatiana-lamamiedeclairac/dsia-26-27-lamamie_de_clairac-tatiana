
import sys

import pytest

from proyecto_2.citybreak_app import cli
from proyecto_2.citybreak_app.exceptions import DataLoadError


def test_cli_train(monkeypatch):
    """
    Comprueba que el comando train llama
    correctamente al módulo de entrenamiento.
    """

    # Arrange
    calls = []

    def fake_train(argv):
        calls.append(argv)

    monkeypatch.setattr(cli, "train_main", fake_train)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "citybreak",
            "train",
            "--output",
            "modelo_prueba.joblib"
        ]
    )

    # Act
    cli.main()

    # Assert
    assert len(calls) == 1
    assert "--output" in calls[0]
    assert "modelo_prueba.joblib" in calls[0]


def test_cli_recommend(monkeypatch):
    """
    Comprueba que recommend envía los argumentos
    correctamente al módulo de predicción.
    """

    # Arrange
    calls = []

    def fake_predict(argv):
        calls.append(argv)

    monkeypatch.setattr(cli, "predict_main", fake_predict)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "citybreak",
            "recommend",
            "--profile-row", "1000",
            "--top-k", "3",
            "--ai-provider", "mock"
        ]
    )

    # Act
    cli.main()

    # Assert
    assert len(calls) == 1
    assert calls[0][calls[0].index("--profile-row") + 1] == "1000"
    assert calls[0][calls[0].index("--top-k") + 1] == "3"
    assert calls[0][calls[0].index("--ai-provider") + 1] == "mock"


def test_cli_pipeline(monkeypatch):
    """
    Comprueba que el pipeline ejecuta
    entrenamiento y después predicción.
    """

    # Arrange
    calls = []

    def fake_train(argv):
        calls.append(("train", argv))

    def fake_predict(argv):
        calls.append(("predict", argv))

    monkeypatch.setattr(cli, "train_main", fake_train)
    monkeypatch.setattr(cli, "predict_main", fake_predict)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "citybreak",
            "pipeline",
            "--ai-provider", "mock"
        ]
    )

    # Act
    cli.main()

    # Assert
    assert len(calls) == 2

    assert calls[0][0] == "train"
    assert calls[1][0] == "predict"

    # El modelo que se guarda es el que se utiliza
    train_args = calls[0][1]
    predict_args = calls[1][1]

    output_path = train_args[
        train_args.index("--output") + 1
    ]

    model_path = predict_args[
        predict_args.index("--model") + 1
    ]

    assert output_path == model_path

    assert predict_args[
        predict_args.index("--ai-provider") + 1
    ] == "mock"


def test_cli_error(monkeypatch):
    """
    Comprueba que la CLI termina con código 1
    cuando ocurre un error durante el entrenamiento.
    """

    # Arrange
    def fake_train(argv):
        raise DataLoadError("No se encuentra el CSV")

    monkeypatch.setattr(cli, "train_main", fake_train)

    monkeypatch.setattr(
        sys,
        "argv",
        ["citybreak", "train"]
    )

    # Act + Assert
    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 1


def test_cli_invalid_provider(monkeypatch):
    """
    Comprueba que argparse rechaza
    proveedores de IA no permitidos.
    """

    # Arrange
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "citybreak",
            "recommend",
            "--ai-provider",
            "proveedor_inventado"
        ]
    )

    # Act + Assert
    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 2
