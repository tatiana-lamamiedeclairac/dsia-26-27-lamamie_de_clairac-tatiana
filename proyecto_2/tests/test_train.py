
import joblib
import pandas as pd
import pytest

from proyecto_2.citybreak_app.train import (
    split_by_user,
    build_pipeline
)


# Datos de prueba creados en memoria
@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "user_id": [
            f"user_{i}"
            for i in range(12)
            for _ in range(2)
        ],
        "liked": [0, 1] * 12
    })


# Comprobar que los usuarios no se mezclan
def test_split_by_user(sample_df):

    # Arrange
    df = sample_df

    # Act
    train, val, test = split_by_user(df)

    # Assert
    assert len(train) + len(val) + len(test) == len(df)

    train_users = set(train["user_id"])
    val_users = set(val["user_id"])
    test_users = set(test["user_id"])

    assert train_users.isdisjoint(val_users)
    assert train_users.isdisjoint(test_users)
    assert val_users.isdisjoint(test_users)


# Comprobar que el modelo se puede guardar y cargar
def test_model_save_and_load(tmp_path):

    # Arrange
    X = pd.DataFrame({
        "destination_id": ["1", "2", "1", "2"] * 3,
        "country": ["Spain", "Italy", "Spain", "Italy"] * 3,
        "form_a_0": [1, 0, 1, 0] * 3
    })

    y = [1, 0, 1, 0] * 3

    model = build_pipeline()

    # Act
    model.fit(X, y)

    model_path = tmp_path / "model.joblib"
    joblib.dump(model, model_path)

    loaded_model = joblib.load(model_path)
    probabilities = loaded_model.predict_proba(X)

    # Assert
    assert model_path.exists()
    assert probabilities.shape == (len(X), 2)
    assert (probabilities >= 0).all()
    assert (probabilities <= 1).all()
