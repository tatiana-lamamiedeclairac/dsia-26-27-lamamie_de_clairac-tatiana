
from types import SimpleNamespace

import pytest

from proyecto_2.citybreak_app.genai_client import (
    MockProvider,
    NvidiaProvider,
    AIServiceError,
    build_prompt,
    generate_explanation
)


# 1. Comprobar el proveedor mock
def test_mock_provider():

    # Arrange
    provider = MockProvider()
    prompt = "Recomienda destinos turísticos"

    # Act
    response = provider.generate(prompt)

    # Assert
    assert isinstance(response, str)
    assert len(response) > 0
    assert "[MOCK]" in response


# 2. Comprobar la construcción del prompt
def test_build_prompt():

    # Arrange
    destinations = ["Roma, Italia", "Lisboa, Portugal"]

    # Act
    prompt = build_prompt(destinations)

    # Assert
    assert "Roma, Italia" in prompt
    assert "Lisboa, Portugal" in prompt
    assert "1. Roma, Italia" in prompt
    assert "2. Lisboa, Portugal" in prompt


# 3. Comprobar que no acepta destinos vacíos
def test_build_prompt_empty():

    # Arrange
    destinations = []

    # Act + Assert
    with pytest.raises(ValueError):
        build_prompt(destinations)


# 4. Comprobar la selección del proveedor mock
def test_generate_explanation_mock():

    # Arrange
    destinations = ["Catania, Italia"]

    # Act
    response = generate_explanation(
        destinations,
        provider="mock"
    )

    # Assert
    assert "[MOCK]" in response


# 5. Comprobar un proveedor no válido
@pytest.mark.parametrize(
    "provider",
    ["invalid", "unknown", "otro"]
)
def test_invalid_provider(provider):

    # Arrange
    destinations = ["Roma, Italia"]

    # Act + Assert
    with pytest.raises(ValueError):
        generate_explanation(
            destinations,
            provider=provider
        )


# 6. Simular una respuesta correcta de NVIDIA
def test_nvidia_response():

    # Arrange
    # Crear el proveedor sin ejecutar su conexión real
    provider = NvidiaProvider.__new__(NvidiaProvider)

    # Simular la respuesta de la API
    fake_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content="Roma es uno de los destinos recomendados."
                )
            )
        ]
    )

    # Simular el cliente de NVIDIA
    provider.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: fake_response
            )
        )
    )

    # Act
    result = provider.generate(
        "Explica la recomendación de Roma"
    )

    # Assert
    assert result == "Roma es uno de los destinos recomendados."


# 7. Comprobar una respuesta vacía de NVIDIA
def test_nvidia_empty_response():

    # Arrange
    provider = NvidiaProvider.__new__(NvidiaProvider)

    fake_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=""
                )
            )
        ]
    )

    provider.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: fake_response
            )
        )
    )

    # Act + Assert
    with pytest.raises(AIServiceError):
        provider.generate(
            "Explica la recomendación de Roma"
        )
