import streamlit as st
import pandas as pd
import os
import json
import numpy as np
from clases_funciones import plot_score_matrix  # sin uso actual
from api_live import (
    obtener_partidos_en_vivo,
    buscar_partido,
    obtener_estadisticas
)
#xddddd
def obtener_escudo(equipo):

    escudos = {

        # América
        "America": "america",
        "América": "america",

        # Atlas
        "Atlas": "atlas",

        # Atlético San Luis
        "Atlético San Luis": "atleticosl",

        # Cruz Azul
        "Cruz Azul": "cruzazul",

        # Guadalajara
        "Guadalajara": "guadalajara",

        # Juárez
        "FC Juárez": "juarez",

        # León
        "Leon": "leon",
        "León": "leon",

        # Mazatlán
        "Mazatlan": "mazatlan",
        "Mazatlán": "mazatlan",

        # Monterrey
        "Monterrey": "monterrey",

        # Necaxa
        "Necaxa": "necaxa",

        # Pachuca
        "Pachuca": "pachuca",

        # Puebla
        "Puebla": "puebla",

        # Pumas
        "UNAM": "pumas",

        # Querétaro
        "Querétaro": "queretaro",

        # Santos
        "Santos Laguna": "santos",

        # Tigres
        "UANL": "tigres",

        # Tijuana
        "Tijuana": "tijuana",

        # Toluca
        "Toluca": "toluca",
        # Atlante
        "Atlante": "atlante"

    }

    archivo = escudos.get(equipo)

    if archivo is None:
        return None

    ruta = os.path.join("escudos", f"{archivo}.png")

    if os.path.exists(ruta):
        return ruta

    return None
def nombre_equipo(equipo):

    nombres = {

        "America": "América",
        "América": "América",

        "FC Juárez": "Juárez",

        "UNAM": "Pumas",

        "UANL": "Tigres",

        "Leon": "León",

        "Mazatlan": "Mazatlán"

    }

    return nombres.get(equipo, equipo)

st.set_page_config(
    page_title="Liga MX Predictor",
    page_icon="⚽",
    layout="wide"
)


# ===== CSS PERSONALIZADO =====
st.markdown("""
<style>
    /* Fondo general */
    .stApp {
        background: linear-gradient(180deg, #0f2027 0%, #203a43 55%, #2c5364 100%);
        color: #eaf2f5;
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    }

    /* Panel principal con tarjetas */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Tarjeta del partido */
    .partido-card {
        background: linear-gradient(135deg, rgba(28, 58, 70, 0.92) 0%, rgba(18, 38, 48, 0.95) 100%);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.6rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.45);
    }

    /* Marcador grande */
    .marcador-grande {
        text-align:center;
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #f7971e, #ffd200);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    /* Etiquetas de sección */
    .seccion-titulo {
        color: #8fd3f4;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        border-left: 4px solid #f7971e;
        padding-left: 10px;
        margin-top: 1.4rem;
        margin-bottom: 0.6rem;
    }

    /* Over/Under - ambos del mismo tamaño */
    .ou-lado {
        font-size: 1.0rem;
        font-weight: 700;
    }
    .ou-over { color: #4ade80; }
    .ou-under { color: #f87171; }
    .ou-caja {
        background: rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 0.5rem 0.3rem;
        text-align: center;
    }

    /* Probabilidades */
    .prob-valor { font-size: 2rem; font-weight: 800; }
    .prob-momio { font-size: 1.1rem; color: #a0aec0; }
    .prob-etiqueta { color: #cbd5e0; font-weight: 600; }

    /* Header partido */
    .header-equipo {
        text-align:center;
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
    }

    /* caption mas legible */
    .small-meta { color: #8b9ba8; font-size: 0.85rem; }

    /* Tabla top 5 compacta */
    .top5-table { font-size: 0.95rem; }

    /* Barra de probabilidad apilada (Local/Empate/Visitante) */
    .barra-wrapper {
        margin-top: 0.8rem;
        margin-bottom: 0.4rem;
    }
    .barra-linea {
        display: flex;
        width: 100%;
        height: 22px;
        border-radius: 12px;
        overflow: hidden;
        background: rgba(255,255,255,0.06);
    }
    .barra-seg {
        height: 100%;
    }
    .leyenda {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    .leyenda span b { font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
# Acerca del proyecto
Este proyecto implementa desde cero modelos para la predicción de partidos de la Liga MX.

El desarrollo fue realizado como proyecto personal con fin educativo para profundizar en:

- Machine Learning
- Modelos de Poisson
- Inferencia Bayesiana
- Optimización Numérica
- Modelado Estadístico Deportivo

**Las predicciones no constituyen recomendaciones de apuesta.**
""")
st.markdown("""
## Ya estan actualizados las predicciones de la J3!!!!
### Las estadisticas en vivo aparecen solo durante el partido una vez acaba el partido ya no se puedeen consultar
""")

c1, c2, c3 = st.columns([1,2,1])

with c2:
    st.image("escudos/ligamx.png", width=250)

st.title("⚽ Predicción de partidos Liga MX")

predicciones = pd.read_csv(
    "data/predicciones.csv"
)

predicciones["fecha"] = pd.to_datetime(
    predicciones["fecha"]
)



jornada = st.selectbox(

    "Selecciona la jornada",

    sorted(predicciones["jornada"].unique()))

st.subheader(f"Jornada {jornada}")

st.divider()





def mostrar_partido(partido, partidos_live):
    local = partido["local"]

    visitante = partido["visitante"]
    live = buscar_partido(partidos_live, local,visitante)
   
    
    stats = None

    if live is not None:
        stats = obtener_estadisticas(live["fixture"])
       
    fecha = partido["fecha"]

    # Metadatos del partido
    estado_txt = "Partido pendiente" if pd.isna(partido["resultado_local"]) else "Partido finalizado"
    st.markdown(
        f'<div class="small-meta" style="text-align:center;margin-top:1.5rem;">'
        f'📅 {fecha.strftime("%d/%m/%Y")} &nbsp;·&nbsp; {estado_txt}</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1.15, 0.6, 1.15], vertical_alignment="center")

    with col1:
        escudo_local = obtener_escudo(local)
        if escudo_local is not None:
            cola, colon, colb = st.columns([1, 2, 1])
            colon.image(escudo_local, width=140)
        st.markdown(
            f'<div class="header-equipo">{nombre_equipo(local)}</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown('<div style="text-align:center;font-size:1.6rem;font-weight:800;color:#f7971e;">VS</div>', unsafe_allow_html=True)

    with col3:
        escudo_visitante = obtener_escudo(visitante)
        if escudo_visitante is not None:
            cola2, colon2, colb2 = st.columns([1, 2, 1])
            colon2.image(escudo_visitante, width=140)
        st.markdown(
            f'<div class="header-equipo">{nombre_equipo(visitante)}</div>',
            unsafe_allow_html=True
        )

    st.divider() 
    
    if live is not None:

     estado = {
        "NS": "No iniciado",
        "1H": "Primer tiempo",
        "HT": "Descanso",
        "2H": "Segundo tiempo",
        "ET": "Tiempo extra",
        "BT": "Descanso T.E.",
        "P": "Penales",
        "FT": "Finalizado"
    }

     st.markdown("""
    <h2 style="
        text-align:center;
        color:#ff4b4b;
        margin-top:25px;
        margin-bottom:20px;">
        🔴 EN VIVO
    </h2>
    """, unsafe_allow_html=True)

     st.markdown(
    f"""<div style="text-align:center;"><h1 style="font-size:70px; margin:0; color:white;">{live['goles_local']} - {live['goles_visitante']}</h1><h3 style="color:#BBBBBB; margin-top:8px;">{live['minuto']}'</h3><p style="color:#999999; font-size:18px; margin-top:0;">{estado.get(live['estado'], live['estado'])}</p></div>""",unsafe_allow_html=True)
     st.divider()
    
    
    
    
    if stats is not None:
         local_stats = {}
         visitante_stats = {}

    
         for s in stats[0]["statistics"]:
             local_stats[s["type"]] = s["value"]

         for s in stats[1]["statistics"]:
             visitante_stats[s["type"]] = s["value"]



         st.markdown("### Estadísticas")

         filas = [
        ("Ball Possession","Posesión"),
        ("Total Shots","Tiros"),
        ("Shots on Goal","A puerta"),
        ("Corner Kicks","Corners"),
        ("Yellow Cards","Amarillas"),
        ("Red Cards","Rojas"),
        ("Offsides","Fuera de lugar"),
        ("Goalkeeper Saves","Atajadas"),]

         for api, nombre in filas:
             c1, c2, c3 = st.columns([2,2,2])
             with c1:
                 st.markdown(f"""
                             <h3 style="text-align:right">{local_stats.get(api,'-')}</h3>""",
                             unsafe_allow_html=True)

             with c2:
                st.markdown(
        f"""
        <div style="
            text-align:center;
            color:#BBBBBB;
            font-size:18px;">
            {nombre}
        </div>
        """,
        unsafe_allow_html=True
    )

             with c3:
                 st.markdown(
        f"""
        <h3 style="text-align:left">
        {visitante_stats.get(api,'-')}
        </h3>
        """,
        unsafe_allow_html=True
    )
     
     
    lam = partido["xg_local"]
    mu = partido["xg_visitante"]
    marcador = (int(partido["pred_local"]), int(partido["pred_visitante"]))
    _total = lam + mu

    prob_local = partido["prob_local"]
    prob_empate = partido["prob_empate"]
    prob_visitante = partido["prob_visitante"]
    momio_local = partido["momio_local"]
    momio_empate = partido["momio_empate"]
    momio_visitante = partido["momio_visitante"]

    # Matriz de probabilidades (se reutiliza en marcador, over/under y top5)
    matriz = np.array(json.loads(partido["matriz"]))

    # ===== TARJETA DEL PARTIDO =====
    st.markdown('<div class="partido-card">', unsafe_allow_html=True)

    # --- Marcador más probable ---
    _prob_marcador = matriz[marcador[0], marcador[1]]
    st.markdown(
        f'<div class="seccion-titulo" style="text-align:center;">Marcador más probable</div>'
        f'<p class="marcador-grande">{nombre_equipo(local)} '
        f'<span style="color:#8b9ba8;">{marcador[0]} - {marcador[1]}</span> '
        f'{nombre_equipo(visitante)}</p>'
        f'<div class="small-meta" style="text-align:center;margin-top:0.2rem;">'
        f'Probabilidad <b style="color:#f7971e;">{_prob_marcador:.1%}</b></div>',
        unsafe_allow_html=True
    )

    # --- Probabilidades y momios (al inicio) ---
    c1, c2, c3 = st.columns(3)

    for col, etiqueta, prob, momio in [
        (c1, nombre_equipo(local), prob_local, momio_local),
        (c2, "Empate", prob_empate, momio_empate),
        (c3, nombre_equipo(visitante), prob_visitante, momio_visitante)
    ]:
        with col:
            st.markdown(
                f'<div class="prob-etiqueta">{etiqueta}</div>'
                f'<div class="prob-valor" style="text-align:center">{prob:.1%}</div>'
                f'<div class="prob-momio" style="text-align:center">Momio {momio:+.0f}</div>',
                unsafe_allow_html=True
            )

    # --- Barra de probabilidad apilada: Local / Empate / Visitante ---
    _pl = float(prob_local)
    _pe = float(prob_empate)
    _pv = float(prob_visitante)
    st.markdown(
        f'<div class="barra-wrapper">'
        f'<div class="barra-linea">'
        f'<div class="barra-seg" style="width:{_pl*100:.1f}%;background:#4ade80;"></div>'
        f'<div class="barra-seg" style="width:{_pe*100:.1f}%;background:#facc15;"></div>'
        f'<div class="barra-seg" style="width:{_pv*100:.1f}%;background:#f87171;"></div>'
        f'</div>'
        f'<div class="leyenda">'
        f'<span style="color:#4ade80;">Local <b>{_pl:.1%}</b></span>'
        f'<span style="color:#facc15;">Empate <b>{_pe:.1%}</b></span>'
        f'<span style="color:#f87171;">Visita <b>{_pv:.1%}</b></span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # --- Resultado final (si el partido ya terminó) ---
    if not pd.isna(partido["resultado_local"]):
        rl = int(partido["resultado_local"])
        rv = int(partido["resultado_visitante"])

        pred_local = marcador[0]
        pred_visitante = marcador[1]

        if prob_local >= prob_empate and prob_local >= prob_visitante:
            signo_pred = 1
        elif prob_visitante >= prob_local and prob_visitante >= prob_empate:
            signo_pred = -1
        else:
            signo_pred = 0

        signo_real = np.sign(rl - rv)

        if pred_local == rl and pred_visitante == rv:
            st.success(f"✅ Marcador exacto | Final: {nombre_equipo(local)} {rl} - {rv} {nombre_equipo(visitante)}")
        elif signo_pred == signo_real:
            st.warning(f"🟡 Se acertó el ganador | Final: {nombre_equipo(local)} {rl} - {rv} {nombre_equipo(visitante)}")
        else:
            st.error(f"❌ Predicción incorrecta | Final: {nombre_equipo(local)} {rl} - {rv} {nombre_equipo(visitante)}")

    # ===== OVER / UNDER =====
    matriz_ou = matriz
    _it = np.nditer(matriz_ou, flags=["multi_index"])
    _tuplas = []
    for _val in _it:
        _tuplas.append(_it.multi_index)

    def _prob_over(umbral):
        return sum(matriz_ou[i, j] for i, j in _tuplas if i + j > umbral)

    st.markdown('<div class="seccion-titulo">Over / Under</div>', unsafe_allow_html=True)

    oc1, oc2, oc3, oc4 = st.columns(4)
    filas_ou = [
        ("2.5", _prob_over(2.5)),
        ("1.5", _prob_over(1.5)),
        ("0.5", _prob_over(0.5)),
    ]

    for col, (umbral, prob_over) in zip([oc1, oc2, oc3], filas_ou):
        prob_over = min(prob_over, 1.0)
        prob_under = max(1 - prob_over, 0.0)
        with col:
            st.markdown(
                f'<div class="ou-caja">'
                f'<div class="ou-lado ou-over">Over {umbral} &nbsp; {prob_over:.0%}</div>'
                f'<div class="ou-lado ou-under">Under {umbral} &nbsp; {prob_under:.0%}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    with oc4:
        st.markdown(
            f'<div class="ou-caja">'
            f'<div class="ou-lado" style="color:#8fd3f4;">Goles esperados</div>'
            f'<div class="ou-lado" style="color:#eaf2f5;">Local <b>{lam:.2f}</b> · Vis <b>{mu:.2f}</b></div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # ===== TOP 5 MARCADORES =====
    st.markdown('<div class="seccion-titulo">Top 5 marcadores más probables</div>', unsafe_allow_html=True)

    _flat_idx = np.argsort(matriz_ou, axis=None)[::-1][:5]
    _top = []
    for _k in _flat_idx:
        _gl, _gv = np.unravel_index(_k, matriz_ou.shape)
        _top.append({
            "Marcador": f"{nombre_equipo(local)} {_gl} - {_gv} {nombre_equipo(visitante)}",
            "Probabilidad": f"{matriz_ou[_gl, _gv]:.1%}"
        })

    st.dataframe(
        pd.DataFrame(_top),
        hide_index=True,
        use_container_width=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


partidos_live = obtener_partidos_en_vivo()

partidos = predicciones[
    predicciones["jornada"] == jornada
]

for _, partido in partidos.iterrows():

    mostrar_partido(
        partido,
        partidos_live
    )



