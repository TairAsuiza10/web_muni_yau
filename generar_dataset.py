"""
Genera un dataset ficticio de trámites municipales para entrenar un modelo
que predice el riesgo de retraso: Bajo, Medio o Alto.

Uso:
    python generar_dataset.py
"""

from __future__ import annotations

import random
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "tramites_historicos.csv"

TIPOS_TRAMITE = [
    "Licencia de funcionamiento",
    "Permiso de construccion",
    "Constancia de posesion",
    "Certificado de residencia",
    "Reclamo ciudadano",
    "Acceso a informacion publica",
    "Pago de arbitrios",
    "Permiso para evento",
]

AREAS = [
    "Mesa de partes",
    "Desarrollo economico",
    "Obras privadas",
    "Catastro",
    "Atencion al ciudadano",
    "Asesoria legal",
]

CARGAS = ["Baja", "Media", "Alta"]


def calcular_riesgo(tipo: str, documentos: str, derivaciones: int, dias: int, carga: str) -> str:
    """Regla simulada para crear la etiqueta del dataset."""
    puntaje = 0

    if documentos == "No":
        puntaje += 3
    if derivaciones >= 4:
        puntaje += 2
    if dias >= 12:
        puntaje += 3
    elif dias >= 7:
        puntaje += 1
    if carga == "Alta":
        puntaje += 2
    elif carga == "Media":
        puntaje += 1
    if tipo in ["Permiso de construccion", "Licencia de funcionamiento", "Constancia de posesion"]:
        puntaje += 2
    if tipo == "Certificado de residencia":
        puntaje -= 1

    if puntaje >= 7:
        return "Alto"
    if puntaje >= 4:
        return "Medio"
    return "Bajo"


def generar_dataset(n: int = 350, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    filas = []

    for i in range(1, n + 1):
        tipo = random.choice(TIPOS_TRAMITE)
        area = random.choice(AREAS)
        documentos = random.choices(["Si", "No"], weights=[70, 30])[0]
        derivaciones = random.randint(1, 6)
        carga = random.choices(CARGAS, weights=[30, 45, 25])[0]

        base_dias = {
            "Certificado de residencia": 2,
            "Pago de arbitrios": 2,
            "Reclamo ciudadano": 4,
            "Acceso a informacion publica": 6,
            "Permiso para evento": 5,
            "Constancia de posesion": 8,
            "Licencia de funcionamiento": 10,
            "Permiso de construccion": 15,
        }[tipo]

        dias = base_dias + random.randint(0, 8)
        if documentos == "No":
            dias += random.randint(3, 8)
        if carga == "Alta":
            dias += random.randint(2, 6)
        if derivaciones >= 4:
            dias += random.randint(1, 5)

        riesgo = calcular_riesgo(tipo, documentos, derivaciones, dias, carga)

        filas.append(
            {
                "id_historico": i,
                "tipo_tramite": tipo,
                "area": area,
                "documentos_completos": documentos,
                "num_derivaciones": derivaciones,
                "dias_transcurridos": dias,
                "carga_area": carga,
                "riesgo_retraso": riesgo,
            }
        )

    return pd.DataFrame(filas)


if __name__ == "__main__":
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = generar_dataset()
    df.to_csv(DATA_PATH, index=False, encoding="utf-8")
    print(f"Dataset generado correctamente: {DATA_PATH}")
    print(df.head())
