# CityBreak App — Proyecto II

## 1. Descripción del proyecto

CityBreak App es un sistema de recomendación de destinos turísticos desarrollado para la asignatura de Programación Avanzada en Python del Máster en Inteligencia Artificial Aplicada.

El objetivo es recomendar destinos turísticos en función de las preferencias personales de los usuarios, utilizando técnicas de Machine Learning e Inteligencia Artificial generativa.

El proyecto amplía el trabajo realizado en el Proyecto I, donde se implementaron la carga, validación y análisis de datos turísticos.

En esta segunda fase se ha desarrollado un sistema que permite:

- Procesar las preferencias y valoraciones de usuarios.
- Entrenar y comparar diferentes modelos de clasificación.
- Seleccionar y guardar un modelo de Machine Learning.
- Generar un ranking personalizado con los cinco destinos más recomendables.
- Complementar las recomendaciones mediante una API de IA generativa.
- Ejecutar el proceso completo desde una interfaz de línea de comandos (CLI).

El sistema está desarrollado de forma modular y dispone de tests automatizados e integración continua mediante GitHub Actions.

## 2. Dataset utilizado

Se utiliza una muestra del dataset público **Stravl Travel Preference Dataset**.

El archivo contiene:

- 12.005 registros.
- 1.379 usuarios.
- 428 destinos turísticos.
- 44 países.
- 16 variables originales.

Entre las variables principales se encuentran:

- `user_id`: identificador del usuario.
- `destination_id`: identificador del destino.
- `destination`: nombre del destino turístico.
- `country`: país del destino.
- `swipe`: valoración positiva o negativa.
- `liked`: variable objetivo binaria (1 = valoración positiva, 0 = negativa).
- `form_a`, `form_b`, etc.: respuestas al cuestionario de preferencias turísticas.

Las respuestas del cuestionario se encuentran codificadas y se transforman mediante Multi-Hot Encoding para poder utilizarlas en los modelos.

El dataset original se encuentra en:

`proyecto_1/parte_b/data/stravl_citybreak_subset.csv`

Por tanto, el Proyecto II reutiliza los datos del Proyecto I sin duplicarlos. Para ejecutar el sistema con su configuración por defecto es necesario conservar ambas carpetas dentro del repositorio.

## 3. Arquitectura del proyecto

El sistema está dividido en módulos con responsabilidades diferenciadas.

| Módulo | Funcionalidad |
|---|---|
| `loader.py` | Carga de los datos del CSV. |
| `validator.py` | Validación de los registros y separación de datos válidos e inválidos. |
| `preprocessing.py` | Transformación y codificación de las respuestas del cuestionario. |
| `features.py` | Preparación de las variables predictoras e interacciones entre preferencias y destinos. |
| `train.py` | División de datos, entrenamiento, comparación y evaluación de modelos. |
| `predict.py` | Carga del modelo y generación del ranking de destinos. |
| `genai_client.py` | Integración de IA generativa con proveedores mock y NVIDIA. |
| `cli.py` | Orquestación del pipeline mediante comandos. |
| `exceptions.py` | Gestión de excepciones específicas. |

El flujo completo es:

**Carga de datos → Validación → Preprocesamiento → Entrenamiento → Evaluación → Guardado del modelo → Inferencia → Ranking Top 5 → IA generativa.**

El entrenamiento y la inferencia pueden ejecutarse por separado para evitar entrenar de nuevo el modelo en cada consulta.

## 4. Machine Learning

### Planteamiento del problema

Se ha planteado un problema de clasificación binaria utilizando `liked` como variable objetivo.

El modelo aprende a estimar la probabilidad de que un usuario con determinadas preferencias valore positivamente un destino turístico.

Para convertir este clasificador en un recomendador, se calcula la probabilidad estimada para los destinos disponibles y se ordenan de mayor a menor, seleccionando los cinco primeros.

### Preprocesamiento

Las respuestas del cuestionario se transforman de cadenas de texto a listas y posteriormente se codifican mediante Multi-Hot Encoding.

Las variables `destination_id` y `country` se tratan como categóricas.

Además, se han incorporado interacciones entre las preferencias de los usuarios y los destinos para permitir una mayor personalización de las recomendaciones.

### División de los datos

Se utiliza `GroupShuffleSplit` para separar los datos por usuarios y evitar que una misma persona aparezca en diferentes conjuntos.

La distribución aproximada es:

- Entrenamiento: 70 %.
- Validación: 15 %.
- Prueba: 15 %.

Las proporciones corresponden a usuarios y pueden variar ligeramente en número de registros.

### Modelos comparados

Se han evaluado los siguientes clasificadores:

- DummyClassifier, como referencia.
- LogisticRegression.
- RandomForestClassifier.
- ExtraTreesClassifier.
- LogisticRegression con interacciones entre preferencias y destinos.

La selección se realiza según el ROC-AUC del conjunto de validación, excluyendo el clasificador de referencia.

### Resultados

El modelo seleccionado ha sido **LogisticInteractions**, con los siguientes resultados:

| Métrica | Validación | Test |
|---|---:|---:|
| Accuracy | 0,5951 | 0,6109 |
| F1-score | 0,6604 | 0,6894 |
| ROC-AUC | 0,6273 | 0,6188 |
| Average Precision | 0,6573 | 0,6710 |

Los resultados muestran una capacidad predictiva limitada, aunque superior a una referencia aleatoria en términos de ROC-AUC.

También se ha comprobado manualmente que el sistema puede generar rankings diferentes para usuarios con distintas preferencias.

No obstante, esta comprobación no garantiza por sí sola que las recomendaciones sean acertadas.

Las métricas se almacenan en `models/metrics.json`, mientras que el modelo entrenado se guarda en `models/model.joblib`.

## 5. Integración de IA generativa

El proyecto incorpora un cliente de IA generativa con dos proveedores:

**MockProvider:** devuelve una respuesta simulada. Permite realizar tests y ejecutar el pipeline sin conexión a internet ni credenciales.

**NvidiaProvider:** utiliza la API de NVIDIA para generar respuestas en lenguaje natural a partir de los destinos recomendados.

Se utiliza el modelo `nvidia/nemotron-3.5-super-vl-120b-a12b` mediante el endpoint de NVIDIA.

La arquitectura utiliza `Protocol` para definir una interfaz común y permitir el intercambio de proveedores.

Las credenciales se almacenan mediante variables de entorno y no se incluyen en el código fuente.

La integración incorpora logging, timeouts, reintentos limitados y gestión de errores de comunicación.

Actualmente, la IA generativa presenta las recomendaciones en lenguaje natural. La generación de explicaciones más personalizadas queda como una mejora futura, al depender de la interpretación de las respuestas del cuestionario y de información adicional fiable sobre los destinos.

## 6. Instalación

### Requisitos

- Python 3.12.
- `uv` como gestor de dependencias.
- Acceso al repositorio completo, incluyendo los datos del Proyecto I.
- Una API Key de NVIDIA únicamente para ejecutar el proveedor real.

### Preparar el entorno

Desde la raíz del repositorio:

```bash
cd proyecto_2
uv sync --frozen --dev
```

Como alternativa, el archivo `requirements.txt` permite instalar las dependencias utilizando pip en un entorno virtual compatible.

### Variables de entorno

Para utilizar NVIDIA, crear el archivo `proyecto_2/.env` con:

```dotenv
NVIDIA_API_KEY=tu_clave_privada
AI_PROVIDER=nvidia
```

El archivo `.env` está excluido del control de versiones mediante `.gitignore`.

El repositorio contiene `.env.example` como referencia, sin credenciales reales.

El modo mock no necesita una API Key.

## 7. Ejecución

Todos los comandos siguientes se ejecutan desde `proyecto_2`.

### Mostrar la ayuda

```bash
uv run python -m proyecto_2.citybreak_app.cli --help
```

### Entrenar el modelo

```bash
uv run python -m proyecto_2.citybreak_app.cli train
```

Este comando procesa los datos, compara modelos, selecciona uno y guarda los artefactos del entrenamiento.

### Generar recomendaciones

Después de entrenar:

```bash
uv run python -m proyecto_2.citybreak_app.cli recommend
```

Se generan cinco destinos recomendados a partir de un perfil de prueba del dataset.

Para utilizar otro perfil:

```bash
uv run python -m proyecto_2.citybreak_app.cli recommend --profile-row 1000
```

### Recomendaciones con IA simulada

```bash
uv run python -m proyecto_2.citybreak_app.cli recommend --ai-provider mock
```

### Recomendaciones con NVIDIA

```bash
uv run python -m proyecto_2.citybreak_app.cli recommend --ai-provider nvidia
```

Este comando necesita una API Key válida y realiza una petición real al servicio externo.

### Ejecutar el pipeline completo

```bash
uv run python -m proyecto_2.citybreak_app.cli pipeline --ai-provider mock
```

Este comando ejecuta el entrenamiento, la inferencia y la generación de texto de manera automatizada.

**Nota:** el comando `pipeline` vuelve a entrenar y sobrescribe el modelo previamente guardado. Para realizar únicamente inferencia, utilizar `recommend`.

## 8. Tests automatizados

Los tests se han implementado con pytest y siguen el patrón Arrange, Act, Assert.

Se comprueban, entre otros aspectos:

- Carga y validación de datos.
- Manejo de errores.
- Separación de usuarios entre conjuntos.
- Entrenamiento, guardado y carga del modelo.
- Generación y ordenación de recomendaciones.
- Cliente de IA generativa con respuestas simuladas.
- Orquestación de la CLI.

Para ejecutar los tests:

```bash
uv run python -m pytest -q tests/
```

Para calcular la cobertura:

```bash
uv run python -m pytest -q tests/ --cov=proyecto_2.citybreak_app --cov-report=term-missing
```

En la última ejecución local se han obtenido:

- **41 tests superados.**
- **64 % de cobertura total.**

Los tests automatizados no realizan peticiones reales a NVIDIA.

## 9. Integración continua

El proyecto dispone de un workflow de GitHub Actions que ejecuta los tests automáticamente.

El workflow se encuentra en:

`.github/workflows/ci_proyecto_2.yml`

La integración continua utiliza las dependencias del proyecto y ejecuta pytest sin necesidad de credenciales externas.

## 10. Limitaciones y mejoras futuras

Las principales limitaciones son:

- El dataset contiene un número relativamente reducido de valoraciones por destino.
- Las métricas del clasificador muestran una capacidad de discriminación moderada-baja.
- No se dispone todavía de un diccionario completo verificado de las respuestas del cuestionario.
- El recomendador utiliza los destinos presentes en el dataset original.
- Las probabilidades del modelo no deben interpretarse como garantías de satisfacción del usuario.
- Las explicaciones generativas todavía no incorporan información turística o meteorológica adicional verificada.

En el Proyecto III se pretende ampliar el sistema mediante una API desarrollada con FastAPI, una interfaz web y la integración de Open-Meteo para complementar las recomendaciones con información meteorológica.

## 11. Uso de inteligencia artificial durante el desarrollo

El uso de asistentes de inteligencia artificial para apoyar el desarrollo del proyecto se documenta en `AI_USAGE.md`, incluyendo las tareas realizadas, las aportaciones aceptadas y la revisión del código y sus resultados.