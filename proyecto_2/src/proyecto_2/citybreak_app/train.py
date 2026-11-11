
import argparse
import json
import logging
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .loader import load_citybreaks, DATA_PATH
from .validator import validate_swipes
from .preprocessing import preprocess_forms, encode_forms
from .features import (
    prepare_features,
    PreferenceDestinationEncoder
)


# Configuración del logging
logger = logging.getLogger(__name__)

# Carpeta donde guardaremos el modelo
PROJECT_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_DIR / "models" / "model.joblib"


def split_by_user(df: pd.DataFrame):
    """
    Divide los datos en train, validation y test,
    evitando compartir usuarios entre conjuntos.
    """

    # Reservar el 15 % de los usuarios para test
    splitter_test = GroupShuffleSplit(
        n_splits=1,
        test_size=0.15,
        random_state=42
    )

    train_val_idx, test_idx = next(
        splitter_test.split(df, groups=df["user_id"])
    )

    train_val = df.iloc[train_val_idx].copy()
    test = df.iloc[test_idx].copy()

    # Reservar el 15 % del total para validación
    splitter_val = GroupShuffleSplit(
        n_splits=1,
        test_size=0.15 / 0.85,
        random_state=43
    )

    train_idx, val_idx = next(
        splitter_val.split(
            train_val,
            groups=train_val["user_id"]
        )
    )

    train = train_val.iloc[train_idx].copy()
    validation = train_val.iloc[val_idx].copy()

    return train, validation, test


def transform_data(df: pd.DataFrame):
    """
    Prepara las variables X e Y utilizando
    los módulos desarrollados anteriormente.
    """

    df = preprocess_forms(df)
    df = encode_forms(df)

    X, y, _ = prepare_features(df)

    return X, y



def build_pipeline(classifier=None, use_interactions=False):
    """
    Construye un pipeline de scikit-learn.

    Permite utilizar el preprocesamiento original
    o uno con interacciones entre preferencias y destinos.
    """

    if classifier is None:
        classifier = LogisticRegression(
            max_iter=1000,
            random_state=42
        )

    if use_interactions:

        # Preprocesamiento con interacciones
        preprocessor = PreferenceDestinationEncoder()

    else:

        # Preprocesamiento original
        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "categorical",
                    OneHotEncoder(handle_unknown="ignore"),
                    ["destination_id", "country"]
                )
            ],
            remainder="passthrough"
        )

    pipeline = Pipeline(
        steps=[
            ("preprocessing", preprocessor),
            ("classifier", classifier)
        ]
    )

    return pipeline


def evaluate_model(model, X, y):
    """
    Evalúa el modelo mediante métricas de clasificación
    y de discriminación de probabilidades.
    """

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]

    return {
        "accuracy": float(
            accuracy_score(y, predictions)
        ),
        "precision": float(
            precision_score(y, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y, predictions, zero_division=0)
        ),
        "f1": float(
            f1_score(y, predictions, zero_division=0)
        ),
        "roc_auc": float(
            roc_auc_score(y, probabilities)
        ),
        "average_precision": float(
            average_precision_score(y, probabilities)
        )
    }


def compare_models(X_train, y_train, X_val, y_val):
    """
    Entrena varios modelos y compara su rendimiento
    utilizando exclusivamente el conjunto de validación.

    Devuelve el mejor modelo y los resultados de todos.
    """

    
    models = {
        "DummyClassifier": (
            DummyClassifier(strategy="most_frequent"),
            False
        ),

        "LogisticRegression": (
            LogisticRegression(
                max_iter=1000,
                random_state=42
            ),
            False
        ),

        "RandomForest": (
            RandomForestClassifier(
                n_estimators=200,
                min_samples_leaf=3,
                random_state=42,
                n_jobs=-1
            ),
            False
        ),

        "ExtraTrees": (
            ExtraTreesClassifier(
                n_estimators=200,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            False
        ),

        "LogisticInteractions": (
            LogisticRegression(
                C=0.03,
                max_iter=1000,
                random_state=42
            ),
            True
        )
    }


    results = {}

    best_model = None
    best_name = None
    best_score = -1.0

    for name, (classifier, use_interactions) in models.items():

        logger.info("Entrenando modelo: %s", name)

        # Construir y entrenar el pipeline
        pipeline = build_pipeline(
            classifier,
            use_interactions=use_interactions
        )
        pipeline.fit(X_train, y_train)

        # Evaluar en validación
        metrics = evaluate_model(pipeline, X_val, y_val)

        results[name] = metrics

        logger.info(
            "%s | Accuracy=%.4f | F1=%.4f | ROC-AUC=%.4f | AP=%.4f",
            name,
            metrics["accuracy"],
            metrics["f1"],
            metrics["roc_auc"],
            metrics["average_precision"]
        )

        # El DummyClassifier solo sirve como referencia
        if name == "DummyClassifier":
            continue

        # Seleccionar el modelo con mejor ROC-AUC
        if metrics["roc_auc"] > best_score:
            best_score = metrics["roc_auc"]
            best_model = pipeline
            best_name = name

    logger.info(
        "Mejor modelo: %s | ROC-AUC validacion=%.4f",
        best_name,
        best_score
    )

    return best_model, best_name, results


def main(argv=None):
    """
    Ejecuta el proceso completo de entrenamiento,
    comparación, evaluación y almacenamiento.
    """

    parser = argparse.ArgumentParser(
        description="Entrenar y comparar modelos de CityBreak App"
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DATA_PATH,
        help="Ruta del CSV de Stravl"
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=MODEL_PATH,
        help="Ruta donde guardar el modelo seleccionado"
    )

    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s"
    )

    # 1. Cargar y validar
    logger.info("Iniciando entrenamiento de CityBreak App")

    df = load_citybreaks(args.input)

    logger.info("Registros cargados: %d", len(df))

    valid, invalid = validate_swipes(df)

    logger.info("Registros validos: %d", len(valid))
    logger.info("Registros invalidos: %d", len(invalid))

    if valid.empty:
        raise ValueError(
            "No hay registros validos para entrenar"
        )

    # 2. Dividir los datos por usuarios
    train, validation, test = split_by_user(valid)

    logger.info(
        "Division: train=%d, validation=%d, test=%d",
        len(train),
        len(validation),
        len(test)
    )

    # Comprobar que no hay usuarios compartidos
    train_users = set(train["user_id"])
    val_users = set(validation["user_id"])
    test_users = set(test["user_id"])

    if not (
        train_users.isdisjoint(val_users)
        and train_users.isdisjoint(test_users)
        and val_users.isdisjoint(test_users)
    ):
        raise ValueError(
            "Hay usuarios compartidos entre los conjuntos"
        )

    # 3. Preparar X e Y
    X_train, y_train = transform_data(train)
    X_val, y_val = transform_data(validation)
    X_test, y_test = transform_data(test)

    # Comprobar las clases disponibles
    for name, y_data in [
        ("train", y_train),
        ("validation", y_val),
        ("test", y_test)
    ]:
        if y_data.nunique() < 2:
            raise ValueError(
                f"El conjunto {name} necesita las dos clases de liked"
            )

    # 4. Entrenar y comparar modelos
    best_model, best_name, results = compare_models(
        X_train,
        y_train,
        X_val,
        y_val
    )

    # 5. Evaluar el mejor modelo en test
    logger.info(
        "Evaluando %s en el conjunto de test",
        best_name
    )

    test_metrics = evaluate_model(
        best_model,
        X_test,
        y_test
    )

    logger.info(
        "Resultados finales de test: %s",
        test_metrics
    )

    # 6. Guardar el mejor modelo
    args.output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(best_model, args.output)

    logger.info(
        "Modelo guardado en: %s",
        args.output
    )

    # 7. Guardar las métricas
    metrics_path = args.output.parent / "metrics.json"

    report = {
        "selection_metric": "roc_auc",
        "best_model": best_name,
        "validation_comparison": results,
        "test": test_metrics,
        "dataset": {
            "total_rows": len(df),
            "valid_rows": len(valid),
            "invalid_rows": len(invalid),
            "train_rows": len(train),
            "validation_rows": len(validation),
            "test_rows": len(test)
        }
    }

    with metrics_path.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4
        )

    logger.info(
        "Metricas guardadas en: %s",
        metrics_path
    )


if __name__ == "__main__":
    main()
