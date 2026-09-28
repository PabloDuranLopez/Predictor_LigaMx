import streamlit as st
import pandas as pd
import os
import json
import numpy as np
from clases_funciones import plot_score_matrix  # sin uso actual
from api_live import (obtener_partidos_en_vivo,buscar_partido,obtener_estadisticas)
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


#  CSS PERSONALIZADO 
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Oswald:wght@500;600;700&display=swap');

    /* Fondo general con halos de color */
    .stApp {
        background:
            radial-gradient(900px 520px at 12% -5%, rgba(163,230,53,0.16), transparent 60%),
            radial-gradient(820px 520px at 95% 6%, rgba(245,158,11,0.14), transparent 60%),
            radial-gradient(760px 640px at 50% 118%, rgba(56,189,248,0.10), transparent 60%),
            linear-gradient(180deg, #070b16 0%, #0d1526 55%, #111e38 100%);
        background-attachment: fixed;
        color: #f8fafc;
        font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', sans-serif;
    }
    .stApp::before {
        content: "";
        position: fixed; inset: 0; pointer-events: none; opacity: 0.05; z-index: 0;
        background-image:
            linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px);
        background-size: 46px 46px;
        -webkit-mask-image: radial-gradient(circle at 50% 30%, #000, transparent 75%);
        mask-image: radial-gradient(circle at 50% 30%, #000, transparent 75%);
    }

    /* Panel principal */
    .block-container {
        position: relative; z-index: 1;
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 960px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Tarjeta del partido */
    .partido-card {
        position: relative;
        background: linear-gradient(160deg, rgba(23,35,64,0.86), rgba(12,20,38,0.92));
        border: 1px solid rgba(163, 230, 53, 0.18);
        border-radius: 22px;
        padding: 1.6rem 1.7rem;
        margin-bottom: 1.6rem;
        box-shadow: 0 24px 60px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        animation: fadeUp 0.6s ease both;
    }
    .partido-card::before {
        content: ""; position: absolute; inset: -1px; border-radius: inherit; padding: 1px; pointer-events: none;
        background: linear-gradient(135deg, rgba(163,230,53,0.55), rgba(245,158,11,0.35) 40%, transparent 70%);
        -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
    }
    .partido-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 30px 70px rgba(0,0,0,0.6), 0 0 0 1px rgba(163,230,53,0.25);
    }

    /* Marcador grande */
    .marcador-grande {
        text-align: center;
        font-family: 'Oswald', sans-serif;
        font-size: 3.4rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        background: linear-gradient(92deg, #a3e635, #fbbf24);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 6px 22px rgba(245,158,11,0.3));
        margin: 0;
    }

    /* Píldoras de sección */
    .titulo-sec { margin-top: 1.4rem; margin-bottom: 0.6rem; }
    .seccion-titulo {
        display: inline-block;
        font-family: 'Oswald', sans-serif;
        font-size: 0.74rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #d9f99d;
        padding: 0.32rem 0.85rem;
        border-radius: 999px;
        background: linear-gradient(90deg, rgba(163,230,53,0.16), rgba(245,158,11,0.12));
        border: 1px solid rgba(163,230,53,0.28);
    }

    /* Over/Under */
    .ou-lado { font-family: 'Oswald', sans-serif; font-size: 0.95rem; font-weight: 600; }
    .ou-over { color: #a3e635; }
    .ou-under { color: #fb7185; }
    .ou-caja {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 0.6rem 0.35rem;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .ou-caja:hover { transform: translateY(-3px); border-color: rgba(245,158,11,0.4); }

    /* Probabilidades */
    .prob-valor { font-family: 'Oswald', sans-serif; font-size: 1.9rem; font-weight: 700; letter-spacing: 0.5px; }
    .prob-momio { font-size: 0.78rem; color: #94a3b8; }
    .prob-etiqueta { color: #e2e8f0; font-weight: 600; font-size: 0.85rem; }

    /* Header partido */
    .header-equipo {
        text-align: center;
        font-family: 'Oswald', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        color: #ffffff;
    }

    .small-meta { color: #94a3b8; font-size: 0.85rem; }

    /* Barra de probabilidad apilada */
    .barra-wrapper { margin-top: 1.1rem; margin-bottom: 0.4rem; }
    .barra-linea {
        display: flex;
        width: 100%;
        height: 16px;
        border-radius: 999px;
        overflow: hidden;
        background: rgba(255,255,255,0.06);
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);
    }
    .barra-seg { height: 100%; position: relative; }
    .barra-seg::after {
        content: ""; position: absolute; inset: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.35), transparent);
        transform: translateX(-100%);
        animation: shimmer 2.6s infinite;
    }
    .leyenda {
        display: flex;
        justify-content: center;
        gap: 1.4rem;
        margin-top: 0.55rem;
        font-size: 0.82rem;
    }
    .leyenda span b { font-family: 'Oswald', sans-serif; }

    /* Fila de probabilidades (mini-tarjetas) */
    .prob-row { display: flex; gap: 0.7rem; margin-top: 1.3rem; }
    .prob-col {
        flex: 1;
        position: relative;
        overflow: hidden;
        text-align: center;
        padding: 0.85rem 0.5rem 0.7rem;
        border-radius: 14px;
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.07);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .prob-col:hover { transform: translateY(-3px); border-color: rgba(163,230,53,0.4); }
    .prob-col::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
    .prob-col.p1::before { background: linear-gradient(90deg, #a3e635, #d9f99d); }
    .prob-col.p2::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
    .prob-col.p3::before { background: linear-gradient(90deg, #fb7185, #fda4af); }

    /* Badge de resultado */
    .result-badge {
        margin: 1rem 0;
        padding: 0.65rem 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
    }
    .result-exacto { background: rgba(163,230,53,0.12); border: 1px solid rgba(163,230,53,0.4); color: #a3e635; }
    .result-ganador { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.4); color: #f59e0b; }
    .result-fallo { background: rgba(251,113,133,0.12); border: 1px solid rgba(251,113,133,0.4); color: #fb7185; }

    /* Grid over/under */
    .ou-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.6rem; }

    /* Tabla top 5 */
    .top5-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
    .top5-table th {
        text-align: left; color: #94a3b8; font-weight: 600; font-size: 0.72rem;
        text-transform: uppercase; letter-spacing: 1px;
        padding: 0.45rem 0.5rem; border-bottom: 1px solid rgba(163,230,53,0.18);
    }
    .top5-table td { padding: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .top5-table tbody tr { transition: background 0.2s ease; }
    .top5-table tbody tr:hover { background: rgba(163,230,53,0.06); }
    .top5-table td:last-child { text-align: right; font-family: 'Oswald', sans-serif; color: #a3e635; }
    .rank {
        display: inline-flex; align-items: center; justify-content: center;
        width: 24px; height: 24px; border-radius: 50%;
        font-family: 'Oswald', sans-serif; font-size: 0.8rem; font-weight: 700;
        margin-right: 0.5rem; color: #0b1120;
    }
    .r1 { background: linear-gradient(135deg, #fde047, #f59e0b); }
    .r2 { background: linear-gradient(135deg, #e2e8f0, #94a3b8); }
    .r3 { background: linear-gradient(135deg, #fdba74, #c2410c); }
    .rn { background: rgba(255,255,255,0.1); color: #cbd5e1; }

    /* Título principal, subtítulo y VS */
    .kicker {
        text-align: center; font-family: 'Oswald', sans-serif;
        letter-spacing: 3px; text-transform: uppercase;
        font-size: 0.75rem; color: #d9f99d; opacity: 0.85;
    }
    .titulo-app {
        text-align: center; font-family: 'Oswald', sans-serif; font-weight: 700;
        font-size: 2.5rem; letter-spacing: 0.5px; margin: 0.2rem 0 0.1rem;
    }
    .titulo-app .grad {
        background: linear-gradient(92deg, #ffffff 10%, #a3e635 45%, #fbbf24 85%);
        -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 4px 18px rgba(163,230,53,0.25));
    }
    .vs-text {
        text-align: center; font-family: 'Oswald', sans-serif;
        font-size: 1.7rem; font-weight: 700; color: #fbbf24;
        text-shadow: 0 0 16px rgba(245,158,11,0.6);
    }

    /* EN VIVO */
    .live-tag {
        display: inline-flex; align-items: center; gap: 0.4rem;
        color: #ff5a5a; font-weight: 700; letter-spacing: 0.5px;
    }
    .live-tag::before {
        content: ""; width: 8px; height: 8px; border-radius: 50%;
        background: #ff5a5a; box-shadow: 0 0 10px #ff5a5a; animation: pulse 1.4s infinite;
    }

    @keyframes fadeUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    @keyframes shimmer { 0% { transform: translateX(-100%); } 60%, 100% { transform: translateX(200%); } }
</style>
""", unsafe_allow_html=True)

st.markdown("""
# Acerca del proyecto
Este proyecto implementa desde cero modelos para la predicción de partidos de la Liga MX.

El desarrollo fue realizado como proyecto personal con fin educativo para profundizar en:

- Machine Learning
- Modelos Lineales Generalizados
- Inferencia Bayesiana
- MCMC
- Optimización Numérica
- Modelado Estadístico Deportivo

**Las predicciones no constituyen recomendaciones de apuesta.**
""")
st.markdown("""
## Ya estan actualizados las predicciones de la J8!!!!
""")

c1, c2, c3 = st.columns([1,2,1])

with c2:
    st.image("escudos/ligamx.png", width=250)

st.markdown(
    '<div class="kicker">Apertura 2026 · Predicciones</div>'
    '<h1 class="titulo-app">⚽ Predicción de partidos '
    '<span class="grad">Liga MX</span></h1>',
    unsafe_allow_html=True
)

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

    estado_txt = "Partido pendiente" if pd.isna(partido["resultado_local"]) else "Partido finalizado"
    st.markdown(
        f'<div class="small-meta" style="text-align:center;margin-top:1.5rem;">'
        f'{fecha.strftime("%d/%m/%Y")} &nbsp;·&nbsp; {estado_txt}</div>',
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
        st.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)

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

     st.markdown(
    '<h2 style="text-align:center;margin:25px 0 20px;">'
    '<span class="live-tag">EN VIVO</span></h2>',
    unsafe_allow_html=True
)

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

    # Matriz probas
    matriz = np.array(json.loads(partido["matriz"]))

    # Tarjeta del partido (una sola pieza HTML para que el estilo aplique)
    _prob_marcador = matriz[marcador[0], marcador[1]]

    _pl = float(prob_local)
    _pe = float(prob_empate)
    _pv = float(prob_visitante)

    result_html = ""
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
            result_html = (
                '<div class="result-badge result-exacto">✅ Marcador exacto | Final: '
                f'{nombre_equipo(local)} {rl} - {rv} {nombre_equipo(visitante)}</div>'
            )
        elif signo_pred == signo_real:
            result_html = (
                '<div class="result-badge result-ganador">🟡 Se acertó el ganador | Final: '
                f'{nombre_equipo(local)} {rl} - {rv} {nombre_equipo(visitante)}</div>'
            )
        else:
            result_html = (
                '<div class="result-badge result-fallo">❌ Predicción incorrecta | Final: '
                f'{nombre_equipo(local)} {rl} - {rv} {nombre_equipo(visitante)}</div>'
            )

    _it = np.nditer(matriz, flags=["multi_index"])
    _tuplas = []
    for _val in _it:
        _tuplas.append(_it.multi_index)

    def _prob_over(umbral):
        return sum(matriz[i, j] for i, j in _tuplas if i + j > umbral)

    ou_boxes = ""
    for umbral in ("2.5", "1.5", "0.5"):
        po = min(_prob_over(float(umbral)), 1.0)
        pu = max(1 - po, 0.0)
        ou_boxes += (
            f'<div class="ou-caja">'
            f'<div class="ou-lado ou-over">Over {umbral} &nbsp; {po:.0%}</div>'
            f'<div class="ou-lado ou-under">Under {umbral} &nbsp; {pu:.0%}</div>'
            f'</div>'
        )

    _flat_idx = np.argsort(matriz, axis=None)[::-1][:5]
    top_rows = ""
    for _rank, _k in enumerate(_flat_idx, start=1):
        _gl, _gv = np.unravel_index(_k, matriz.shape)
        _rcls = "r1" if _rank == 1 else "r2" if _rank == 2 else "r3" if _rank == 3 else "rn"
        top_rows += (
            f'<tr><td><span class="rank {_rcls}">{_rank}</span>'
            f'{nombre_equipo(local)} {_gl} - {_gv} {nombre_equipo(visitante)}</td>'
            f'<td>{matriz[_gl, _gv]:.1%}</td></tr>'
        )

    card_html = (
        '<div class="partido-card">'
        '<div class="titulo-sec" style="text-align:center;">'
        '<span class="seccion-titulo">Marcador más probable</span></div>'
        f'<p class="marcador-grande">{nombre_equipo(local)} '
        f'<span style="color:#94a3b8;">{marcador[0]} - {marcador[1]}</span> '
        f'{nombre_equipo(visitante)}</p>'
        f'<div class="small-meta" style="text-align:center;margin-top:0.2rem;">'
        f'Probabilidad <b style="color:#a3e635;">{_prob_marcador:.1%}</b></div>'
        f'<div class="prob-row">'
        f'<div class="prob-col p1"><div class="prob-etiqueta">{nombre_equipo(local)}</div>'
        f'<div class="prob-valor">{prob_local:.1%}</div>'
        f'<div class="prob-momio">Momio {momio_local:+.0f}</div></div>'
        f'<div class="prob-col p2"><div class="prob-etiqueta">Empate</div>'
        f'<div class="prob-valor">{prob_empate:.1%}</div>'
        f'<div class="prob-momio">Momio {momio_empate:+.0f}</div></div>'
        f'<div class="prob-col p3"><div class="prob-etiqueta">{nombre_equipo(visitante)}</div>'
        f'<div class="prob-valor">{prob_visitante:.1%}</div>'
        f'<div class="prob-momio">Momio {momio_visitante:+.0f}</div></div>'
        f'</div>'
        f'<div class="barra-wrapper">'
        f'<div class="barra-linea">'
        f'<div class="barra-seg" style="width:{_pl*100:.1f}%;background:linear-gradient(180deg,#bef264,#84cc16);"></div>'
        f'<div class="barra-seg" style="width:{_pe*100:.1f}%;background:linear-gradient(180deg,#fcd34d,#f59e0b);"></div>'
        f'<div class="barra-seg" style="width:{_pv*100:.1f}%;background:linear-gradient(180deg,#fda4af,#f43f5e);"></div>'
        f'</div>'
        f'<div class="leyenda">'
        f'<span style="color:#a3e635;">Local <b>{_pl:.1%}</b></span>'
        f'<span style="color:#fbbf24;">Empate <b>{_pe:.1%}</b></span>'
        f'<span style="color:#fb7185;">Visita <b>{_pv:.1%}</b></span>'
        f'</div>'
        f'</div>'
        f'{result_html}'
        f'<div class="titulo-sec"><span class="seccion-titulo">Over / Under</span></div>'
        f'<div class="ou-grid">{ou_boxes}'
        f'<div class="ou-caja">'
        f'<div class="ou-lado" style="color:#fbbf24;">Goles esperados</div>'
        f'<div class="ou-lado" style="color:#f8fafc;">Local <b>{lam:.2f}</b> · Vis <b>{mu:.2f}</b></div>'
        f'</div>'
        f'</div>'
        f'<div class="titulo-sec"><span class="seccion-titulo">Top 5 marcadores más probables</span></div>'
        f'<table class="top5-table"><thead><tr><th>Marcador</th><th style="text-align:right;">Probabilidad</th></tr></thead>'
        f'<tbody>{top_rows}</tbody></table>'
        f'</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)


partidos_live = obtener_partidos_en_vivo()

partidos = predicciones[
    predicciones["jornada"] == jornada
]

for _, partido in partidos.iterrows():

    mostrar_partido(
        partido,
        partidos_live
    )



