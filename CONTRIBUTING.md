# 🤝 Guía de Contribución — Simulador DGSC

¡Gracias por tu interés en contribuir! Este documento explica cómo hacerlo de forma efectiva.

---

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo Contribuir?](#cómo-contribuir)
- [Proceso de Contribución](#proceso-de-contribución)
- [Agregar Preguntas](#agregar-preguntas)
- [Guía de Estilo](#guía-de-estilo)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Mejoras](#sugerir-mejoras)
- [Estructura de Commits](#estructura-de-commits)

---

## 📜 Código de Conducta

Este proyecto se compromete a un ambiente respetuoso e inclusivo. Se espera:

✅ Lenguaje respetuoso y constructivo  
✅ Aceptar críticas con apertura  
✅ Enfocarse en mejorar el proyecto  
❌ Sin ataques personales, trolling ni acoso  
❌ Sin lenguaje discriminatorio de ningún tipo

---

## 🎯 ¿Cómo Contribuir?

### 1. 📝 Agregar Contenido (más impacto)

El banco tiene 380 preguntas. El objetivo para v3.0 es llegar a **400+**. Los temas más prioritarios para nuevas preguntas son los que tienen menos cobertura relativa.

### 2. 🐛 Reportar Bugs

¿Encontraste un error? [Abre un Issue](https://github.com/Alonso666cr/Prueba_Idoneidad_General_DGSC/issues/new) con la etiqueta `bug`.

### 3. 💡 Sugerir Mejoras

¿Tienes una idea? [Abre un Issue](https://github.com/Alonso666cr/Prueba_Idoneidad_General_DGSC/issues/new) con la etiqueta `enhancement`.

### 4. 📚 Mejorar Documentación

Corregir errores, clarificar instrucciones, mejorar comentarios en el código.

### 5. 🧪 Testing

Probar en distintos navegadores y dispositivos, reportar comportamientos inesperados.

---

## 🔄 Proceso de Contribución

```bash
# 1. Fork del repositorio en GitHub

# 2. Clonar tu fork
git clone https://github.com/Alonso666cr/Prueba_Idoneidad_General_DGSC.git
cd Prueba_Idoneidad_General_DGSC

# 3. Agregar el upstream
git remote add upstream https://github.com/Alonso666cr/Prueba_Idoneidad_General_DGSC.git

# 4. Crear rama de trabajo
git checkout main
git pull upstream main
git checkout -b feature/nombre-descriptivo

# 5. Hacer cambios y probar localmente
pip install -r requirements.txt
streamlit run app.py

# 6. Commit con mensaje descriptivo
git add .
git commit -m "feat(tema3): Agregar 15 preguntas de Ley 8131"

# 7. Push y Pull Request
git push origin feature/nombre-descriptivo
```

### Convenciones de Nombres de Rama

- `feature/` — Nueva funcionalidad o preguntas
- `fix/` — Corrección de bug
- `docs/` — Cambios en documentación
- `refactor/` — Refactorización de código

---

## ➕ Agregar Preguntas

Esta es la contribución más valiosa. Sigue el formato exacto:

### Formato de Tupla

```python
("TEMA_NUM", "Título Exacto del Tema",
 "¿Enunciado completo y claro de la pregunta?",
 "Respuesta correcta (texto completo)",
 "Distractor 1 (plausible pero incorrecto)",
 "Distractor 2 (plausible pero incorrecto)",
 "Distractor 3 (plausible pero incorrecto)",
 "Manual p.XX - Sección Y.Z: Justificación extraída del texto del manual.",
 "basico",   # nivel: basico | intermedio | avanzado
 "p.XX"),    # página exacta del manual
```

### Ejemplo Correcto ✅

```python
("4", "El Régimen de Servicio Civil en Costa Rica",
 "¿Cuál es el principio rector para el ingreso al Régimen de Servicio Civil?",
 "El mérito y la idoneidad comprobada mediante concurso",
 "La antigüedad acumulada en el sector público costarricense",
 "Las recomendaciones del jerarca de la institución",
 "El nivel socioeconómico del aspirante al puesto",
 "Manual p.43 - Sección 4.2: El ingreso al RSC se rige por el principio "
 "de mérito e idoneidad comprobada a través de concurso.",
 "basico",
 "p.43"),
```

### Ejemplo Incorrecto ❌

```python
# ❌ Enunciado sin signo de interrogación
# ❌ Respuesta correcta demasiado corta
# ❌ Distractores obviamente incorrectos
# ❌ Justificación sin referencia de página
# ❌ Nivel de dificultad faltante
("4", "Servicio Civil",
 "Principio del servicio civil",
 "Mérito",
 "Dinero", "Suerte", "Favores",
 "Es el mérito.",
 "",
 ""),
```

### Criterios de Calidad

| Criterio | Requerimiento |
|---|---|
| **Fuente** | Basada fielmente en el Manual DGSC 2019 |
| **Enunciado** | Claro, entre 60–150 caracteres, con signo de interrogación |
| **Respuesta correcta** | Texto completo, no abreviado |
| **Distractores** | Plausibles y del mismo dominio que la correcta |
| **Justificación** | Referencia exacta: "Manual p.XX - Sección Y.Z: ..." |
| **Dificultad** | `basico` para definiciones, `intermedio` para aplicación, `avanzado` para análisis/normativa exacta |

### Dónde Agregar las Preguntas

En `banco_preguntas.py`, añade las tuplas dentro de la lista correspondiente al tema:

```python
TEMA_1 = [
    # ... preguntas existentes ...
    ("1", "Generalidades del Estado de Derecho...",  # tu pregunta aquí
     ...),
]
```

---

## 🎨 Guía de Estilo

### Python (PEP 8)

```python
# ✅ Correcto
def cargar_preguntas(temas_seleccionados: list = None, 
                     dificultad: str = None, 
                     limit: int = None) -> pd.DataFrame:
    """
    Carga preguntas filtradas desde SQLite.

    Args:
        temas_seleccionados: Lista de tema_num a incluir (None = todos)
        dificultad: Nivel de dificultad (None = todos)
        limit: Máximo de preguntas a retornar

    Returns:
        DataFrame con preguntas aleatorias según filtros
    """
    conn = sqlite3.connect(DB_PATH)
    # ...

# ❌ Incorrecto
def cargaPreguntas(t,d,l):
    c=sqlite3.connect(DB_PATH)
```

**Reglas:**
- Indentación: 4 espacios
- Líneas máximo 88 caracteres
- Docstrings en todas las funciones públicas
- Type hints en parámetros
- Variables en `snake_case`, constantes en `UPPER_CASE`

### Streamlit

```python
# ✅ Estructura organizada
with st.sidebar:
    st.title("📈 Progreso")
    st.progress(avance)

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Configuración")

# ❌ Sin estructura
st.title("X")
st.write("y")
st.selectbox("z", [])
```

---

## 🐛 Reportar Bugs

Al abrir un Issue de bug, incluye:

```markdown
**Descripción**
[Qué pasa exactamente]

**Pasos para reproducir**
1. Ir a '...'
2. Hacer clic en '...'
3. Ver el error

**Comportamiento esperado**
[Qué debería pasar]

**Comportamiento actual**
[Qué pasa realmente]

**Entorno**
- OS: [ej. Ubuntu 22.04]
- Navegador: [ej. Chrome 122]
- Python: [ej. 3.11.5]
- Streamlit: [ej. 1.32.0]

**Screenshots / mensajes de error**
[Adjunta si aplica]
```

---

## 💡 Sugerir Mejoras

Al abrir un Issue de feature request, incluye:

```markdown
**Problema que resuelve**
[Necesidad o limitación actual]

**Solución propuesta**
[Descripción de la mejora]

**Alternativas consideradas**
[Otras opciones evaluadas]

**Impacto esperado**
[Cómo mejora la experiencia del usuario]
```

---

## 📝 Estructura de Commits

Usamos **Conventional Commits**:

```
<tipo>(<alcance>): <descripción corta en imperativo>
```

### Tipos

| Tipo | Cuándo usarlo |
|---|---|
| `feat` | Nueva funcionalidad o preguntas |
| `fix` | Corrección de bug |
| `docs` | Solo documentación |
| `style` | Formato (sin cambio de lógica) |
| `refactor` | Refactorización |
| `test` | Tests |
| `chore` | Mantenimiento |

### Ejemplos

```bash
git commit -m "feat(banco): Agregar 20 preguntas del Tema 3 (Ley 8131)"
git commit -m "fix(historial): Corregir tipo numpy.int64 en guardar_historial"
git commit -m "docs(readme): Actualizar tabla de preguntas a 380"
git commit -m "feat(ui): Añadir botón de abandono seguro en Modo Estudio"
```

---

## ✅ Checklist Antes de PR

- [ ] El código sigue la guía de estilo del proyecto
- [ ] Probado localmente con `streamlit run app.py`
- [ ] Las preguntas nuevas siguen el formato exacto documentado
- [ ] Los commits tienen mensajes descriptivos siguiendo Conventional Commits
- [ ] El README o CHANGELOG fue actualizado si el cambio lo amerita
- [ ] No hay conflictos con la rama `main`

---

## 🏆 Reconocimiento

Todos los contribuidores serán reconocidos en el README con su usuario de GitHub y tipo de contribución.

---

## ❓ ¿Dudas?

Abre un Issue con la etiqueta `question` en [GitHub Issues](https://github.com/Alonso666cr/Prueba_Idoneidad_General_DGSC/issues).

---

<div align="center">

**¡Gracias por contribuir al acceso libre al conocimiento! 🎓**

[⬆ Volver al README](README.md)

</div>
