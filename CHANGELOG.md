# 🚀 CHANGELOG — Simulador DGSC

---

## v2.0 — Modo Examen Real + 380 Preguntas
**Fecha:** 20 de febrero de 2026  
**Autor:** Apache

---

### ✨ Nuevas Características

#### 1. Modo Examen Real ⏱️

Nueva pantalla de selección al inicio con dos modos claramente diferenciados:

**📚 Modo Estudio** (mejorado desde v1.0)
- Sin límite de tiempo
- Feedback inmediato con justificaciones del manual
- Selección de temas específicos y nivel de dificultad
- Nuevo botón de abandono seguro en el sidebar

**⏱️ Modo Examen Real** (nuevo)
- 66 preguntas aleatorias de todos los temas
- 70 minutos cronometrados con auto-envío al agotar el tiempo
- Sin feedback durante el examen — resultados solo al final
- Simula las condiciones del examen oficial DGSC

---

#### 2. Cronómetro con Alertas Visuales ⏰

- Cuenta regresiva visible en el sidebar durante el examen
- Verde (`timer-ok`) cuando quedan más de 10 minutos
- Rojo parpadeante (`timer-warning` con animación CSS) al bajar de 10 minutos
- **Auto-envío automático** cuando el tiempo llega a cero

---

#### 3. Grid de Navegación Visual 🗺️

Mapa interactivo de las 66 preguntas del examen en el sidebar:

- 🟢 **Verde**: Pregunta respondida
- ⭐ **Estrella**: Marcada para revisión posterior
- ⚪ **Blanco**: Sin tocar aún
- **[N]**: Pregunta actualmente visible

Click en cualquier número para saltar directamente a esa pregunta. Los botones ⬅️ Anterior / Siguiente ➡️ siguen disponibles.

---

#### 4. Sistema de Marcadores ⭐

- Botón "⭐ Marcar / ✅ Desmarcar" en cada pregunta del examen
- Contador de marcadas en el sidebar
- Las marcadas aparecen en el grid para facilitar la revisión final antes de enviar

---

#### 5. Historial Persistente de Sesiones 📊

Base de datos SQLite ampliada con tabla `historial`:

```sql
CREATE TABLE historial (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT,
    fecha       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modo        TEXT,        -- 'estudio' | 'examen'
    calificacion REAL,
    tiempo_usado INTEGER,    -- segundos
    correctas   INTEGER,
    total       INTEGER,
    por_tema    TEXT         -- JSON con % por tema
);
```

- Últimas 5 sesiones visibles en el menú principal
- Gráfico de línea con evolución de calificaciones en la pantalla de resultados del examen
- Mensaje de tendencia (mejora / disminución desde primer intento)

---

#### 6. Dashboard de Resultados Mejorado 📈

**Modo Estudio**
- Métricas: calificación, correctas, incorrectas, tiempo
- Gráfico de barras por tema
- Tabla detallada con porcentaje de aciertos
- Identificación de áreas < 70%

**Modo Examen**
- Métricas anteriores + estado **APROBADO ✅ / REPROBADO ❌** (umbral 70%)
- Gráfico de barras por tema
- Sección expandible con detalle de cada pregunta incorrecta:
  - Enunciado completo
  - Tu respuesta vs. la correcta
  - Justificación del manual
- Gráfico de progreso entre intentos anteriores

---

#### 7. Banco de Preguntas Ampliado a 380 🗃️

| Tema | v1.0 | v2.0 | Δ |
|---|---|---|---|
| 1 — Estado de Derecho | 45 | 74 | +29 |
| 2 — Administración Pública | 27 | 32 | +5 |
| 3 — Normas Básicas (7 leyes) | 42 | 79 | +37 |
| 4 — Régimen de Servicio Civil | 46 | 37 | −9* |
| 5 — Ética y Valores | 36 | 38 | +2 |
| 6 — Competencias Directivos | 20 | 36 | +16 |
| 7 — Administración y Tendencias | 20 | 46 | +26 |
| S — Glosario de Siglas | 10 | 38 | +28 |
| **TOTAL** | **246** | **380** | **+134** |

*El Tema 4 fue revisado y depurado eliminando preguntas duplicadas o con errores de referencia.

Cada pregunta incluye: enunciado, respuesta correcta, 3 distractores plausibles, justificación con cita textual del manual y número de página exacto.

---

### 🐛 Correcciones de Bugs

#### Bug crítico: valores binarios en historial

**Síntoma:** El historial mostraba `b'\x01\x00\x00\x00\x00\x00\x00\x00'` en lugar del número de respuestas correctas.

**Causa raíz:** Los valores `correctas` y `total` provenían de operaciones `.sum()` y `.count()` de Pandas, que retornan `numpy.int64`. SQLite los serializaba como blob binario en lugar de integer.

**Corrección (`app.py` línea 448):**
```python
# Antes (buggy)
guardar_historial('estudio', nota, int(tiempo_usado), ok, total_r, ...)

# Ahora (corregido)
guardar_historial('estudio', float(nota), int(tiempo_usado), int(ok), int(total_r), ...)
```

**Corrección adicional** en visualización del historial: conversión defensiva con `try/except` antes de mostrar los valores.

---

#### Bug: sesiones incompletas guardadas en historial

**Síntoma:** Al volver al menú desde un simulacro a mitad sin terminarlo, el sistema guardaba el resultado parcial con datos incorrectos.

**Causa raíz:** No existía botón de salida limpio dentro del quiz activo. El flujo de estado quedaba inconsistente al cambiar `modo = None` sin limpiar `quiz_data`.

**Corrección:**
- Añadido botón **"🚪 Abandonar simulacro"** en el sidebar del Modo Estudio que elimina todo el estado antes de volver al menú
- Añadida guardia al inicio del bloque de resultados del Modo Estudio:
```python
if "tiempo_inicio_estudio" not in st.session_state:
    # Estado corrupto — limpiar y redirigir al menú
    for k in ["quiz_data", "indice", "respuestas", "feedback"]:
        st.session_state.pop(k, None)
    st.session_state.modo = None
    st.rerun()
```

---

#### Bug: registros corruptos en la base de datos

**Síntoma:** Registros con `correctas` o `total` almacenados como blob binario persistían entre sesiones.

**Corrección:** `inicializar_db()` ejecuta un `DELETE` al arrancar:
```sql
DELETE FROM historial 
WHERE typeof(correctas) != 'integer' 
   OR typeof(total) != 'integer'
   OR correctas IS NULL 
   OR total IS NULL 
   OR total = 0
```

---

### 🛠️ Cambios Técnicos

#### Session State en v2.0

```python
st.session_state = {
    # Siempre presente
    'session_id':    'user_1708189423',   # único por navegador
    'modo':          'estudio' | 'examen' | 'resultados_examen' | None,

    # Modo Estudio
    'quiz_data':            pd.DataFrame,  # preguntas cargadas
    'indice':               int,
    'respuestas':           list,          # [{tema, dificultad, es_correcta}]
    'feedback':             dict | None,
    'tiempo_inicio_estudio': datetime,

    # Modo Examen
    'respuestas_examen':    dict,          # {indice: texto_respuesta}
    'marcadas':             set,           # {0, 5, 12, ...}
    'tiempo_inicio':        datetime,
    'tiempo_limite_seg':    4200,          # 70 minutos
    'tiempo_usado_examen':  int,
    'mostrar_confirmacion': bool,
    'mostrar_confirmacion_salida': bool,
    'info_mostrada':        bool,
}
```

#### Nuevas Funciones

```python
def formatear_tiempo(segundos: int) -> str:
    """Convierte segundos a formato MM:SS."""

def guardar_historial(modo, calificacion, tiempo_usado, correctas, total, por_tema):
    """Guarda sesión en BD con tipos nativos Python (no numpy)."""

def cargar_historial() -> pd.DataFrame:
    """Recupera los últimos 10 intentos del session_id actual."""
```

---

### 🔄 Migración desde v1.0

```bash
# El archivo banco_preguntas.py es compatible con ambas versiones
# La BD se actualiza automáticamente al iniciar

# Ejecutar la nueva versión
streamlit run app.py

# La tabla historial se crea automáticamente si no existe
# Los registros corruptos se eliminan en el primer arranque
```

---

## v1.0 — Lanzamiento Inicial
**Fecha:** Enero 2026

- 246 preguntas en 7 temas basadas en el Manual DGSC 2019
- Modo Estudio con feedback inmediato
- Filtros por tema y dificultad
- Dashboard de resultados con gráfico por tema
- Base de datos SQLite con carga automática del banco

---

<div align="center">

**Desarrollado por Apache | Universidad del Rosario | 2026**

[⬆ Volver al README](README.md)

</div>
