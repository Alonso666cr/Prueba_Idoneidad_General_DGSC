import streamlit as st
import sqlite3
import random
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from banco_preguntas import BANCO_COMPLETO

# ============================================================
# 1. MOTOR DE BASE DE DATOS
# ============================================================
DB_PATH = "dgsc_pro.db"

def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabla de preguntas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preguntas (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            tema_num     TEXT    NOT NULL,
            tema_titulo  TEXT    NOT NULL,
            enunciado    TEXT    NOT NULL,
            correcta     TEXT    NOT NULL,
            d1           TEXT    NOT NULL,
            d2           TEXT    NOT NULL,
            d3           TEXT    NOT NULL,
            justificacion TEXT   NOT NULL,
            dificultad   TEXT    NOT NULL DEFAULT 'basico',
            pagina_manual TEXT   NOT NULL DEFAULT ''
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM preguntas")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            """INSERT INTO preguntas
               (tema_num, tema_titulo, enunciado, correcta, d1, d2, d3,
                justificacion, dificultad, pagina_manual)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            BANCO_COMPLETO
        )
        conn.commit()

    # Tabla de historial
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modo TEXT,
            calificacion REAL,
            tiempo_usado INTEGER,
            correctas INTEGER,
            total INTEGER,
            por_tema TEXT
        )
    ''')

    # Limpiar registros corruptos (correctas/total guardados como bytes por error numpy)
    cursor.execute("""
        DELETE FROM historial 
        WHERE typeof(correctas) != 'integer' OR typeof(total) != 'integer'
           OR correctas IS NULL OR total IS NULL OR total = 0
    """)

    conn.commit()
    conn.close()

# ============================================================
# 2. HELPERS
# ============================================================
def cargar_preguntas(temas_seleccionados=None, dificultad=None, limit=None):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM preguntas WHERE 1=1"
    params = []

    if temas_seleccionados:
        placeholders = ",".join("?" * len(temas_seleccionados))
        query += f" AND tema_num IN ({placeholders})"
        params.extend(temas_seleccionados)

    if dificultad and dificultad != "Todos":
        query += " AND dificultad = ?"
        params.append(dificultad.lower())

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    df = df.sample(frac=1).reset_index(drop=True)
    if limit:
        df = df.head(limit)
    return df

def mezclar_opciones(row, key):
    if key not in st.session_state:
        opciones = [row["correcta"], row["d1"], row["d2"], row["d3"]]
        random.shuffle(opciones)
        st.session_state[key] = opciones
    return st.session_state[key]

def badge_dificultad(nivel):
    colores = {"basico": "🟢", "intermedio": "🟡", "avanzado": "🔴"}
    return colores.get(nivel, "⚪")

def guardar_historial(modo, calificacion, tiempo_usado, correctas, total, por_tema):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    session_id = st.session_state.get('session_id', 'anonymous')
    cursor.execute("""
        INSERT INTO historial (session_id, modo, calificacion, tiempo_usado, correctas, total, por_tema)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, modo, calificacion, tiempo_usado, correctas, total, json.dumps(por_tema)))
    conn.commit()
    conn.close()

def cargar_historial():
    conn = sqlite3.connect(DB_PATH)
    session_id = st.session_state.get('session_id', 'anonymous')
    df = pd.read_sql_query(
        "SELECT * FROM historial WHERE session_id = ? ORDER BY fecha DESC LIMIT 10",
        conn,
        params=(session_id,)
    )
    conn.close()
    return df

def formatear_tiempo(segundos):
    mins, secs = divmod(int(segundos), 60)
    return f"{mins:02d}:{secs:02d}"

# ============================================================
# 3. CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="Simulador DGSC v2",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stRadio > div { gap: 0.5rem; }
    div[data-testid="metric-container"] { 
        background:#f0f4ff; border-radius:8px; padding:0.5rem 1rem; 
    }
    .tema-badge { 
        background:#1a3a6b; color:white; padding:4px 12px;
        border-radius:12px; font-size:0.85rem; font-weight:600; 
    }
    .pregunta-box { 
        background:#f8f9fa; border-left:4px solid #1a3a6b;
        padding:1rem 1.5rem; border-radius:0 8px 8px 0;
        font-size:1.05rem; margin-bottom:1rem; 
    }
    .timer-warning { 
        background:#ff4b4b; color:white; padding:1rem;
        border-radius:8px; text-align:center; font-size:1.5rem;
        font-weight:bold; animation: pulse 1s infinite;
    }
    .timer-ok { 
        background:#0d9373; color:white; padding:1rem;
        border-radius:8px; text-align:center; font-size:1.5rem;
        font-weight:bold;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    .nav-grid {
        display: grid;
        grid-template-columns: repeat(11, 1fr);
        gap: 0.5rem;
        margin: 1rem 0;
    }
    .nav-btn {
        padding: 0.5rem;
        border-radius: 4px;
        text-align: center;
        cursor: pointer;
        font-weight: bold;
    }
    .nav-respondida { background: #90EE90; }
    .nav-marcada { background: #FFD700; }
    .nav-sin-responder { background: #E0E0E0; }
    .nav-actual { border: 3px solid #1a3a6b; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 4. INICIALIZACIÓN
# ============================================================
inicializar_db()

# Session ID único para tracking
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"user_{int(time.time())}"

TEMAS_INFO = {
    "1": "Generalidades del Estado de Derecho",
    "2": "La Administración Pública Costarricense",
    "3": "Normas Básicas para la Función Pública",
    "4": "El Régimen de Servicio Civil en Costa Rica",
    "5": "Ética y Valores en la Función Pública",
    "6": "Competencias Requeridas para Directivos Públicos",
    "7": "Elementos de Administración y Tendencias",
    "8": "Glosario de Siglas",
}

# ============================================================
# 5. SELECTOR DE MODO
# ============================================================
if 'modo' not in st.session_state:
    st.session_state.modo = None

if st.session_state.modo is None:
    st.title("🏛️ Simulador DGSC v2.0")
    st.markdown("**Dirección General de Servicio Civil | Costa Rica**")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📚 Modo Estudio")
        st.markdown("""
        **Características:**
        - ✅ Sin límite de tiempo
        - ✅ Feedback inmediato con justificaciones
        - ✅ Selección de temas y dificultad
        - ✅ Ideal para aprender conceptos
        
        **Recomendado para:**
        - Primera aproximación al material
        - Reforzar áreas débiles
        - Estudiar temas específicos
        """)
        if st.button("📖 Iniciar Modo Estudio", use_container_width=True, type="secondary"):
            st.session_state.modo = 'estudio'
            st.rerun()

    with col2:
        st.markdown("### ⏱️ Modo Examen Real")
        st.markdown("""
        **Características:**
        - ⚠️ **66 preguntas aleatorias** de todos los temas
        - ⚠️ **70 minutos** cronometrados
        - ⚠️ **Sin feedback inmediato** (resultados al final)
        - ⚠️ Auto-envío al terminar el tiempo
        
        **Simula examen oficial DGSC**
        - Presión de tiempo real
        - Evaluación completa
        - Estadísticas detalladas
        """)
        if st.button("🎯 Iniciar Examen Real", use_container_width=True, type="primary"):
            # Cargar 66 preguntas aleatorias de todos los temas
            df = cargar_preguntas(limit=66)
            if len(df) < 66:
                st.error(f"⚠️ Solo hay {len(df)} preguntas disponibles. Se requieren mínimo 66.")
            else:
                st.session_state.modo = 'examen'
                st.session_state.quiz_data = df
                st.session_state.indice = 0
                st.session_state.respuestas_examen = {}  # {indice: respuesta}
                st.session_state.marcadas = set()
                st.session_state.tiempo_inicio = datetime.now()
                st.session_state.tiempo_limite_seg = 70 * 60  # 70 minutos
                st.rerun()

    st.divider()
    
    # Mostrar historial si existe
    historial_df = cargar_historial()
    if not historial_df.empty:
        st.subheader("📊 Tu Historial Reciente")
        for _, row in historial_df.head(5).iterrows():
            fecha = pd.to_datetime(row['fecha']).strftime("%d/%m/%Y %H:%M")
            modo_icon = "📚" if row['modo'] == 'estudio' else "⏱️"
            tiempo = formatear_tiempo(row['tiempo_usado']) if row['tiempo_usado'] else "N/A"
            # Conversión segura: correctas y total pueden venir como bytes en SQLite
            try:
                correctas_val = int(row['correctas']) if row['correctas'] is not None else 0
                total_val = int(row['total']) if row['total'] is not None else 0
            except (TypeError, ValueError):
                correctas_val = 0
                total_val = 0
            st.markdown(f"""
            **{modo_icon} {row['modo'].title()}** - {fecha}  
            Calificación: **{row['calificacion']:.1f}%** ({correctas_val}/{total_val}) | Tiempo: {tiempo}
            """)
        st.divider()

    st.stop()

# ============================================================
# 6. MODO ESTUDIO
# ============================================================
elif st.session_state.modo == 'estudio':
    
    # Configuración (solo si no hay quiz activo)
    if "quiz_data" not in st.session_state:
        st.title("🏛️ Simulador DGSC — Modo Estudio")
        st.divider()

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("⚙️ Configura tu sesión")

            modo_temas = st.radio(
                "¿Qué temas deseas practicar?",
                ["Todos los temas", "Seleccionar temas específicos"],
                horizontal=True
            )

            temas_elegidos = list(TEMAS_INFO.keys())
            if modo_temas == "Seleccionar temas específicos":
                opciones = [f"Tema {k}: {v}" for k, v in TEMAS_INFO.items()]
                seleccion = st.multiselect("Elige los temas:", opciones)
                temas_elegidos = [op.split(":")[0].replace("Tema ", "").strip() for op in seleccion]

            dificultad_sel = st.selectbox(
                "Nivel de dificultad:",
                ["Todos", "Basico", "Intermedio", "Avanzado"]
            )

        with col2:

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM preguntas")
            total_general = cursor.fetchone()[0]
            
            st.subheader(f"📊 Banco de preguntas: {total_general}")
            
            #st.subheader("📊 Banco de preguntas")
            #conn = sqlite3.connect(DB_PATH)
            stats_df = pd.read_sql_query(
                "SELECT tema_num, COUNT(*) as total FROM preguntas GROUP BY tema_num", conn
            )
            conn.close()
            st.dataframe(stats_df.rename(columns={"tema_num": "Tema", "total": "Preguntas"}),
                         hide_index=True, use_container_width=True)

        st.divider()

        col_b1, col_b2 = st.columns([3, 1])
        with col_b1:
            if st.button("🚀 Comenzar simulacro", type="primary", use_container_width=True):
                if not temas_elegidos:
                    st.error("⚠️ Selecciona al menos un tema.")
                else:
                    df = cargar_preguntas(temas_elegidos, dificultad_sel)
                    if df.empty:
                        st.error("No hay preguntas disponibles con los filtros seleccionados.")
                    else:
                        st.session_state.quiz_data = df
                        st.session_state.indice = 0
                        st.session_state.respuestas = []
                        st.session_state.feedback = None
                        st.session_state.tiempo_inicio_estudio = datetime.now()
                        st.rerun()
        with col_b2:
            if st.button("⬅️ Volver al menú", use_container_width=True):
                st.session_state.modo = None
                st.rerun()
        st.stop()

    # Quiz activo (modo estudio)
    total = len(st.session_state.quiz_data)
    indice = st.session_state.indice

    with st.sidebar:
        st.title("📈 Progreso")
        avance = indice / total if total > 0 else 0
        st.progress(avance, text=f"Pregunta {indice + 1} de {total}")

        correctas_hasta_ahora = sum(1 for r in st.session_state.respuestas if r["es_correcta"])
        if indice > 0:
            pct = correctas_hasta_ahora / indice * 100
            st.metric("Aciertos acumulados", f"{correctas_hasta_ahora}/{indice}", f"{pct:.0f}%")

        if st.button("🏁 Terminar y ver resultados"):
            st.session_state.indice = total
            st.rerun()

        st.divider()
        if st.button("🚪 Abandonar simulacro", use_container_width=True,
                     help="Salir sin guardar resultados"):
            for k in ["quiz_data", "indice", "respuestas", "feedback", "tiempo_inicio_estudio"]:
                st.session_state.pop(k, None)
            claves_rand = [k for k in st.session_state if k.startswith("opciones_") or k.startswith("radio_")]
            for k in claves_rand:
                del st.session_state[k]
            st.session_state.modo = None
            st.rerun()

    if indice < total:
        p = st.session_state.quiz_data.iloc[indice]
        key = f"opciones_{p['id']}"

        col_t, col_d = st.columns([3, 1])
        with col_t:
            st.markdown(
                f'<span class="tema-badge">📚 Tema {p["tema_num"]}: {p["tema_titulo"]}</span>',
                unsafe_allow_html=True
            )
        with col_d:
            st.markdown(
                f"{badge_dificultad(p['dificultad'])} **{p['dificultad'].capitalize()}** · p.{p['pagina_manual']}",
                unsafe_allow_html=True
            )

        st.divider()
        st.markdown(f'<div class="pregunta-box">❓ {p["enunciado"]}</div>', unsafe_allow_html=True)

        if st.session_state.feedback:
            st.error(st.session_state.feedback["mensaje"])
            st.info(f"📖 **Justificación del manual:** {p['justificacion']}")
            if st.button("✅ Entendido, continuar", type="primary"):
                st.session_state.feedback = None
                st.session_state.indice += 1
                st.rerun()
        else:
            opciones = mezclar_opciones(p, key)
            seleccion = st.radio("Selecciona tu respuesta:", opciones, key=f"radio_{indice}")

            if st.button("✔️ Validar respuesta", type="primary"):
                es_correcta = (seleccion == p["correcta"])
                st.session_state.respuestas.append({
                    "tema_num": p["tema_num"],
                    "tema": p["tema_titulo"],
                    "dificultad": p["dificultad"],
                    "es_correcta": es_correcta,
                })

                if es_correcta:
                    st.success(f"✅ ¡Correcto! {p['justificacion']}")
                    st.session_state.indice += 1
                    st.rerun()
                else:
                    st.session_state.feedback = {
                        "mensaje": f"❌ Incorrecto. La respuesta correcta es: **{p['correcta']}**"
                    }
                    st.rerun()
    else:
        # Dashboard de resultados modo estudio
        # Guardia: si no hay tiempo de inicio, el simulacro fue abandonado/corrompido
        if "tiempo_inicio_estudio" not in st.session_state:
            for k in ["quiz_data", "indice", "respuestas", "feedback"]:
                st.session_state.pop(k, None)
            st.session_state.modo = None
            st.rerun()

        st.balloons()
        st.title("🎓 Resultados del Simulacro - Modo Estudio")

        if not st.session_state.respuestas:
            st.warning("No respondiste ninguna pregunta.")
            if st.button("🔄 Volver al inicio"):
                for k in ["quiz_data", "indice", "respuestas", "feedback"]:
                    st.session_state.pop(k, None)
                st.session_state.modo = None
                st.rerun()
            st.stop()

        res_df = pd.DataFrame(st.session_state.respuestas)
        nota = res_df["es_correcta"].mean() * 100
        total_r = len(res_df)
        ok = res_df["es_correcta"].sum()
        
        # Calcular tiempo usado
        tiempo_usado = (datetime.now() - st.session_state.tiempo_inicio_estudio).total_seconds()

        # Guardar en historial
        stats_tema = res_df.groupby("tema")["es_correcta"].mean() * 100
        guardar_historial('estudio', float(nota), int(tiempo_usado), int(ok), int(total_r), stats_tema.to_dict())

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🏆 Calificación", f"{nota:.1f}%")
        c2.metric("✅ Correctas", f"{ok}")
        c3.metric("❌ Incorrectas", f"{total_r - ok}")
        c4.metric("⏱️ Tiempo", formatear_tiempo(tiempo_usado))

        st.divider()

        st.subheader("📊 Desempeño por tema")
        stats_tema = (
            res_df.groupby("tema")["es_correcta"]
            .agg(correctas="sum", total="count")
            .assign(porcentaje=lambda x: (x["correctas"] / x["total"] * 100).round(1))
            .reset_index()
        )
        st.bar_chart(stats_tema.set_index("tema")["porcentaje"])
        st.dataframe(
            stats_tema.rename(columns={"tema": "Tema", "correctas": "Correctas",
                                       "total": "Total", "porcentaje": "% Aciertos"}),
            hide_index=True, use_container_width=True
        )

        debiles = stats_tema[stats_tema["porcentaje"] < 70]
        if not debiles.empty:
            st.subheader("⚠️ Áreas de refuerzo recomendadas")
            for _, row in debiles.iterrows():
                st.error(
                    f"📌 **{row['tema']}** — {row['porcentaje']}% ({int(row['correctas'])}/{int(row['total'])})"
                )

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Nuevo simulacro", type="primary", use_container_width=True):
                for k in ["quiz_data", "indice", "respuestas", "feedback", "tiempo_inicio_estudio"]:
                    st.session_state.pop(k, None)
                claves_rand = [k for k in st.session_state if k.startswith("opciones_") or k.startswith("radio_")]
                for k in claves_rand:
                    del st.session_state[k]
                st.rerun()
        with col2:
            if st.button("⬅️ Volver al menú", use_container_width=True):
                for k in ["quiz_data", "indice", "respuestas", "feedback", "tiempo_inicio_estudio"]:
                    st.session_state.pop(k, None)
                st.session_state.modo = None
                st.rerun()

# ============================================================
# 7. MODO EXAMEN
# ============================================================
elif st.session_state.modo == 'examen':
    
    total = len(st.session_state.quiz_data)
    indice = st.session_state.indice
    
    # Calcular tiempo
    tiempo_transcurrido = (datetime.now() - st.session_state.tiempo_inicio).total_seconds()
    tiempo_restante = st.session_state.tiempo_limite_seg - tiempo_transcurrido
    
    # Auto-envío si se acaba el tiempo
    if tiempo_restante <= 0 and indice < total:
        st.session_state.modo = 'resultados_examen'
        st.session_state.tiempo_usado_examen = st.session_state.tiempo_limite_seg
        st.rerun()
    
    # Sidebar con cronómetro y navegación
    with st.sidebar:
        st.markdown("### ⏱️ Tiempo Restante")
        mins, secs = divmod(int(tiempo_restante), 60)
        
        if mins < 10:
            st.markdown(f'<div class="timer-warning">⚠️ {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="timer-ok">✅ {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 📊 Progreso")
        respondidas = len(st.session_state.respuestas_examen)
        marcadas = len(st.session_state.marcadas)
        sin_responder = total - respondidas - marcadas
        
        # Métricas detalladas
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("🟢 Respondidas", f"{respondidas}/{total}")
            st.metric("⭐ Marcadas", marcadas)
        with col_m2:
            st.metric("⚪ Sin tocar", sin_responder)
            pct_completo = ((respondidas + marcadas) / total * 100)
            st.metric("Avance", f"{pct_completo:.0f}%")
        
        st.progress(respondidas / total, text=f"Respondidas: {respondidas}/{total}")
        
        # Advertencia si hay muchas sin tocar
        if sin_responder > 10 and (respondidas + marcadas) > 20:
            st.warning(f"⚠️ {sin_responder} preguntas sin tocar")
        
        st.divider()
        
        # Botón de abandonar examen
        st.markdown("### ⚠️ Acciones")
        if st.button("🚪 Abandonar Examen", use_container_width=True, help="Salir sin guardar resultados"):
            st.session_state.mostrar_confirmacion_salida = True
            st.rerun()
        
        # Confirmación de abandono
        if st.session_state.get('mostrar_confirmacion_salida', False):
            st.warning("⚠️ **¿Salir sin guardar?**")
            st.markdown("Se perderá todo el progreso.")
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                if st.button("✅ Sí, salir", key="confirm_exit"):
                    for k in ['quiz_data', 'indice', 'respuestas_examen', 'marcadas', 
                              'tiempo_inicio', 'mostrar_confirmacion', 'mostrar_confirmacion_salida']:
                        st.session_state.pop(k, None)
                    claves = [k for k in st.session_state if k.startswith("opciones_") or k.startswith("radio_")]
                    for k in claves:
                        del st.session_state[k]
                    st.session_state.modo = None
                    st.rerun()
            with col_s2:
                if st.button("❌ No", key="cancel_exit"):
                    st.session_state.mostrar_confirmacion_salida = False
                    st.rerun()
        
        st.divider()
        st.markdown("### 🗺️ Navegación Rápida")
        st.caption("🟢 Respondida | ⭐ Marcada | ⚪ Sin responder")
        
        # Mapa de navegación mejorado
        cols_nav = st.columns(6)
        for i in range(min(total, 66)):
            col_idx = i % 6
            with cols_nav[col_idx]:
                # Determinar estado de la pregunta
                respondida = i in st.session_state.respuestas_examen
                marcada = i in st.session_state.marcadas
                
                if respondida:
                    estado = "🟢"
                elif marcada:
                    estado = "⭐"
                else:
                    estado = "⚪"
                
                # Marcar pregunta actual
                if i == indice:
                    label = f"**[{i+1}]**"
                else:
                    label = f"{estado} {i+1}"
                
                if st.button(label, key=f"nav_{i}", use_container_width=True):
                    st.session_state.indice = i
                    st.rerun()
    
    if indice < total:
        p = st.session_state.quiz_data.iloc[indice]
        key = f"opciones_{p['id']}"
        
        # Mensaje informativo al inicio (solo en primera pregunta)
        if indice == 0 and not st.session_state.get('info_mostrada', False):
            st.info("""
            📌 **Importante:** Para avanzar a la siguiente pregunta debes:
            - ✅ Seleccionar una respuesta, **O**
            - ⭐ Marcar la pregunta (si no sabes la respuesta)
            
            💡 Las preguntas marcadas con ⭐ aparecen en el mapa de navegación para que las revises al final.
            """)
            st.session_state.info_mostrada = True
        
        # Cabecera
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"### Pregunta {indice + 1} de {total}")
        with col2:
            st.markdown(f"**Tema {p['tema_num']}** · {badge_dificultad(p['dificultad'])}")
        with col3:
            marcada = indice in st.session_state.marcadas
            if st.button("⭐ Marcar" if not marcada else "✅ Desmarca", key=f"mark_{indice}"):
                if marcada:
                    st.session_state.marcadas.remove(indice)
                else:
                    st.session_state.marcadas.add(indice)
                st.rerun()
        
        st.divider()
        st.markdown(f'<div class="pregunta-box">❓ {p["enunciado"]}</div>', unsafe_allow_html=True)
        
        opciones = mezclar_opciones(p, key)
        
        # Mostrar respuesta previa si existe
        respuesta_previa = st.session_state.respuestas_examen.get(indice)
        default_index = opciones.index(respuesta_previa) if respuesta_previa in opciones else 0
        
        seleccion = st.radio(
            "Selecciona tu respuesta:",
            opciones,
            key=f"radio_examen_{indice}",
            index=default_index if respuesta_previa else None
        )
        
        # Guardar respuesta automáticamente
        if seleccion:
            st.session_state.respuestas_examen[indice] = seleccion
        
        st.divider()
        
        # Navegación
        col_prev, col_next, col_finish = st.columns([1, 1, 2])
        with col_prev:
            if indice > 0:
                if st.button("⬅️ Anterior", use_container_width=True):
                    st.session_state.indice -= 1
                    st.rerun()
        with col_next:
            if indice < total - 1:
                if st.button("Siguiente ➡️", use_container_width=True, type="primary"):
                    # VALIDACIÓN: Debe responder o marcar antes de avanzar
                    respondida = indice in st.session_state.respuestas_examen
                    marcada = indice in st.session_state.marcadas
                    
                    if not respondida and not marcada:
                        st.error("⚠️ **Debes seleccionar una respuesta o marcar esta pregunta (⭐) antes de avanzar.**")
                        st.info("💡 Si no sabes la respuesta, márcala con ⭐ para revisarla después.")
                    else:
                        st.session_state.indice += 1
                        st.rerun()
        with col_finish:
            if st.button("🏁 Finalizar Examen", use_container_width=True, type="primary"):
                st.session_state.mostrar_confirmacion = True
                st.rerun()
        
        # Mostrar confirmación de finalización
        if st.session_state.get('mostrar_confirmacion', False):
            st.divider()
            sin_responder = total - len(st.session_state.respuestas_examen)
            
            if sin_responder > 0:
                st.warning(f"⚠️ **Tienes {sin_responder} preguntas sin responder.**")
                st.info("💡 Puedes continuar respondiendo o enviar el examen ahora.")
            else:
                st.success("✅ **Has respondido todas las preguntas.**")
            
            st.markdown("### ¿Qué deseas hacer?")
            
            col_confirm1, col_confirm2, col_confirm3 = st.columns(3)
            
            with col_confirm1:
                if st.button("✅ Enviar Examen", use_container_width=True, type="primary"):
                    st.session_state.modo = 'resultados_examen'
                    st.session_state.tiempo_usado_examen = int(tiempo_transcurrido)
                    st.session_state.mostrar_confirmacion = False
                    st.rerun()
            
            with col_confirm2:
                if st.button("↩️ Seguir Respondiendo", use_container_width=True):
                    st.session_state.mostrar_confirmacion = False
                    st.rerun()
            
            with col_confirm3:
                if st.button("🚪 Salir sin Guardar", use_container_width=True):
                    # Limpiar todo el estado del examen
                    for k in ['quiz_data', 'indice', 'respuestas_examen', 'marcadas', 
                              'tiempo_inicio', 'mostrar_confirmacion']:
                        st.session_state.pop(k, None)
                    claves = [k for k in st.session_state if k.startswith("opciones_") or k.startswith("radio_")]
                    for k in claves:
                        del st.session_state[k]
                    st.session_state.modo = None
                    st.rerun()

# ============================================================
# 8. RESULTADOS EXAMEN
# ============================================================
elif st.session_state.modo == 'resultados_examen':
    st.balloons()
    st.title("🎯 Resultados del Examen Real")
    
    total = len(st.session_state.quiz_data)
    respuestas = st.session_state.respuestas_examen
    
    # Evaluar respuestas
    correctas = 0
    incorrectas_detalle = []
    
    for i in range(total):
        p = st.session_state.quiz_data.iloc[i]
        respuesta_usuario = respuestas.get(i)
        
        if respuesta_usuario == p["correcta"]:
            correctas += 1
        else:
            incorrectas_detalle.append({
                "pregunta_num": i + 1,
                "tema": p["tema_titulo"],
                "enunciado": p["enunciado"],
                "tu_respuesta": respuesta_usuario if respuesta_usuario else "Sin responder",
                "correcta": p["correcta"],
                "justificacion": p["justificacion"]
            })
    
    calificacion = (correctas / total) * 100
    tiempo_usado = st.session_state.tiempo_usado_examen
    aprobado = calificacion >= 70
    
    # Guardar en historial
    df_temp = st.session_state.quiz_data.copy()
    df_temp['respondida'] = df_temp.index.map(lambda i: respuestas.get(i) == df_temp.iloc[i]["correcta"])
    stats_por_tema = df_temp.groupby('tema_titulo')['respondida'].mean() * 100
    guardar_historial('examen', calificacion, tiempo_usado, correctas, total, stats_por_tema.to_dict())
    
    # Métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🎯 Calificación", f"{calificacion:.1f}%")
    col2.metric("✅ Correctas", f"{correctas}/{total}")
    col3.metric("❌ Incorrectas", len(incorrectas_detalle))
    col4.metric("⏱️ Tiempo", formatear_tiempo(tiempo_usado))
    col5.metric("📊 Estado", "APROBADO ✅" if aprobado else "REPROBADO ❌")
    
    if aprobado:
        st.success(f"🎉 ¡Felicitaciones! Has aprobado con {calificacion:.1f}%")
    else:
        st.error(f"📚 Necesitas más preparación. Obtuviste {calificacion:.1f}% (mínimo 70%)")
    
    st.divider()
    
    # Estadísticas por tema
    st.subheader("📊 Desempeño por Tema")
    stats_tema = (
        df_temp.groupby('tema_titulo')
        .agg(
            total_preguntas=('respondida', 'count'),
            correctas=('respondida', 'sum')
        )
        .assign(porcentaje=lambda x: (x['correctas'] / x['total_preguntas'] * 100).round(1))
        .reset_index()
    )
    st.bar_chart(stats_tema.set_index('tema_titulo')['porcentaje'])
    st.dataframe(
        stats_tema.rename(columns={
            'tema_titulo': 'Tema',
            'total_preguntas': 'Total',
            'correctas': 'Correctas',
            'porcentaje': '% Aciertos'
        }),
        hide_index=True,
        use_container_width=True
    )
    
    # Áreas críticas
    debiles = stats_tema[stats_tema['porcentaje'] < 70]
    if not debiles.empty:
        st.subheader("⚠️ Áreas Críticas (< 70%)")
        for _, row in debiles.iterrows():
            st.error(
                f"📌 **{row['tema_titulo']}**: {row['porcentaje']:.1f}% "
                f"({int(row['correctas'])}/{int(row['total_preguntas'])})"
            )
    
    st.divider()
    
    # Preguntas incorrectas
    if incorrectas_detalle:
        with st.expander(f"❌ Ver {len(incorrectas_detalle)} Preguntas Incorrectas", expanded=False):
            for item in incorrectas_detalle:
                st.markdown(f"""
                **Pregunta {item['pregunta_num']}** - {item['tema']}
                
                **Enunciado:** {item['enunciado']}
                
                ❌ **Tu respuesta:** {item['tu_respuesta']}  
                ✅ **Respuesta correcta:** {item['correcta']}
                
                📖 **Justificación:** {item['justificacion']}
                """)
                st.divider()
    
    st.divider()
    
    # Historial de intentos
    historial_df = cargar_historial()
    if len(historial_df) > 1:
        st.subheader("📈 Tu Progreso en Exámenes")
        examenes = historial_df[historial_df['modo'] == 'examen'].head(5)
        if not examenes.empty:
            st.line_chart(examenes.set_index('fecha')['calificacion'])
            
            mejora = examenes.iloc[0]['calificacion'] - examenes.iloc[-1]['calificacion']
            if mejora > 0:
                st.success(f"📈 Has mejorado {mejora:.1f}% desde tu primer intento")
            elif mejora < 0:
                st.info(f"📊 Tuviste una disminución de {abs(mejora):.1f}% - sigue practicando")
    
    st.divider()
    
    # Acciones
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Nuevo Examen", use_container_width=True, type="primary"):
            # Limpiar estado
            for k in ['quiz_data', 'indice', 'respuestas_examen', 'marcadas', 
                      'tiempo_inicio', 'tiempo_usado_examen']:
                st.session_state.pop(k, None)
            claves = [k for k in st.session_state if k.startswith("opciones_") or k.startswith("radio_")]
            for k in claves:
                del st.session_state[k]
            st.session_state.modo = None
            st.rerun()
    with col2:
        if st.button("📚 Modo Estudio", use_container_width=True):
            for k in ['quiz_data', 'indice', 'respuestas_examen', 'marcadas', 
                      'tiempo_inicio', 'tiempo_usado_examen']:
                st.session_state.pop(k, None)
            st.session_state.modo = 'estudio'
            st.rerun()
    with col3:
        if st.button("⬅️ Menú Principal", use_container_width=True):
            for k in ['quiz_data', 'indice', 'respuestas_examen', 'marcadas', 
                      'tiempo_inicio', 'tiempo_usado_examen']:
                st.session_state.pop(k, None)
            st.session_state.modo = None
            st.rerun()
