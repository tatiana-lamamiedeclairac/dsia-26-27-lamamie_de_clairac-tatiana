
# CityBreak App — Proyecto II

## 1. Descripción del proyecto

CityBreak App es un sistema de recomendación de destinos turísticos desarrollado para el Proyecto II de la asignatura de DSIA del Máster en Inteligencia Artificial Aplicada.

Su objetivo es recomendar destinos turísticos en función de las preferencias de los usuarios, combinando un modelo clásico de *Machine Learning* entrenado con scikit-learn y un servicio de inteligencia artificial generativa.

Este proyecto continúa el trabajo realizado en el Proyecto I, donde se implementaron la carga, validación y análisis de datos turísticos.

En esta segunda fase se ha desarrollado un sistema que permite:

- Procesar las preferencias y valoraciones de usuarios.
- Entrenar y comparar diferentes modelos de clasificación.
- Seleccionar, evaluar y guardar un modelo de Machine Learning.
- Generar un ranking personalizado de los cinco destinos más recomendables, configurable mediante `--top-k`.
- Presentar las recomendaciones con un cliente de IA generativa, en modo simulado o mediante la API de NVIDIA.
- Ejecutar el entrenamiento, la inferencia y la generación de texto desde una interfaz de línea de comandos (CLI).

El código se organiza en módulos reutilizables y dispone de pruebas automatizadas con pytest. Esta arquitectura servirá de base para el Proyecto III.

## 2. Dataset utilizado

### Origen y motivación

Se utiliza una muestra del conjunto de datos público **Stravl Travel Preference Dataset**, publicado por Stravl.

- **Fuente original:** [Stravl/Stravl-Data en GitHub](https://github.com/Stravl/Stravl-Data).
- **Archivo utilizado:** `proyecto_1/parte_b/data/stravl_citybreak_subset.csv`.

Se eligió este dominio porque el conjunto contiene preferencias declaradas por viajeros y valoraciones de destinos turísticos.

Esto permite formular un problema de clasificación binaria y reutilizar sus predicciones para ordenar destinos, con posibilidades de ampliación a una aplicación de recomendación de viajes en el Proyecto III.

La muestra utilizada contiene:

- 12.005 registros.
- 1.379 usuarios.
- 428 destinos turísticos.
- 44 países.
- 16 variables originales.

Entre las principales columnas se encuentran:

| Columna | Descripción |
|---|---|
| `user_id` | Identificador del usuario. |
| `destination_id` | Identificador del destino. |
| `destination` | Nombre del destino turístico. |
| `country` | País del destino. |
| `swipe` | Valoración positiva o negativa (`yes` / `no`). |
| `liked` | Variable objetivo binaria (`1` = positiva; `0` = negativa). |
| `form_a`, `form_b`, etc. | Respuestas codificadas a preguntas sobre preferencias turísticas. |

Las respuestas del cuestionario se transforman mediante Multi-Hot Encoding para poder utilizarlas como variables predictoras.

### Condiciones de uso y atribución

En el README del [repositorio original de Stravl](https://github.com/Stravl/Stravl-Data), sus autores indican que los datos pueden utilizarse con fines académicos o comerciales.

No se ha identificado una licencia estándar concreta, como MIT o Creative Commons, en la documentación consultada. Por tanto, se cita el permiso indicado por los autores sin atribuir al conjunto una licencia que no conste expresamente.

**Fuente y atribución:** Stravl, *Stravl-Data: Travel Preference Dataset*, GitHub.

https://github.com/Stravl/Stravl-Data

El Proyecto II reutiliza el CSV del Proyecto I sin duplicarlo. Para ejecutar los comandos con la ruta predeterminada es necesario disponer de ambas carpetas dentro del repositorio.

## 3. Arquitectura del proyecto

El código principal se encuentra en:

`proyecto_2/src/proyecto_2/citybreak_app/`

El sistema está dividido en módulos con responsabilidades diferenciadas.

| Módulo | Funcionalidad |
|---|---|
| `loader.py` | Carga de los datos del CSV. |
| `validator.py` | Validación y separación de registros válidos e inválidos. |
| `preprocessing.py` | Transformación y codificación de las respuestas del cuestionario. |
| `features.py` | Preparación de variables predictoras e interacciones entre preferencias y destinos. |
| `train.py` | División de datos, entrenamiento, comparación y evaluación de modelos. |
| `predict.py` | Carga del modelo y generación del ranking de destinos. |
| `genai_client.py` | Integración de IA generativa con proveedores mock y NVIDIA. |
| `cli.py` | Orquestación del pipeline mediante comandos. |
| `exceptions.py` | Gestión de excepciones específicas. |

El flujo completo es:

**Carga de datos → Validación → División por usuarios → Preprocesamiento → Entrenamiento → Evaluación → Guardado del modelo → Inferencia → Ranking Top 5 → IA generativa.**

El entrenamiento y la inferencia pueden ejecutarse por separado para evitar volver a entrenar el modelo cada vez que se solicitan recomendaciones.

Esta organización modular permite incorporar posteriormente una API y una interfaz web sin reescribir el núcleo de procesamiento y predicción.

## 4. Machine Learning

### Planteamiento del problema

Se ha planteado un problema de **clasificación binaria** utilizando `liked` como variable objetivo.

El modelo aprende a estimar la probabilidad de que un usuario con determinadas preferencias valore positivamente un destino turístico.

Para convertir este clasificador en un recomendador, se calcula la probabilidad estimada para los destinos disponibles y se ordenan de mayor a menor, seleccionando los cinco primeros por defecto.

### Preprocesamiento

Las respuestas del cuestionario se transforman de cadenas de texto a listas y posteriormente se codifican mediante Multi-Hot Encoding.

Las variables `destination_id` y `country` se tratan como categóricas.

Además, se han incorporado interacciones entre las preferencias de los usuarios y los destinos para permitir una mayor personalización de las recomendaciones.

El procesamiento necesario para el estimador se incluye en un `Pipeline` de scikit-learn, que se guarda junto con el clasificador entrenado.

### División de los datos

Se utiliza `GroupShuffleSplit` para separar los datos por `user_id` y evitar que un mismo usuario aparezca en diferentes conjuntos.

La distribución aproximada es:

- Entrenamiento: 70 %.
- Validación: 15 %.
- Prueba: 15 %.

Las proporciones corresponden a grupos de usuarios y pueden variar ligeramente en número de registros.

### Modelos comparados

Se han entrenado y evaluado los siguientes clasificadores:

- `DummyClassifier`, como referencia.
- `LogisticRegression`.
- `RandomForestClassifier`.
- `ExtraTreesClassifier`.
- `LogisticRegression` con interacciones entre preferencias y destinos (`LogisticInteractions`).

La selección se realiza según el **ROC-AUC del conjunto de validación**, excluyendo el clasificador de referencia.

Una vez seleccionado el mejor modelo, se evalúa en el conjunto de prueba.

### Resultados

El modelo seleccionado ha sido **LogisticInteractions**, con los siguientes resultados, redondeados a cuatro decimales:

| Métrica | Validación | Test |
|---|---:|---:|
| Accuracy | 0,5951 | 0,6191 |
| F1-score | 0,6604 | 0,6894 |
| ROC-AUC | 0,6273 | 0,6188 |
| Average Precision | 0,6573 | 0,6710 |

Los resultados muestran una capacidad predictiva limitada, aunque el ROC-AUC supera el valor 0,5 de una clasificación sin capacidad discriminativa.

También se ha comprobado manualmente que el sistema puede generar rankings diferentes para usuarios con distintas preferencias.

No obstante, esta comprobación no garantiza por sí sola que las recomendaciones sean acertadas para usuarios reales.

Los artefactos generados se almacenan en:

- `models/model.joblib`: modelo entrenado y pipeline de preprocesamiento.
- `models/metrics.json`: comparación de modelos, métricas de evaluación y resumen de registros.

El modelo puede regenerarse utilizando el comando de entrenamiento documentado en el apartado de ejecución.

## 5. Integración de IA generativa

El proyecto incorpora un cliente de IA generativa con una interfaz común definida mediante `Protocol` y dos proveedores.

### MockProvider

Devuelve una respuesta simulada sin realizar peticiones a servicios externos.

Permite:

- Ejecutar el pipeline sin conexión a internet.
- Realizar pruebas sin utilizar credenciales.
- Comprobar la integración de IA generativa de forma reproducible.

### NvidiaProvider

Utiliza la API de NVIDIA para generar respuestas en lenguaje natural a partir de los destinos recomendados por el modelo de Machine Learning.

Se utiliza el modelo:

`nvidia/nemotron-3.5-super-vl-120b-a12b`

Mediante el endpoint:

`https://integrate.api.nvidia.com/v1`

La arquitectura utiliza `Protocol` para definir una interfaz común y permitir el intercambio de proveedores.

Las credenciales se obtienen mediante variables de entorno y no se incluyen en el código fuente.

La integración incorpora:

- Logging.
- Timeouts.
- Reintentos limitados.
- Gestión de errores de conexión.
- Validación de las respuestas de la API.

Actualmente, la IA generativa presenta las recomendaciones en lenguaje natural, sin modificar las probabilidades ni el orden de los destinos.

La generación de explicaciones más personalizadas queda como una mejora futura, al depender de la interpretación de las respuestas del cuestionario y de información adicional fiable sobre los destinos.

## 6. Instalación y configuración

### Requisitos

- Python 3.12 o una versión compatible con `pyproject.toml`.
- `uv` como gestor de dependencias recomendado, o `pip`.
- Acceso al repositorio completo, incluyendo los datos del Proyecto I.
- Una API Key de NVIDIA únicamente para ejecutar el proveedor real.

### Preparar el entorno con uv

Desde la raíz del repositorio:

```bash
cd proyecto_2
uv sync --frozen --dev
```

Las dependencias del proyecto se declaran en `pyproject.toml` y se fijan mediante `uv.lock`.

### Alternativa con pip

Desde `proyecto_2`, dentro de un entorno virtual activado:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

La segunda instrucción instala el paquete local para que puedan ejecutarse los módulos `proyecto_2.citybreak_app`.

### Variables de entorno

El repositorio incluye el archivo `.env.example` como plantilla de configuración.

Para utilizar el proveedor real, crear el archivo `proyecto_2/.env` con el siguiente contenido:

```dotenv
NVIDIA_API_KEY=tu_clave_privada
AI_PROVIDER=nvidia
```

La selección del proveedor en la CLI se realiza mediante el argumento `--ai-provider`.

La variable `AI_PROVIDER` del ejemplo no modifica por sí sola el proveedor predeterminado en la implementación actual.

El archivo `.env` está excluido del control de versiones mediante `.gitignore` y no debe subirse a GitHub.

El modo mock no necesita una API Key.

## 7. Ejecución del programa

Todos los comandos siguientes se ejecutan desde `proyecto_2`.

### Mostrar la ayuda

```bash
uv run python -m proyecto_2.citybreak_app.cli --help
```

### Entrenar el modelo

```bash
uv run python -m proyecto_2.citybreak_app.cli train
```

Este comando realiza las siguientes operaciones:

1. Carga y validación de datos.
2. División de los registros por usuarios.
3. Preprocesamiento y codificación de variables.
4. Entrenamiento y comparación de modelos.
5. Selección del mejor clasificador.
6. Evaluación en el conjunto de prueba.
7. Guardado del modelo y de las métricas.

### Generar recomendaciones

Después de entrenar:

```bash
uv run python -m proyecto_2.citybreak_app.cli recommend
```

Se generan cinco destinos recomendados a partir de un perfil de ejemplo del dataset.

Para utilizar otro perfil:

```bash
uv run python -m proyecto_2.citybreak_app.cli recommend --profile-row 1000
```

Para modificar el número de destinos recomendados:

```bash
uv run python -m proyecto_2.citybreak_app.cli recommend --top-k 3
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

**Importante:** el comando `pipeline` vuelve a entrenar y sobrescribe el modelo previamente guardado. Para realizar únicamente inferencia, se debe utilizar `recommend`.

## 8. Tests automatizados

Los tests se han implementado con `pytest` y siguen el patrón Arrange, Act, Assert.

Se comprueban, entre otros aspectos:

- Carga y validación de datos.
- Manejo de errores.
- Separación de usuarios entre conjuntos.
- Entrenamiento, guardado y carga del modelo.
- Inferencia mediante el modelo guardado.
- Generación y ordenación de recomendaciones.
- Cliente de IA generativa con respuestas simuladas.
- Simulación de respuestas del proveedor NVIDIA.
- Orquestación de la CLI.

Para ejecutar los tests:

```bash
uv run python -m pytest -q tests/
```

Para calcular la cobertura:

```bash
uv run python -m pytest -q tests/ --cov=proyecto_2.citybreak_app --cov-report=term-missing
```

En la última ejecución local documentada se han obtenido:

- **41 tests superados.**
- **64 % de cobertura total.**

Los tests automatizados no realizan peticiones reales al servicio de NVIDIA.

## 9. Integración continua

El proyecto contempla un workflow de GitHub Actions para ejecutar las pruebas automáticamente.

El workflow se encuentra en:

`.github/workflows/ci_proyecto_2.yml`

Su propósito es instalar las dependencias del proyecto y ejecutar pytest sin necesidad de credenciales externas.

El resultado de las ejecuciones puede comprobarse desde la pestaña **Actions** del repositorio de GitHub.

## 10. Limitaciones y continuidad hacia el Proyecto III

Las principales limitaciones del sistema actual son:

- El dataset contiene un número relativamente reducido de valoraciones por destino.
- Las métricas del clasificador muestran una capacidad de discriminación moderada-baja.
- No se dispone todavía de un diccionario completo y verificado de las respuestas del cuestionario.
- El recomendador utiliza únicamente los destinos presentes en el dataset original.
- Las probabilidades del modelo no deben interpretarse como garantías de satisfacción del usuario.
- Las explicaciones generativas todavía no incorporan información turística o meteorológica adicional verificada.

### Continuidad hacia el Proyecto III

El Proyecto II constituye la base del Proyecto III, en el que se pretende ampliar el sistema mediante:

- Una API desarrollada con **FastAPI**, que permita consultar recomendaciones desde endpoints.
- Una interfaz web para introducir preferencias y visualizar resultados.
- Integración de **Open-Meteo** para complementar las recomendaciones con información meteorológica.
- Pruebas adicionales de integración y robustez.
- Despliegue y monitorización del sistema.

El objetivo es reutilizar los módulos de carga, validación, preprocesamiento, entrenamiento, inferencia e IA generativa desarrollados en esta entrega, sin reescribir el núcleo de la aplicación.

## 11. Uso de inteligencia artificial durante el desarrollo

El uso de herramientas de inteligencia artificial como apoyo durante el desarrollo se documenta en [`AI_USAGE.md`](AI_USAGE.md).

En dicho archivo se describen las herramientas utilizadas y su aplicación en tareas como:

- Implementación y mejora del código.
- Resolución de errores.
- Desarrollo y evaluación del modelo de Machine Learning.
- Elaboración de tests.
- Documentación del proyecto.
- Revisión de los resultados.

