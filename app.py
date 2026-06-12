"""
Sistema inteligente de gestión documental y priorización de trámites municipales.

Proyecto académico para el curso Taller de Desarrollo de Aplicaciones con Machine Learning.

Ejecución:
    python generar_dataset.py
    python train_model.py
    python app.py

Luego abrir:
    http://127.0.0.1:5000
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from flask import Flask, flash, redirect, render_template, request, url_for

from generar_dataset import generar_dataset
from train_model import entrenar_modelo

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "municipalidad_yau.db"
MODEL_PATH = BASE_DIR / "models" / "modelo_riesgo_tramites.pkl"
DATA_PATH = BASE_DIR / "data" / "tramites_historicos.csv"

app = Flask(__name__)
app.secret_key = "cambiar-esta-clave-en-produccion"

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
ESTADOS = ["Registrado", "En revision", "Derivado", "Observado", "Aprobado", "Rechazado", "Finalizado"]


def conectar_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_db() -> None:
    """Crea las tablas principales si todavía no existen."""
    with conectar_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ciudadanos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dni TEXT NOT NULL UNIQUE,
                nombres TEXT NOT NULL,
                telefono TEXT,
                correo TEXT,
                direccion TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tramites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL UNIQUE,
                ciudadano_id INTEGER NOT NULL,
                tipo_tramite TEXT NOT NULL,
                area TEXT NOT NULL,
                documentos_completos TEXT NOT NULL,
                num_derivaciones INTEGER NOT NULL,
                dias_transcurridos INTEGER NOT NULL,
                carga_area TEXT NOT NULL,
                riesgo_retraso TEXT NOT NULL,
                probabilidad REAL NOT NULL,
                prioridad TEXT NOT NULL,
                estado TEXT NOT NULL,
                observaciones TEXT,
                fecha_registro TEXT NOT NULL,
                FOREIGN KEY (ciudadano_id) REFERENCES ciudadanos(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tramite_id INTEGER NOT NULL,
                estado_anterior TEXT,
                estado_nuevo TEXT NOT NULL,
                comentario TEXT,
                fecha TEXT NOT NULL,
                FOREIGN KEY (tramite_id) REFERENCES tramites(id)
            )
            """
        )
        conn.commit()


def asegurar_modelo():
    """Carga el modelo. Si no existe, crea dataset y entrena automáticamente."""
    if not DATA_PATH.exists():
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        generar_dataset().to_csv(DATA_PATH, index=False, encoding="utf-8")
    if not MODEL_PATH.exists():
        entrenar_modelo()
    return joblib.load(MODEL_PATH)


modelo_ml = None


def obtener_modelo():
    global modelo_ml
    if modelo_ml is None:
        modelo_ml = asegurar_modelo()
    return modelo_ml


def predecir_riesgo(datos: dict[str, Any]) -> tuple[str, float]:
    """Predice el riesgo de retraso usando el modelo entrenado."""
    modelo = obtener_modelo()
    entrada = pd.DataFrame(
        [
            {
                "tipo_tramite": datos["tipo_tramite"],
                "area": datos["area"],
                "documentos_completos": datos["documentos_completos"],
                "num_derivaciones": int(datos["num_derivaciones"]),
                "dias_transcurridos": int(datos["dias_transcurridos"]),
                "carga_area": datos["carga_area"],
            }
        ]
    )

    riesgo = str(modelo.predict(entrada)[0])
    probabilidad = 0.0

    if hasattr(modelo, "predict_proba"):
        clases = list(modelo.classes_)
        probabilidades = modelo.predict_proba(entrada)[0]
        probabilidad = float(probabilidades[clases.index(riesgo)])

    return riesgo, probabilidad


def prioridad_desde_riesgo(riesgo: str) -> str:
    return {"Alto": "Alta", "Medio": "Media", "Bajo": "Baja"}.get(riesgo, "Media")


def crear_codigo_expediente() -> str:
    fecha = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"YAU-{fecha}"


@app.route("/")
def index():
    with conectar_db() as conn:
        tramites = conn.execute(
            """
            SELECT t.*, c.dni, c.nombres
            FROM tramites t
            JOIN ciudadanos c ON c.id = t.ciudadano_id
            ORDER BY t.id DESC
            """
        ).fetchall()
    return render_template("index.html", tramites=tramites)


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        dni = request.form.get("dni", "").strip()
        nombres = request.form.get("nombres", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()
        direccion = request.form.get("direccion", "").strip()

        datos_tramite = {
            "tipo_tramite": request.form.get("tipo_tramite"),
            "area": request.form.get("area"),
            "documentos_completos": request.form.get("documentos_completos"),
            "num_derivaciones": request.form.get("num_derivaciones", 1),
            "dias_transcurridos": request.form.get("dias_transcurridos", 1),
            "carga_area": request.form.get("carga_area"),
        }

        if not dni or not nombres:
            flash("Debe ingresar DNI y nombres del ciudadano.", "error")
            return redirect(url_for("registrar"))

        riesgo, probabilidad = predecir_riesgo(datos_tramite)
        prioridad = prioridad_desde_riesgo(riesgo)
        codigo = crear_codigo_expediente()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with conectar_db() as conn:
            ciudadano = conn.execute("SELECT id FROM ciudadanos WHERE dni = ?", (dni,)).fetchone()
            if ciudadano:
                ciudadano_id = ciudadano["id"]
                conn.execute(
                    """
                    UPDATE ciudadanos
                    SET nombres = ?, telefono = ?, correo = ?, direccion = ?
                    WHERE id = ?
                    """,
                    (nombres, telefono, correo, direccion, ciudadano_id),
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO ciudadanos (dni, nombres, telefono, correo, direccion)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (dni, nombres, telefono, correo, direccion),
                )
                ciudadano_id = cursor.lastrowid

            cursor = conn.execute(
                """
                INSERT INTO tramites (
                    codigo, ciudadano_id, tipo_tramite, area, documentos_completos,
                    num_derivaciones, dias_transcurridos, carga_area, riesgo_retraso,
                    probabilidad, prioridad, estado, observaciones, fecha_registro
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    codigo,
                    ciudadano_id,
                    datos_tramite["tipo_tramite"],
                    datos_tramite["area"],
                    datos_tramite["documentos_completos"],
                    int(datos_tramite["num_derivaciones"]),
                    int(datos_tramite["dias_transcurridos"]),
                    datos_tramite["carga_area"],
                    riesgo,
                    probabilidad,
                    prioridad,
                    "Registrado",
                    "Trámite registrado y evaluado automáticamente por el modelo ML.",
                    fecha,
                ),
            )
            tramite_id = cursor.lastrowid
            conn.execute(
                """
                INSERT INTO historial (tramite_id, estado_anterior, estado_nuevo, comentario, fecha)
                VALUES (?, ?, ?, ?, ?)
                """,
                (tramite_id, None, "Registrado", "Registro inicial del trámite.", fecha),
            )
            conn.commit()

        flash(f"Trámite registrado. Riesgo: {riesgo}. Prioridad: {prioridad}.", "success")
        return redirect(url_for("detalle_tramite", tramite_id=tramite_id))

    return render_template(
        "registrar.html",
        tipos_tramite=TIPOS_TRAMITE,
        areas=AREAS,
        cargas=CARGAS,
    )


@app.route("/tramite/<int:tramite_id>")
def detalle_tramite(tramite_id: int):
    with conectar_db() as conn:
        tramite = conn.execute(
            """
            SELECT t.*, c.dni, c.nombres, c.telefono, c.correo, c.direccion
            FROM tramites t
            JOIN ciudadanos c ON c.id = t.ciudadano_id
            WHERE t.id = ?
            """,
            (tramite_id,),
        ).fetchone()
        historial = conn.execute(
            "SELECT * FROM historial WHERE tramite_id = ? ORDER BY id DESC",
            (tramite_id,),
        ).fetchall()

    if not tramite:
        flash("Trámite no encontrado.", "error")
        return redirect(url_for("index"))

    return render_template("detalle.html", tramite=tramite, historial=historial, estados=ESTADOS)


@app.route("/tramite/<int:tramite_id>/estado", methods=["POST"])
def cambiar_estado(tramite_id: int):
    nuevo_estado = request.form.get("estado")
    comentario = request.form.get("comentario", "").strip()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with conectar_db() as conn:
        tramite = conn.execute("SELECT estado FROM tramites WHERE id = ?", (tramite_id,)).fetchone()
        if not tramite:
            flash("Trámite no encontrado.", "error")
            return redirect(url_for("index"))

        estado_anterior = tramite["estado"]
        conn.execute(
            "UPDATE tramites SET estado = ?, observaciones = ? WHERE id = ?",
            (nuevo_estado, comentario, tramite_id),
        )
        conn.execute(
            """
            INSERT INTO historial (tramite_id, estado_anterior, estado_nuevo, comentario, fecha)
            VALUES (?, ?, ?, ?, ?)
            """,
            (tramite_id, estado_anterior, nuevo_estado, comentario, fecha),
        )
        conn.commit()

    flash("Estado actualizado. Se simuló la notificación al ciudadano.", "success")
    return redirect(url_for("detalle_tramite", tramite_id=tramite_id))


@app.route("/reportes")
def reportes():
    with conectar_db() as conn:
        total = conn.execute("SELECT COUNT(*) AS total FROM tramites").fetchone()["total"]
        por_riesgo = conn.execute(
            "SELECT riesgo_retraso, COUNT(*) AS total FROM tramites GROUP BY riesgo_retraso"
        ).fetchall()
        por_estado = conn.execute(
            "SELECT estado, COUNT(*) AS total FROM tramites GROUP BY estado"
        ).fetchall()
        por_area = conn.execute(
            "SELECT area, COUNT(*) AS total FROM tramites GROUP BY area ORDER BY total DESC"
        ).fetchall()
        criticos = conn.execute(
            """
            SELECT t.*, c.nombres
            FROM tramites t
            JOIN ciudadanos c ON c.id = t.ciudadano_id
            WHERE riesgo_retraso = 'Alto'
            ORDER BY probabilidad DESC
            LIMIT 10
            """
        ).fetchall()

    return render_template(
        "reportes.html",
        total=total,
        por_riesgo=por_riesgo,
        por_estado=por_estado,
        por_area=por_area,
        criticos=criticos,
    )


if __name__ == "__main__":
    inicializar_db()
    asegurar_modelo()
    app.run(debug=True)
