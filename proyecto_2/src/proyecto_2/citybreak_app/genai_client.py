
import logging
import os
from pathlib import Path
from typing import Protocol

from dotenv import load_dotenv
from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    APIStatusError
)


logger = logging.getLogger(__name__)

# Configuración de NVIDIA
PROJECT_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = PROJECT_DIR / ".env"

NVIDIA_MODEL = "nvidia/nemotron-3.5-super-vl-120b-a12b"
NVIDIA_URL = "https://integrate.api.nvidia.com/v1"


class AIServiceError(Exception):
    """Error al utilizar el servicio de IA generativa."""


class AIProvider(Protocol):
    """
    Interfaz común para los proveedores de IA.
    """

    def generate(self, prompt: str) -> str:
        ...


class MockProvider:
    """
    Simula una respuesta sin utilizar una API real.
    """

    def generate(self, prompt: str) -> str:
        return (
            "[MOCK] Estos destinos han sido seleccionados "
            "por el modelo de Machine Learning. "
            "Compara las opciones antes de organizar tu viaje."
        )


class NvidiaProvider:
    """
    Genera respuestas mediante la API de NVIDIA.
    """

    def __init__(self):

        # Cargar las variables de entorno
        load_dotenv(ENV_PATH)

        api_key = os.getenv("NVIDIA_API_KEY")

        if not api_key:
            raise AIServiceError(
                "No se ha configurado NVIDIA_API_KEY en .env"
            )

        # Crear cliente de NVIDIA
        self.client = OpenAI(
            base_url=NVIDIA_URL,
            api_key=api_key,
            timeout=30.0,
            max_retries=1
        )

    def generate(self, prompt: str) -> str:

        try:
            response = self.client.chat.completions.create(
                model=NVIDIA_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un asistente de recomendaciones "
                            "turísticas. Responde en español, "
                            "de manera breve y clara. "
                            "No inventes datos sobre los destinos "
                            "ni atribuyas al usuario preferencias "
                            "que no se hayan proporcionado."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=1.0,
                top_p=0.95,
                max_tokens=500,
                stream=False,
                extra_body={
                    "chat_template_kwargs": {
                        "enable_thinking": False
                    }
                }
            )

        except (APITimeoutError, APIConnectionError) as e:
            raise AIServiceError(
                "No se ha podido conectar con NVIDIA."
            ) from e

        except APIStatusError as e:
            raise AIServiceError(
                f"NVIDIA ha devuelto el error HTTP {e.status_code}."
            ) from e

        if not response.choices:
            raise AIServiceError(
                "NVIDIA no ha devuelto ninguna respuesta."
            )

        content = response.choices[0].message.content

        if not content or not content.strip():
            raise AIServiceError(
                "NVIDIA ha devuelto una respuesta vacía."
            )

        return content.strip()


def build_prompt(destinations: list[str]) -> str:
    """
    Construye el prompt a partir de los destinos recomendados.
    """

    if not destinations:
        raise ValueError(
            "Se necesita al menos un destino recomendado."
        )

    destination_text = "\n".join(
        f"{i}. {destination}"
        for i, destination in enumerate(destinations, start=1)
    )

    return (
        "Nuestro modelo de Machine Learning ha recomendado "
        "los siguientes destinos turísticos:\n\n"
        f"{destination_text}\n\n"
        "Redacta una breve introducción para presentar "
        "estas recomendaciones al usuario. "
        "No inventes motivos específicos de personalización, "
        "previsiones meteorológicas ni información que "
        "no se haya proporcionado. "
        "No modifiques el orden de las recomendaciones."
    )


def generate_explanation(
    destinations: list[str],
    provider: str = "mock"
) -> str:
    """
    Genera una explicación utilizando el proveedor indicado.
    """

    prompt = build_prompt(destinations)

    if provider == "mock":
        client = MockProvider()

    elif provider == "nvidia":
        client = NvidiaProvider()

    else:
        raise ValueError(
            f"Proveedor de IA no válido: {provider}"
        )

    logger.info(
        "Generando explicación con proveedor: %s",
        provider
    )

    return client.generate(prompt)
