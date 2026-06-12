"""
Entrena el modelo de Machine Learning para predecir riesgo de retraso.

Uso:
    python generar_dataset.py
    python train_model.py
"""

from __future__ import annotations

from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "tramites_historicos.csv"
MODEL_PATH = BASE_DIR / "models" / "modelo_riesgo_tramites.pkl"

FEATURES = [
    "tipo_tramite",
    "area",
    "documentos_completos",
    "num_derivaciones",
    "dias_transcurridos",
    "carga_area",
]
TARGET = "riesgo_retraso"

CATEGORICAL_FEATURES = ["tipo_tramite", "area", "documentos_completos", "carga_area"]
NUMERIC_FEATURES = ["num_derivaciones", "dias_transcurridos"]


def entrenar_modelo() -> Pipeline:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "No existe data/tramites_historicos.csv. Primero ejecuta: python generar_dataset.py"
        )

    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES]
    y = df[TARGET]

    preprocesador = ColumnTransformer(
        transformers=[
            ("categoricas", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ("numericas", "passthrough", NUMERIC_FEATURES),
        ]
    )

    modelo = RandomForestClassifier(
        n_estimators=120,
        max_depth=8,
        random_state=42,
        class_weight="balanced",
    )

    pipeline = Pipeline(
        steps=[
            ("preprocesador", preprocesador),
            ("modelo", modelo),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    print("Accuracy:", round(accuracy_score(y_test, y_pred), 4))
    print("\nMatriz de confusión:")
    print(confusion_matrix(y_test, y_pred))
    print("\nReporte de clasificación:")
    print(classification_report(y_test, y_pred))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Modelo guardado en: {MODEL_PATH}")

    return pipeline


if __name__ == "__main__":
    entrenar_modelo()
