import streamlit as st
import sqlite3
import random
import pandas as pd
from banco_preguntas import BANCO_COMPLETO

# ============================================================
# 1. MOTOR DE BASE DE DATOS
# ============================================================
DB_PATH = "dgsc_pro.db"

def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Schema extendido con columnas de analítica
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

    # Solo insertar si la tabla está vacía (evita duplicados en reinicios)
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

    conn.close()

# ============================================================
# 2. HELPERS
# ============================================================
def cargar_preguntas(temas_seleccionados=None, dificultad=None):
    """Carga y devuelve las preguntas filtradas y mezcladas."""
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
    return df.sample(frac=1).reset_index(drop=True)

def mezclar_opciones(row, key):
    """Mezcla las cuatro opciones de manera reproducible por pregunta."""
    if key not in st.session_state:
        opciones = [row["correcta"], row["d1"], row["d2"], row["d3"]]
        random.shuffle(opciones)
        st.session_state[key] = opciones
    return st.session_state[key]

def badge_dificultad(nivel):
    colores = {"basico": "🟢", "intermedio": "🟡", "avanzado": "🔴"}
    return colores.get(nivel, "⚪")

# ============================================================
# 3. CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="Simulador DGSC",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stRadio > div { gap: 0.5rem; }
    div[data-testid="metric-container"] { background:#f0f4ff; border-radius:8px; padding:0.5rem 1rem; }
    .tema-badge { background:#1a3a6b; color:white; padding:4px 12px;
                  border-radius:12px; font-size:0.85rem; font-weight:600; }
    .pregunta-box { background:#f8f9fa; border-left:4px solid #1a3a6b;
                    padding:1rem 1.5rem; border-radius:0 8px 8px 0;
                    font-size:1.05rem; margin-bottom:1rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 4. INICIALIZACIÓN
# ============================================================
inicializar_db()

TEMAS_INFO = {
    "1": "Generalidades del Estado de Derecho",
    "2": "La Administración Pública Costarricense",
    "3": "Normas Básicas para la Función Pública",
    "4": "El Régimen de Servicio Civil en Costa Rica",
    "5": "Ética y Valores en la Función Pública",
    "6": "Competencias Requeridas para Directivos Públicos",
    "7": "Elementos de Administración y Tendencias",
    "SIGLAS": "Glosario de Siglas",
}

# ============================================================
# 5. PANTALLA DE INICIO / CONFIGURACIÓN
# ============================================================
if "quiz_data" not in st.session_state:
    st.title("🏛️ Simulador DGSC — Modo Estudio")
    st.markdown("**Dirección General de Servicio Civil | Costa Rica**")
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
        st.subheader("📊 Banco de preguntas")
        conn = sqlite3.connect(DB_PATH)
        stats_df = pd.read_sql_query(
            "SELECT tema_num, COUNT(*) as total FROM preguntas GROUP BY tema_num", conn
        )
        conn.close()
        st.dataframe(stats_df.rename(columns={"tema_num": "Tema", "total": "Preguntas"}),
                     hide_index=True, use_container_width=True)

    st.divider()

    if st.button("🚀 Comenzar simulacro", type="primary", use_container_width=True):
        if not temas_elegidos:
            st.error("⚠️ Selecciona al menos un tema.")
        else:
            df = cargar_preguntas(temas_elegidos, dificultad_sel)
            if df.empty:
                st.error("No hay preguntas disponibles con los filtros seleccionados.")
            else:
                st.session_state.quiz_data   = df
                st.session_state.indice      = 0
                st.session_state.respuestas  = []
                st.session_state.feedback    = None
                st.rerun()
    st.stop()

# ============================================================
# 6. QUIZ ACTIVO
# ============================================================
total     = len(st.session_state.quiz_data)
indice    = st.session_state.indice

# --- Sidebar de progreso ---
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

# --- Pregunta activa ---
if indice < total:
    p   = st.session_state.quiz_data.iloc[indice]
    key = f"opciones_{p['id']}"

    # Cabecera
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

    # Enunciado
    st.markdown(f'<div class="pregunta-box">❓ {p["enunciado"]}</div>', unsafe_allow_html=True)

    # Modo feedback bloqueante
    if st.session_state.feedback:
        st.error(st.session_state.feedback["mensaje"])
        st.info(f"📖 **Justificación del manual:** {p['justificacion']}")
        if st.button("✅ Entendido, continuar", type="primary"):
            st.session_state.feedback = None
            st.session_state.indice  += 1
            st.rerun()
    else:
        opciones = mezclar_opciones(p, key)
        seleccion = st.radio("Selecciona tu respuesta:", opciones, key=f"radio_{indice}")

        if st.button("✔️ Validar respuesta", type="primary"):
            es_correcta = (seleccion == p["correcta"])
            st.session_state.respuestas.append({
                "tema_num":    p["tema_num"],
                "tema":        p["tema_titulo"],
                "dificultad":  p["dificultad"],
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

# ============================================================
# 7. DASHBOARD FINAL
# ============================================================
else:
    st.balloons()
    st.title("🎓 Resultados del Simulacro")

    if not st.session_state.respuestas:
        st.warning("No respondiste ninguna pregunta.")
        if st.button("🔄 Volver al inicio"):
            for k in ["quiz_data", "indice", "respuestas", "feedback"]:
                st.session_state.pop(k, None)
            st.rerun()
        st.stop()

    res_df = pd.DataFrame(st.session_state.respuestas)
    nota   = res_df["es_correcta"].mean() * 100
    total_r = len(res_df)
    ok      = res_df["es_correcta"].sum()

    # Métricas principales
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏆 Calificación", f"{nota:.1f}%")
    c2.metric("✅ Correctas", f"{ok}")
    c3.metric("❌ Incorrectas", f"{total_r - ok}")
    c4.metric("📝 Total respondidas", f"{total_r}")

    st.divider()

    # Desempeño por tema
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

    # Desempeño por dificultad
    st.subheader("🎯 Desempeño por nivel de dificultad")
    stats_dif = (
        res_df.groupby("dificultad")["es_correcta"]
        .agg(correctas="sum", total="count")
        .assign(porcentaje=lambda x: (x["correctas"] / x["total"] * 100).round(1))
        .reset_index()
    )
    st.bar_chart(stats_dif.set_index("dificultad")["porcentaje"])

    # Áreas débiles
    st.subheader("⚠️ Áreas de refuerzo recomendadas")
    debiles = stats_tema[stats_tema["porcentaje"] < 70]
    if debiles.empty:
        st.success("🌟 ¡Excelente! No tienes áreas críticas. Todos los temas superan el 70%.")
    else:
        for _, row in debiles.iterrows():
            st.error(
                f"📌 **{row['tema']}** — {row['porcentaje']}% de aciertos "
                f"({int(row['correctas'])}/{int(row['total'])} correctas) — Requiere más estudio."
            )

    st.divider()
    if st.button("🔄 Nuevo simulacro", type="primary", use_container_width=True):
        for k in ["quiz_data", "indice", "respuestas", "feedback"]:
            st.session_state.pop(k, None)
        # Limpiar caché de opciones mezcladas
        claves_rand = [k for k in st.session_state if k.startswith("opciones_") or k.startswith("radio_")]
        for k in claves_rand:
            del st.session_state[k]
        st.rerun()
