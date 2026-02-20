# 🏛️ Simulador DGSC — Costa Rica

<div align="center">

![Estado](https://img.shields.io/badge/estado-activo-success.svg)
![Licencia MIT](https://img.shields.io/badge/licencia-MIT-blue.svg)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.32+-red.svg)
![Preguntas](https://img.shields.io/badge/preguntas-380-brightgreen.svg)
![Versión](https://img.shields.io/badge/versión-2.0-orange.svg)

**Herramienta de estudio interactiva para aspirantes a puestos de dirección en el Servicio Civil de Costa Rica**

[📱 Demo en Vivo](#) · [📚 Documentación](#contenido-académico) · [🤝 Contribuir](CONTRIBUTING.md) · [⚖️ Disclaimer](DISCLAIMER.md)

</div>

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción-del-proyecto)
- [Novedades v2.0](#-novedades-en-v20)
- [Características](#-características)
- [Tecnologías](#-tecnologías-utilizadas)
- [Instalación](#-instalación-local)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Contenido Académico](#-contenido-académico)
- [Roadmap](#-roadmap)
- [Contribuciones](#-contribuciones)
- [Licencia](#-licencia)
- [Disclaimer](#-disclaimer-legal)
- [Contacto](#-contacto)

---

## 📖 Descripción del Proyecto

**Simulador DGSC** es una aplicación web interactiva de código abierto diseñada para facilitar el estudio y preparación de aspirantes a puestos de dirección pública en Costa Rica. Con **380 preguntas** distribuidas en 8 temas, cubre íntegramente el contenido del *Manual de Orientación para el Ingreso y Ejercicio de Puestos de Dirección Pública* (DGSC, versión 1, enero 2019).

La versión 2.0 añade un **Modo Examen Real** con cronómetro, navegación avanzada, historial persistente de sesiones y análisis de resultados por tema — replicando las condiciones del examen oficial.

### 🎯 Objetivos Académicos

- Aplicar principios de desarrollo de software educativo (EdTech) con Python
- Demostrar implementación de bases de datos relacionales (SQLite) en aplicaciones interactivas
- Contribuir al acceso libre al conocimiento sobre administración pública costarricense
- Estudiar técnicas de feedback pedagógico en entornos digitales de evaluación

---

## 🚀 Novedades en v2.0

| Característica | v1.0 | v2.0 |
|---|---|---|
| Modos de práctica | Solo Estudio | Estudio + **Examen Real** |
| Cronómetro | ❌ | ✅ 70 min con auto-envío |
| Navegación de preguntas | Lineal | Grid visual + saltos libres |
| Marcar para revisión | ❌ | ✅ Sistema de marcadores ⭐ |
| Historial de sesiones | ❌ | ✅ Con gráficos de progreso |
| Estadísticas | Básicas | Por tema + tendencias temporales |
| Revisión de incorrectas | ❌ | ✅ Detalle con justificación |
| Estado de aprobación | ❌ | ✅ APROBADO / REPROBADO (≥70%) |
| Abandono seguro | ❌ | ✅ Sin guardar sesiones incompletas |
| Total de preguntas | 246 | **380** |

---

## ✨ Características

### 📚 Modo Estudio

- Selección libre de temas (todos o específicos) y nivel de dificultad
- **Feedback inmediato** con justificación del manual después de cada respuesta
- Progreso y métricas en tiempo real en el sidebar
- Botón **"🚪 Abandonar simulacro"** en el sidebar que limpia el estado completamente y vuelve al menú sin guardar datos parciales

### ⏱️ Modo Examen Real

- **66 preguntas aleatorias** de todos los temas (simula el examen oficial DGSC)
- **Cronómetro regresivo de 70 minutos**: verde cuando hay tiempo suficiente, rojo parpadeante al bajar de 10 minutos
- **Auto-envío automático** al agotar el tiempo
- Sin feedback durante el examen — resultados completos al finalizar
- **Grid de navegación** codificado por color: 🟢 respondida · ⭐ marcada · ⚪ sin tocar
- Navegación libre entre preguntas (sin restricción de avance)
- Diálogo de confirmación antes de enviar, con conteo de preguntas pendientes

### 📊 Dashboard de Resultados

- Calificación general con veredicto **APROBADO / REPROBADO** (umbral 70%)
- Tiempo total usado
- Desempeño por tema con gráfico de barras
- Identificación automática de áreas críticas (< 70%)
- Revisión de cada pregunta incorrecta con tu respuesta vs. la correcta y justificación del manual
- Gráfico de línea de evolución entre intentos anteriores

### 🗃️ Historial Persistente

- Registro automático de sesiones completadas en SQLite local
- Últimas 5 sesiones visibles directamente en el menú principal
- Limpieza automática al iniciar de registros con datos corruptos (tipos binarios de numpy)

### 🔧 Funcionalidades Técnicas

- Aleatorización de preguntas y opciones en cada sesión
- Filtrado por temas y nivel de dificultad
- Session ID único por navegador
- Diseño responsive (desktop y móvil)
- Sin necesidad de registro ni cuenta

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|---|---|---|
| **Python** | 3.11+ | Lenguaje base |
| **Streamlit** | 1.32+ | Framework web interactivo |
| **SQLite** | 3.x | Base de datos embebida |
| **Pandas** | 2.0+ | Manipulación de datos y estadísticas |

### Arquitectura

```
┌──────────────────────────────┐
│         Streamlit UI         │  ← Interfaz (Menú / Estudio / Examen / Resultados)
└──────────────┬───────────────┘
               │
        ┌──────▼──────┐
        │   app.py    │      ← Lógica principal, estados, modos, validaciones
        └──────┬──────┘
               │
   ┌───────────┼──────────────┐
   ▼           ▼              ▼
banco_preguntas.py    dgsc_pro.db (SQLite)
(380 preguntas        ├── preguntas
 en 8 temas)          └── historial
```

---

## 💻 Instalación Local

### Prerrequisitos

- Python 3.11 o superior
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU-USUARIO/dgsc-quiz.git
cd dgsc-quiz

# 2. (Recomendado) Crear entorno virtual
python -m venv venv
source venv/bin/activate       # Linux/macOS
# venv\Scripts\activate        # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
streamlit run app.py
```

La aplicación se abre automáticamente en `http://localhost:8501`

---

## 🚀 Uso

### Flujo Modo Estudio

1. Haz clic en **"📖 Iniciar Modo Estudio"**
2. Selecciona temas y nivel de dificultad
3. Haz clic en **"🚀 Comenzar simulacro"**
4. Responde cada pregunta y lee la justificación antes de continuar
5. Usa **"🏁 Terminar y ver resultados"** en el sidebar cuando quieras
6. Para salir sin guardar: **"🚪 Abandonar simulacro"** en el sidebar

### Flujo Modo Examen

1. Haz clic en **"🎯 Iniciar Examen Real"**
2. Se cargan 66 preguntas aleatorias y el cronómetro inicia
3. Responde o marca con ⭐ las preguntas dudosas
4. Navega libremente con el grid del sidebar
5. Haz clic en **"🏁 Finalizar Examen"** cuando termines
6. Confirma el envío en el diálogo que aparece
7. El examen también se envía automáticamente al agotar el tiempo

---

## 📁 Estructura del Proyecto

```
dgsc-quiz/
│
├── app.py                    # Aplicación principal Streamlit (v2.0)
├── banco_preguntas.py        # 380 preguntas en 8 temas
├── requirements.txt          # Dependencias
├── LICENSE                   # Licencia MIT
│
├── README.md                 # Este archivo
├── CHANGELOG_v2.md           # Historial de cambios v1 → v2
├── DISCLAIMER.md             # Aviso legal completo
├── CONTRIBUTING.md           # Guía para contribuidores
├── ACADEMIC.md               # Ficha académica y estrategia de difusión
│
├── .gitignore
└── dgsc_pro.db               # Base de datos SQLite (se genera automáticamente)
```

---

## 📚 Contenido Académico

### Temas Cubiertos

| # | Tema | Preguntas | Páginas Manual |
|---|---|---|---|
| 1 | Generalidades del Estado de Derecho Costarricense | 74 | pp. 5–18 |
| 2 | La Administración Pública Costarricense | 32 | pp. 19–21 |
| 3 | Normas Básicas para la Función Pública (7 leyes) | 79 | pp. 22–41 |
| 4 | El Régimen de Servicio Civil en Costa Rica | 37 | pp. 42–49 |
| 5 | Ética y Valores en la Función Pública | 38 | pp. 50–61 |
| 6 | Competencias Requeridas para Directivos Públicos | 36 | pp. 62–68 |
| 7 | Elementos Generales de Administración y Tendencias | 46 | pp. 69–77 |
| S | Glosario de Siglas y Acrónimos | 38 | p. 2 + barrido completo |
| **TOTAL** | | **380** | |

### Distribución por Dificultad

Cada pregunta está clasificada para una curva de aprendizaje progresiva:

- 🟢 **Básico**: Definiciones y conceptos directos extraídos del manual
- 🟡 **Intermedio**: Aplicación de conceptos, comparación de categorías, procedimientos
- 🔴 **Avanzado**: Análisis, síntesis, referencias normativas exactas (artículos, fechas, decretos)

### Fuente Oficial

Todas las preguntas están basadas en:

> **Manual de Orientación para el Ingreso y Ejercicio de Puestos de Dirección Pública**  
> Dirección General de Servicio Civil — Versión 1, enero 2019  
> Elaborado por: Mauricio Rojas Alfaro (CECADES / DGSC)

Cada pregunta incluye referencia exacta a la página del manual y justificación con el texto relevante.

---

## 🗺️ Roadmap

### ✅ v1.0 — Modo Estudio Base
- 246 preguntas, 7 temas
- Feedback inmediato con justificaciones
- Filtros por tema y dificultad
- Dashboard de resultados básico

### ✅ v2.0 — Modo Examen Real (actual)
- Modo Examen con cronómetro de 70 min y auto-envío
- 380 preguntas (Temas 1–7 + Glosario de Siglas)
- Grid de navegación visual con sistema de marcadores ⭐
- Historial persistente en SQLite con gráfico de evolución
- Análisis de incorrectas con justificaciones del manual
- Estado APROBADO / REPROBADO (umbral 70%)
- Abandono seguro sin guardar sesiones incompletas
- Corrección de bug de tipos de datos numpy en SQLite

### 🔮 v3.0 — Planificado
- [ ] Exportar resultados a PDF
- [ ] Modo de repaso inteligente (solo preguntas falladas anteriormente)
- [ ] Login opcional para historial entre dispositivos
- [ ] Modo oscuro / claro seleccionable
- [ ] Meta: 500+ preguntas

### 💡 Ideas Futuras
- Gamificación (puntos, rachas diarias, badges por tema)
- Percentiles anónimos comparativos entre usuarios
- Flashcards para repaso rápido
- Preguntas adaptativas por dificultad dinámica

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Lee [CONTRIBUTING.md](CONTRIBUTING.md) para el workflow completo.

### Formas de Contribuir

- 📝 **Contenido**: Agregar o corregir preguntas siguiendo el formato documentado
- 🐛 **Bugs**: Reportar errores mediante Issues de GitHub
- 💡 **Features**: Proponer mejoras con un Feature Request
- 📚 **Documentación**: Mejorar README, guías o comentarios en el código

### Workflow Rápido

```bash
git checkout -b feature/mi-mejora
# ... cambios ...
git commit -m "feat: descripción del cambio"
git push origin feature/mi-mejora
# abrir Pull Request
```

---

## 📄 Licencia

Distribuido bajo la **Licencia MIT**. Ver [LICENSE](LICENSE) para detalles.

El autor conserva la autoría perpetua del proyecto. El código puede ser usado, modificado y distribuido libremente siempre que se conserve el aviso de copyright original.

---

## ⚖️ Disclaimer Legal

Este es un proyecto académico **independiente y no oficial**. No está afiliado, patrocinado ni respaldado por la Dirección General de Servicio Civil (DGSC) ni por ninguna institución del Estado costarricense.

Las preguntas son paráfrasis educativas basadas en un documento de dominio público. No garantizan aprobación en exámenes oficiales. Siempre verifica la información con fuentes oficiales en [www.dgsc.go.cr](http://www.dgsc.go.cr).

Ver [DISCLAIMER.md](DISCLAIMER.md) para el texto legal completo.

---

## 👤 Contacto

**Autor:** Apache  
**Institución:** Universidad del Rosario — Bogotá, Colombia  
**Programa:** Maestría en Matemáticas Aplicadas y Ciencias de la Computación (Especialización IA)

| Canal | Link |
|---|---|
| 🌐 Sitio Web | [mindforce.cloud](https://mindforce.cloud) |
| 💼 LinkedIn | [Tu perfil] |
| 📧 Email | [Tu email] |
| 🐙 GitHub | [@TU-USUARIO](https://github.com/TU-USUARIO) |

### Cita Académica (BibTeX)

```bibtex
@software{apache_dgsc_simulator_2026,
  author       = {Apache},
  title        = {{Simulador DGSC: Herramienta Educativa Interactiva
                   para Preparación de Exámenes del Servicio Civil de Costa Rica}},
  year         = {2026},
  version      = {2.0},
  publisher    = {GitHub},
  url          = {https://github.com/TU-USUARIO/dgsc-quiz},
  institution  = {Universidad del Rosario, Colombia},
  license      = {MIT},
  note         = {380 preguntas basadas en Manual DGSC 2019. 
                  Incluye Modo Examen Real con cronómetro e historial persistente.}
}
```

---

## 🙏 Agradecimientos

- **Dirección General de Servicio Civil de Costa Rica** — Por el manual público que sirve de base
- **Universidad del Rosario** — Por el contexto académico
- **Comunidad Streamlit** — Por el framework
- **Contribuidores** — A todos quienes mejoren este proyecto

---

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/TU-USUARIO/dgsc-quiz?style=social)
![GitHub forks](https://img.shields.io/github/forks/TU-USUARIO/dgsc-quiz?style=social)

**Hecho con ❤️ para la comunidad académica y los aspirantes al servicio público costarricense**

⭐ Si este proyecto te resultó útil, dale una estrella en GitHub

[⬆ Volver arriba](#-simulador-dgsc--costa-rica)

</div>
