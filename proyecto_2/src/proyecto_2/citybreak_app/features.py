
import pandas as pd

from scipy import sparse
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder


def build_predictors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara las variables predictoras X.

    Se utiliza tanto para entrenamiento como para inferencia.
    """

    # Columnas del cuestionario ya codificadas
    form_columns = [
        col for col in df.columns
        if col.startswith("form_")
    ]

    # Comprobar que las preferencias sean numéricas
    for col in form_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(
                f"La columna {col} todavía no es numérica."
            )

    # Seleccionar preferencias y características del destino
    X = df[
        form_columns + ["destination_id", "country"]
    ].copy()

    # El identificador del destino es una categoría
    X["destination_id"] = X["destination_id"].astype(str)

    return X


def prepare_features(df: pd.DataFrame):
    """
    Prepara X, y y los identificadores de usuario
    para el entrenamiento del modelo.
    """

    X = build_predictors(df)

    y = df["liked"].astype(int).copy()

    groups = df["user_id"].copy()

    return X, y, groups




class PreferenceDestinationEncoder(BaseEstimator, TransformerMixin):
    """
    Codifica las preferencias, los destinos y los países,
    e incorpora interacciones para personalizar las predicciones.
    """

    def fit(self, X, y=None):

        # Identificar las características del cuestionario
        self.form_columns_ = [
            col for col in X.columns
            if col.startswith("form_")
        ]

        # Aprender las categorías presentes en entrenamiento
        self.destination_encoder_ = OneHotEncoder(
            handle_unknown="ignore"
        )

        self.country_encoder_ = OneHotEncoder(
            handle_unknown="ignore"
        )

        self.destination_encoder_.fit(X[["destination_id"]])
        self.country_encoder_.fit(X[["country"]])

        return self

    def transform(self, X):

        # Características numéricas del cuestionario
        preferences = X[self.form_columns_].to_numpy(
            dtype=float
        )

        # Codificar destinos y países
        destinations = self.destination_encoder_.transform(
            X[["destination_id"]]
        )

        countries = self.country_encoder_.transform(
            X[["country"]]
        )

        # Interacciones entre preferencias y países
        country_interactions = sparse.hstack(
            [
                countries.multiply(preferences[:, i:i+1])
                for i in range(preferences.shape[1])
            ],
            format="csr"
        )

        # Interacciones entre preferencias y destinos
        destination_interactions = sparse.hstack(
            [
                destinations.multiply(preferences[:, i:i+1])
                for i in range(preferences.shape[1])
            ],
            format="csr"
        )

        # Unir todas las características
        X_encoded = sparse.hstack(
            [
                sparse.csr_matrix(preferences),
                destinations,
                countries,
                country_interactions,
                destination_interactions
            ],
            format="csr"
        )

        return X_encoded
