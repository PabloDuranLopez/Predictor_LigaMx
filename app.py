import streamlit as st
import pandas as pd
import os
import json
import numpy as np
from clases_funciones import plot_score_matrix
from api_live import (
    obtener_partidos_en_vivo,
    buscar_partido,
    obtener_estadisticas
)
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

st.markdown("""
### Acerca del proyecto
Este proyecto implementa desde cero el modelo **Dixon-Coles con decaimiento temporal** para la predicción de partidos de la Liga MX.

El desarrollo fue realizado como proyecto personal con fin educativo para profundizar en:

- Machine Learning
- Modelos de Poisson
- Inferencia Bayesiana
- Optimización Numérica
- Modelado Estadístico Deportivo

**Las predicciones no constituyen recomendaciones de apuesta.**
""")

c1, c2, c3 = st.columns([1,2,1])

with c2:
    st.image("escudos/ligamx.png", width=250)

st.title("⚽ Predicción de partidos Liga MX")
st.write("Modelo Dixon-Coles con Decaimiento Temporal")

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

    st.caption(f" {fecha.strftime('%d/%m/%Y')}")


    if pd.isna(partido["resultado_local"]):
     st.caption("- Partido pendiente")
    else:
     st.caption("+ Partido finalizado")

    col1, col2, col3 = st.columns([2,1,2])

    with col1:

     escudo_local = obtener_escudo(local)

     if escudo_local is not None:
        st.image(escudo_local, width=170)

     st.markdown(
        f"<h3 style='text-align:center'>{nombre_equipo(local)}</h3>",
        unsafe_allow_html=True)

    with col2:

        st.markdown(
            "<h1 style='text-align:center;margin-top:70px'>VS</h1>",
            unsafe_allow_html=True
        )

    with col3:

     escudo_visitante = obtener_escudo(visitante)

     if escudo_visitante is not None:
        st.image(escudo_visitante, width=170)

     st.markdown(
        f"<h3 style='text-align:center'>{nombre_equipo(visitante)}</h3>",
        unsafe_allow_html=True)
    
    if live is not None:

        estado = {
        "NS": "No iniciado",
        "1H": "Primer tiempo",
        "HT": "Descanso",
        "2H": "Segundo tiempo",
        "ET": "Tiempo extra",
        "BT": "Descanso T.E.",
        "P": "Penales",
        "FT": "Finalizado"}

        st.markdown("""
         <h2 style="text-align:center;color:#ff4b4b">🔴 EN VIVO</h2>""", unsafe_allow_html=True)

        st.markdown(f"""<div style="text-align:center"><h1 style="font-size:70px;margin-bottom:0;margin-top:0;">{live["goles_local"]} - {live["goles_visitante"]}</h1><h3 style="color:#BBBBBB">{live["minuto"]}'</h3><p style="color:#999999;font-size:18px;">{estado.get(live["estado"],live["estado"])}</p></div>""", unsafe_allow_html=True)

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
    
    st.markdown("### Marcador esperado")

    st.success(f"{nombre_equipo(local)} {marcador[0]} - {marcador[1]} {nombre_equipo(visitante)}")
    
    prob_local = partido["prob_local"]
    prob_empate = partido["prob_empate"]
    prob_visitante = partido["prob_visitante"]
    
    momio_local = partido["momio_local"]

    momio_empate = partido["momio_empate"]

    momio_visitante = partido["momio_visitante"]
    
    if not pd.isna(partido["resultado_local"]):

     rl = int(partido["resultado_local"])
     rv = int(partido["resultado_visitante"])

     st.markdown("### Resultado final")

     st.info(
        f"{nombre_equipo(local)} {rl} - {rv} {nombre_equipo(visitante)}")

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
        st.success("✅ Marcador exacto")

     elif signo_pred == signo_real:
        st.warning("🟡 Se acertó el ganador")

     else:
        st.error("❌ Predicción incorrecta") 


    
    st.markdown("### Probabilidades y momios")
    c1, c2, c3 = st.columns(3) 
    
    with c1: 
        st.markdown(f"""
    <div style="text-align:center;">
        <h3> Local</h3>
        <h1>{prob_local:.1%}</h1>
        <h2>{momio_local:+.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
    <div style="text-align:center;">
        <h3> Empate</h3>
        <h1>{prob_empate:.1%}</h1>
        <h2>{momio_empate:+.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    with c3: 
        st.markdown(f"""
    <div style="text-align:center;">
        <h3> Visitante</h3>
        <h1>{prob_visitante:.1%}</h1>
        <h2>{momio_visitante:+.0f}</h2>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    with st.expander("Ver detalles"):

        c1, c2 = st.columns(2)

        c1.metric("Goles esperados local", f"{lam:.2f}")
        c2.metric("Goles esperados visitante", f"{mu:.2f}")

        matriz = np.array(json.loads(partido["matriz"]))
        fig = plot_score_matrix(matriz,local,visitante) 
        st.pyplot(fig)

    st.divider()


partidos_live = obtener_partidos_en_vivo()

partidos = predicciones[
    predicciones["jornada"] == jornada
]

for _, partido in partidos.iterrows():

    mostrar_partido(
        partido,
        partidos_live
    )


