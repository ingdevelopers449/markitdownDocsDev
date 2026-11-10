# ⚡ Doc2Markdown Studio

> **Herramienta para desarrolladores y analistas**: Convierte documentos complejos (Excel `.xlsx`, Word `.docx`, PDF, PowerPoint `.pptx`, CSV) en Markdown (`.md`) limpio y optimizado, reduciendo significativamente el consumo de tokens y contexto al interactuar con modelos de IA (ChatGPT, Claude, Gemini, etc.).

---

## 🎯 ¿Por qué este proyecto?

Al subir archivos como hojas de cálculo de Excel (`.xlsx`) a una IA:

- La IA gasta una enorme cantidad de tokens procesando estilos, colores de celdas, fuentes, metadatos binarios y XML innecesarios.
- Las tablas en Excel generan ruido visual en el prompt.

**Doc2Markdown Studio** extrae el contenido semántico y lo estructura en formato Markdown nativo (tablas limpias, encabezados, listas), reduciendo el peso en más del **85%** y ahorrando cientos o miles de tokens en cada consulta.

---

## 🏗️ Arquitectura del Proyecto (Feature-First)

El software sigue estrictamente una arquitectura modular orientada a funcionalidades (**Feature-First**), aislando cada capacidad del sistema para facilitar su mantenimiento y escalabilidad:

```text
markitdown-studio/
├── main.py                          # Punto de entrada dual (GUI / CLI)
├── requirements.txt                 # Dependencias del proyecto
├── README.md                        # Documentación completa
├── tests/                           # Suite de pruebas unitarias
│   └── test_converter.py
└── src/
    ├── core/                        # Núcleo transversal compartido
    │   ├── __init__.py
    │   ├── config.py                # Configuración, rutas y extensiones soportadas
    │   ├── exceptions.py            # Jerarquía de excepciones de dominio
    │   └── utils.py                 # Estimación de tokens y formato de tamaños
    │
    └── features/                    # Módulos por Funcionalidad (Feature-First)
        ├── converter/               # [Feature 1] Motor de conversión a Markdown
        │   ├── __init__.py
        │   ├── models.py            # Modelos de solicitud y resultado
        │   └── service.py           # Servicio MarkItDown y saneamiento de texto
        │
        ├── batch/                   # [Feature 2] Procesamiento por lotes y carpetas
        │   ├── __init__.py
        │   └── service.py           # Ejecución concurrente multihilo
        │
        ├── history/                 # [Feature 3] Historial y auditoría de conversiones
        │   ├── __init__.py
        │   └── service.py           # Registro de métricas y persistencia local
        │
        ├── gui/                     # [Feature 4] Interfaz Gráfica de Usuario (CustomTkinter)
        │   ├── __init__.py
        │   └── views.py             # Ventana principal, previsualizador y métricas
        │
        └── cli/                     # [Feature 5] Línea de Comandos para desarrolladores
            ├── __init__.py
            └── runner.py            # Argumentos CLI y ejecución desde terminal
```

---

## 🚀 Instalación y Requisitos

1. Asegúrate de tener Python 3.10+ instalado.
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

---

## 💻 Modos de Uso

### 1. Interfaz Gráfica de Escritorio (Modo Recomendado)

Inicia la app moderna con soporte para modo oscuro:

```bash
python main.py
```

**Características de la GUI:**

- 📄 **Selección múltiple**: Carga múltiples archivos a la vez.
- 📁 **Conversión por carpeta**: Convierte todos los documentos de un directorio en lote.
- 📊 **Métricas en tiempo real**: Estima los tokens que consumirá la IA y el porcentaje de ahorro.
- 👁️ **Vista previa integrada**: Inspecciona el Markdown resultante directamente en la pantalla.
- 📋 **Botón de copiado rápido**: Copia el Markdown listo para pegarlo a tu IA favorita con un solo clic.
- 🕒 **Pestaña de Historial**: Revisa conversiones previas y su rendimiento.

### 2. Modo Terminal / CLI (Para Desarrolladores)

Convierte rápidamente archivos sin abrir la interfaz:

- **Convertir un archivo específico:**

  ```bash
  python main.py mi_historia_usuario.xlsx
  ```

  *(Genera `mi_historia_usuario.md` en el mismo directorio).*

- **Especificar ruta de salida:**

  ```bash
  python main.py historia.docx -o ./docs/historia.md
  ```

- **Convertir una carpeta completa por lotes:**

  ```bash
  python main.py ./historias_de_usuario/ -r
  ```

- **Ver formatos soportados:**

  ```bash
  python main.py --list-formats
  ```

---

## 📄 Formatos Compatibles

- **Hojas de Cálculo**: `.xlsx`, `.xls`, `.csv`
- **Documentos de Texto**: `.docx`, `.txt`, `.pdf`
- **Presentaciones**: `.pptx`
- **Estructurados**: `.json`, `.xml`, `.html`, `.htm`

---

## 🧪 Pruebas Unitarias

Ejecuta la suite de pruebas del proyecto:

```bash
python -m unittest tests/test_converter.py
```
