# ⚡ Doc2Markdown Studio

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://microsoft.com)

> **Convierte documentos pesados (Excel, Word, PDF, PowerPoint) a Markdown (.md) limpio con un solo clic.**  
> Diseñado para que **cualquier persona** (analistas, estudiantes, investigadores, docentes y programadores) ahorre miles de tokens y dinero al interactuar con Inteligencias Artificiales como ChatGPT, Claude, DeepSeek o Gemini.

---

## 💡 ¿Por qué esta herramienta es imprescindible para ti?

Cuando subes un archivo tradicional de **Excel (`.xlsx`, `.xls`)**, **Word (`.docx`)** o **PDF** a una IA:

- **Desperdicio masivo de tokens**: El 85% al 90% de la información de esos archivos corresponde a colores de celdas, fuentes, estilos visuales, márgenes y código XML binario interno que la IA no necesita para entender tus datos.
- **Límites de contexto agotados**: Si tu archivo es grande, la IA se satura rápidamente o empieza a olvidar partes de tu conversación.
- **Costos innecesarios**: Si usas APIs de IA de pago, estás pagando por estilos visuales en lugar de contenido real.

### ✨ La Solución: Doc2Markdown Studio

Esta herramienta extrae únicamente la información valiosa y la transforma en **Markdown puro (`.md`)**:
tablas limpias, encabezados y listas legibles.

| Métrica | Archivo Original (Excel / Word) | Convertido a Markdown (.md) | Ahorro |
| :--- | :--- | :--- | :--- |
| **Tamaño de archivo** | ~30 KB - 500 KB | ~1 KB - 15 KB | **> 85% de reducción** |
| **Tokens consumidos en IA** | Miles de tokens gastados | Solo los datos necesarios | **Ahorro de hasta un 90%** |
| **Comprensión de la IA** | Distraída con formato | **100% enfocada en el contenido** | **Respuestas más precisas** |

---

## 👥 ¿A quién le sirve esta aplicación?

- 📊 **Analistas de Negocio y Producto**: Convierte reportes y matrices de requerimientos para pedirle a la IA análisis estadísticos o resúmenes sin sobrecargar el chat.
- 📋 **Scrum Masters y Product Owners**: Sube historias de usuario o épicas en segundos sin basura visual.
- 🎓 **Estudiantes e Investigadores**: Extrae tablas de artículos PDF o diapositivas para que la IA elabore mapas conceptuales o fichas de estudio.
- 💻 **Desarrolladores**: Limpia documentación técnica y acelera la integración de prompts en sus sistemas.
- 🏢 **Equipos de Oficina y Administración**: Pasa planillas de asistencia, inventarios o cotizaciones a texto amigable para cualquier modelo LLM.

---

## 🚀 ¿Cómo instalar y usar el programa (`.exe`)?

No necesitas saber de programación ni tener Python instalado en tu computadora.

### Paso 1: Ejecutar la aplicación

1. Dirígete a la carpeta `dist/` de este proyecto (o descárgate el archivo ejecutable compartido por el autor).
2. Haz doble clic sobre **`Doc2Markdown.exe`**.
3. Se abrirá inmediatamente la ventana moderna con soporte para modo oscuro.

### Paso 2: Convertir documentos en segundos

1. **Seleccionar archivos**:
   - Pulsa el botón **`📄 Seleccionar Archivo(s)`** para elegir cualquier documento desde tus carpetas (Descargas, Escritorio, etc.).
   - O simplemente **arrastra tu archivo desde el Explorador de Windows y suéltalo** en la ventana del programa.
   - También puedes convertir una carpeta completa usando **`📁 Seleccionar Carpeta`**.
2. **Convertir**:
   - Pulsa el botón verde **`🚀 CONVERTIR A .MD`**.
3. **Usar el resultado**:
   - En la pestaña **Vista Previa**, verás tu archivo convertido a texto limpio.
   - Haz clic en **`📋 Copiar al Portapapeles`** y pégalo directamente en ChatGPT, Claude o Gemini.
   - O pulsa **`📂 Abrir Carpeta del Archivo`** para ubicar el archivo `.md` generado en tu equipo.

---

## 🛠️ Para Desarrolladores (Ejecutar desde el Código Fuente)

Si deseas inspeccionar el código o contribuir al desarrollo:

```bash
# 1. Clonar el repositorio
git clone https://github.com/ingdevelopers449/markitdownDocsDev.git
cd markitdownDocsDev

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar la interfaz gráfica
python main.py

# O ejecutar mediante la terminal (CLI)
python main.py ruta/a/tu_archivo.xlsx
```

### Ejecución de Pruebas Automatizadas

```bash
python -m unittest discover tests
```

---

## 🏗️ Arquitectura del Software (Feature-First)

El proyecto sigue una estructura limpia modular por funcionalidades (**Feature-First**):

```text
markitdown-studio/
├── main.py                          # Punto de entrada de la aplicación
├── requirements.txt                 # Dependencias del proyecto
├── README.md                        # Documentación para usuarios y desarrolladores
├── LICENSE                          # Licencia con atribución obligatoria
├── tests/                           # Suite de pruebas automatizadas
│   └── test_converter.py
└── src/
    ├── core/                        # Configuración global y estimador de tokens
    └── features/                    # Módulos aislados por funcionalidad
        ├── converter/               # Motor de conversión y Auto-Sniffer inteligente
        ├── batch/                   # Procesamiento multihilo por lotes y carpetas
        ├── history/                 # Historial y auditoría de métricas de ahorro
        ├── gui/                     # Interfaz Gráfica interactiva (CustomTkinter + Drag&Drop)
        └── cli/                     # Modo consola para terminal
```

---

## 📄 Formatos Compatibles

- **Hojas de cálculo**: `.xlsx`, `.xls` (antiguos y modernos), `.csv`
- **Documentos de texto**: `.docx`, `.pdf`, `.txt`
- **Presentaciones**: `.pptx`
- **Estructurados y web**: `.html`, `.htm`, `.json`, `.xml`

---

## ⚖️ Licencia y Créditos de Autoría

Este proyecto está publicado bajo la licencia **MIT**.

> [!IMPORTANT]
> **Atribución Requerida**: Cualquier persona u organización que clone, bifurque (*fork*), redistribuya o reutilice el código fuente de este proyecto **debe conservar de manera visible los créditos correspondientes a su autor original (ingdeveloper449)** y el archivo [`LICENSE`](LICENSE) intacto.
