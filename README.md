# Sistema Inteligente de Gestión Documental y Priorización de Trámites Municipales con Machine Learning

Proyecto académico para el curso **Taller de Desarrollo de Aplicaciones con Machine Learning**.

## 1. Descripción del proyecto

Este proyecto implementa un prototipo web para la **Municipalidad Provincial de Yau**. La finalidad es registrar trámites administrativos, hacer seguimiento de expedientes y usar un modelo de **Machine Learning** para predecir el riesgo de retraso de cada trámite.

El sistema permite:

- Registrar ciudadanos.
- Registrar trámites municipales.
- Predecir riesgo de retraso: **Bajo, Medio o Alto**.
- Asignar prioridad automática.
- Cambiar estados del expediente.
- Simular notificaciones al ciudadano.
- Consultar reportes básicos por estado, área y riesgo.

---

## 2. Problema que resuelve

La municipalidad tiene problemas por el uso de procesos manuales:

- largas colas;
- pérdida de tiempo;
- errores en el registro;
- falta de seguimiento;
- poca transparencia;
- ciudadanos sin información clara sobre su expediente.

El sistema propuesto mejora ese proceso mediante una aplicación web con un modelo predictivo.

---

## 3. Tecnologías utilizadas

- Python 3.10 o superior.
- Flask.
- SQLite.
- Pandas.
- Scikit-learn.
- Joblib.
- HTML y CSS.

---

## 4. Estructura del proyecto

```text
proyecto_ml_municipalidad_yau/
│
├── app.py                         # Aplicación principal Flask
├── generar_dataset.py              # Genera datos ficticios de trámites
├── train_model.py                  # Entrena el modelo ML
├── requirements.txt                # Librerías necesarias
├── municipalidad_yau.db             # Se crea automáticamente al ejecutar
│
├── data/
│   └── tramites_historicos.csv      # Dataset ficticio
│
├── models/
│   └── modelo_riesgo_tramites.pkl   # Modelo entrenado
│
├── templates/
│   ├── layout.html
│   ├── index.html
│   ├── registrar.html
│   ├── detalle.html
│   └── reportes.html
│
├── static/
│   └── styles.css
│
└── docs/
    ├── arquitectura.md
    └── diagrama_flujo.md
```

---

## 5. Instalación paso a paso

### Paso 1: Descargar el proyecto

Descomprimir el archivo ZIP en una carpeta de trabajo.

### Paso 2: Abrir terminal

Ingresar a la carpeta del proyecto:

```bash
cd proyecto_ml_municipalidad_yau
```

### Paso 3: Crear entorno virtual

En Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

En macOS o Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 4: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 5: Generar dataset ficticio

```bash
python generar_dataset.py
```

### Paso 6: Entrenar el modelo de Machine Learning

```bash
python train_model.py
```

### Paso 7: Ejecutar la aplicación

```bash
python app.py
```

### Paso 8: Abrir el sistema

En el navegador ingresar a:

```text
http://127.0.0.1:5000
```

---

## 6. Explicación del modelo de Machine Learning

El modelo usa datos históricos ficticios para aprender qué características hacen que un trámite tenga mayor probabilidad de retrasarse.

### Variables de entrada

- tipo de trámite;
- área responsable;
- documentos completos;
- número de derivaciones;
- días transcurridos;
- carga del área.

### Variable de salida

- riesgo de retraso: Bajo, Medio o Alto.

### Algoritmo utilizado

Se usa **Random Forest Classifier** porque es un algoritmo de clasificación útil para predecir categorías. En este caso, clasifica el trámite según el nivel de riesgo.

---

## 7. Funcionamiento del sistema

### Registro de trámite

El usuario ingresa los datos del ciudadano y del trámite.

### Predicción automática

Cuando se guarda el trámite, el modelo analiza los datos y devuelve:

- riesgo de retraso;
- probabilidad de la predicción;
- prioridad de atención.

### Seguimiento

El personal puede cambiar el estado del trámite:

- Registrado;
- En revisión;
- Derivado;
- Observado;
- Aprobado;
- Rechazado;
- Finalizado.

### Reportes

El sistema muestra:

- total de trámites;
- trámites por riesgo;
- trámites por estado;
- trámites por área;
- trámites críticos.

---

## 8. Ejemplo de caso de prueba

Registrar un trámite con estos datos:

- Tipo: Permiso de construcción.
- Área: Obras privadas.
- Documentos completos: No.
- Número de derivaciones: 5.
- Días transcurridos: 18.
- Carga del área: Alta.

Resultado esperado:

- Riesgo: Alto.
- Prioridad: Alta.

---

## 9. Cómo explicar este proyecto en exposición

Una explicación breve sería:

> Este proyecto propone un sistema web inteligente para mejorar la gestión de trámites municipales. El sistema registra expedientes, permite hacer seguimiento y utiliza un modelo de Machine Learning para predecir si un trámite tiene riesgo bajo, medio o alto de retraso. Con esta predicción, la municipalidad puede priorizar trámites críticos, reducir tiempos de espera y mejorar la atención al ciudadano.

---

## 10. Mejoras futuras

El prototipo puede ampliarse con:

- inicio de sesión por roles;
- carga real de documentos PDF;
- notificaciones por correo o WhatsApp;
- integración con firma digital;
- dashboard con gráficos;
- conexión a PostgreSQL;
- despliegue en servidor;
- uso de datos reales de una municipalidad.

---

## 11. Recomendación para el estudiante

El código entregado es un punto de partida. El estudiante debe revisarlo, ejecutarlo, probarlo y personalizarlo. Se recomienda mejorar la interfaz, agregar más datos, incluir capturas de pantalla y explicar claramente cómo el modelo de Machine Learning ayuda a resolver el problema del caso práctico.
