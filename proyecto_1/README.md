
# Proyecto I - Programación avanzada en Python

Este proyecto corresponde a la asignatura de Programación Avanzada en Python.

El objetivo es desarrollar dos programas que permitan cargar datos desde archivos CSV, validar la información y calcular diferentes métricas.

El proyecto está dividido en dos partes:

- **Parte A:** análisis de datos de ventas.
- **Parte B:** análisis de preferencias de destinos turísticos.

Ambas partes utilizan Python, pandas y pytest.

## 1. Estructura del proyecto

```text
proyecto_1/
├── .github/
│   └── workflows/
│       └── ci.yml
├── parte_a/
│   ├── ventas_app/
│   │   ├── exceptions.py
│   │   ├── loader.py
│   │   ├── validator.py
│   │   ├── metrics.py
│   │   └── cli.py
│   ├── data/
│   │   └── ventas.csv
│   └── tests/
│       ├── test_loader.py
│       ├── test_validator.py
│       ├── test_metrics.py
│       └── test_cli.py
├── parte_b/
│   ├── citybreak_app/
│   │   ├── exceptions.py
│   │   ├── loader.py
│   │   ├── validator.py
│   │   ├── metrics.py
│   │   └── cli.py
│   ├── data/
│   │   └── stravl_citybreak_subset.csv
│   └── tests/
│       ├── test_loader.py
│       ├── test_validator.py
│       ├── test_metrics.py
│       └── test_cli.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## 2. Parte A - Análisis de ventas

La Parte A utiliza un dataset de ventas proporcionado por el profesor.

1. Carga el archivo CSV mediante pandas.
2. Comprueba qué ventas son válidas e inválidas.
3. Separa las ventas válidas de las inválidas.
4. Calcula diferentes métricas utilizando únicamente las ventas válidas.
5. Muestra los resultados en la terminal.

### Reglas de validación

Una venta es válida cuando:

- Las unidades son numéricas, no nulas y mayores que 0.
- El precio unitario es numérico, no nulo y mayor que 0.

### Métricas calculadas

- Importe total de todas las ventas válidas.
- Importe total vendido por región.
- Importe total vendido por producto.

El importe de cada venta se calcula multiplicando las unidades por el precio unitario.

### Ejecución

Desde la raíz del proyecto:

```bash
uv run python -m parte_a.ventas_app.cli --input parte_a/data/ventas.csv
```

El programa muestra el número de ventas válidas e inválidas, junto con las métricas calculadas.

En el dataset proporcionado por el profesor hay 150 ventas:

- 140 ventas válidas.
- 10 ventas inválidas.

## 3. Parte B - Preferencias de destinos turísticos

La Parte B utiliza un dataset público de preferencias de viajes.

El objetivo es analizar qué destinos turísticos gustan a los usuarios a partir de sus valoraciones.

El programa sigue el mismo proceso que la Parte A:

1. Carga el archivo CSV.
2. Valida las valoraciones.
3. Separa los registros válidos e inválidos.
4. Calcula métricas sobre los registros válidos.
5. Muestra los resultados en la terminal.

### Dataset utilizado

**Nombre:** Stravl Travel Preference Dataset.

**Fuente:** https://github.com/Stravl/Stravl-Data

**Autor:** Stravl.

**Condiciones de uso:** El repositorio de origen permite utilizar los datos para fines académicos y comerciales. Se debe consultar la documentación original para conocer sus condiciones completas.

Para este proyecto se utiliza una muestra reducida del dataset original, almacenada en:

```text
parte_b/data/stravl_citybreak_subset.csv
```

La muestra contiene 12.005 registros y 16 columnas.

Entre las columnas utilizadas están:

- `user_id`: identificador del usuario.
- `destination_id`: identificador del destino.
- `destination`: nombre del destino turístico.
- `country`: país del destino.
- `swipe`: indica si al usuario le gusta el destino (`yes` o `no`).
- `liked`: representa la valoración mediante 1 o 0.

### Reglas de validación

Una valoración se considera válida cuando:

- `user_id` no es nulo ni está vacío.
- `destination_id` representa un número entero mayor o igual que 0.
- `destination` no es nulo ni está vacío.
- `country` no es nulo ni está vacío.
- `swipe` contiene únicamente `yes` o `no`.
- `liked` contiene únicamente 0 o 1.
- Existe coherencia entre `swipe` y `liked`.

La coherencia se comprueba de la siguiente manera:

- Si `swipe = yes`, entonces `liked = 1`.
- Si `swipe = no`, entonces `liked = 0`.

### Métricas calculadas

Se calculan tres métricas:

1. **Total de likes:** suma de todas las valoraciones positivas.
2. **Likes por país:** número de likes recibidos por los destinos de cada país.
3. **Likes por destino:** número de likes recibidos por cada destino turístico.

Las métricas se calculan utilizando únicamente los registros válidos.

### Ejecución

Desde la raíz del proyecto:

```bash
uv run python -m parte_b.citybreak_app.cli --input parte_b/data/stravl_citybreak_subset.csv
```

El programa muestra las valoraciones válidas e inválidas y las tres métricas calculadas.

## 4. Instalación de dependencias

El proyecto utiliza Python 3.12 o superior y uv para gestionar las dependencias.

Las principales librerías utilizadas son:

- pandas
- numpy
- pytest
- pytest-cov

Para instalar las dependencias, ejecutar desde la raíz del proyecto:

```bash
uv sync
```

Las dependencias están definidas en `pyproject.toml` y sus versiones se gestionan mediante `uv.lock`.

## 5. Tests con pytest

Se han creado tests para los cuatro módulos principales de cada parte:

- `loader.py`
- `validator.py`
- `metrics.py`
- `cli.py`

Los tests comprueban la carga de datos, la validación de registros, los cálculos de métricas y el funcionamiento del programa principal.

Se utilizan herramientas de pytest como:

- `assert`
- `pytest.raises`
- `pytest.mark.parametrize`
- `monkeypatch`
- `capsys`

También se incluye un test de integración que comprueba el funcionamiento conjunto de varios módulos.

### Ejecutar todos los tests

```bash
uv run python -m pytest -q
```

### Ejecutar únicamente los tests de la Parte A

```bash
uv run python -m pytest -q parte_a/tests/
```

### Ejecutar únicamente los tests de la Parte B

```bash
uv run python -m pytest -q parte_b/tests/
```

### Ejecutar los tests sin los de integración

```bash
uv run python -m pytest -q -m "not integration"
```

### Ejecutar únicamente los tests de integración

```bash
uv run python -m pytest -q -m integration
```

## 6. Cobertura de código

Se utiliza `pytest-cov` para medir el porcentaje de código ejecutado durante los tests.

El profesor exige una cobertura mínima del 60 %.

Para comprobar la cobertura de las dos partes:

```bash
uv run python -m pytest -q --cov=parte_a.ventas_app --cov=parte_b.citybreak_app --cov-report=term-missing --cov-fail-under=60
```

En la última ejecución se obtuvieron los siguientes resultados:

- **33 tests superados.**
- **90,18 % de cobertura total.**

Por tanto, se supera el mínimo de cobertura exigido.

## 7. Integración continua con GitHub Actions

El proyecto utiliza GitHub Actions para ejecutar automáticamente los tests.

La configuración se encuentra en:

```text
.github/workflows/ci.yml
```

El workflow está configurado para ejecutarse:

- Cuando se realiza un `push` a la rama `main`.
- Cuando se crea o actualiza un `pull_request`.

GitHub Actions realiza los siguientes pasos:

1. Descarga el código del repositorio.
2. Configura Python 3.12.
3. Instala uv.
4. Instala las dependencias del proyecto.
5. Ejecuta los tests de ambas partes.
6. Comprueba que la cobertura total sea al menos del 60 %.

