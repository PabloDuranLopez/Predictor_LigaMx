import streamlit as st
import pandas as pd
import os
from clases_funciones import DixonColes


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


c1, c2, c3 = st.columns([1,2,1])

with c2:
    st.image("escudos/ligamx.png", width=250)

st.title("⚽ Predicción de partidos Liga MX")
st.write("Modelo Dixon-Coles con Decaimiento Temporal")
@st.cache_data
def cargar_datos():

    df = pd.read_csv("data/ligamx.csv")
    df["fecha"] = pd.to_datetime(df["fecha"])

    return df



@st.cache_data
def cargar_jornadas():

    return pd.read_csv("data/partidos_predecir.csv")


@st.cache_resource
def entrenar_modelo(df):

    modelo = DixonColes(xi=0.0065)
    modelo.fit(df)
    return modelo

df = cargar_datos()
jornadas = cargar_jornadas()

with st.spinner("Entrenando modelo..."):

    modelo = entrenar_modelo(df)
st.write(sorted(modelo.teams))



st.divider()

jornada = st.selectbox(
    "Selecciona la jornada",
    sorted(jornadas["jornada"].unique())
)
st.divider()

goles_max = st.slider(
    "Máximo de goles",
    3,
    10,
    7
)

def mostrar_partido(local, visitante, modelo, goles_max, fecha):
    st.caption(f"📅 {fecha}")


    col1, col2, col3 = st.columns([2,1,2])

    with col1:

        st.image(obtener_escudo(local), width=170)

        st.markdown(
            f"<h3 style='text-align:center'>{nombre_equipo(local)}</h3>",
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            "<h1 style='text-align:center;margin-top:70px'>VS</h1>",
            unsafe_allow_html=True
        )

    with col3:

        st.image(obtener_escudo(visitante), width=170)

        st.markdown(
            f"<h3 style='text-align:center'>{nombre_equipo(visitante)}</h3>",
            unsafe_allow_html=True
        )
    
    lam, mu = modelo.expected_goals(local, visitante)

    marcador = modelo.predict_score(
        local,
        visitante,
        goles_max
    )

    probs = modelo.win_prob(
        local,
        visitante,
        goles_max
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Local",
        f"{probs.iloc[0][local]:.1%}"
    )

    c2.metric(
        "Empate",
        f"{probs.iloc[0]['Empate']:.1%}"
    )

    c3.metric(
        "Visitante",
        f"{probs.iloc[0][visitante]:.1%}"
    )

    st.success(
    f"{nombre_equipo(local)} {marcador[0]} - {marcador[1]} {nombre_equipo(visitante)}")

    with st.expander("Ver detalles"):

        c1, c2 = st.columns(2)

        c1.metric("λ Local", f"{lam:.2f}")
        c2.metric("μ Visitante", f"{mu:.2f}")

        fig = modelo.score_matrix(
            local,
            visitante,
            goles_max
        )

        st.pyplot(fig)

    st.divider()

partidos = jornadas[
    jornadas["jornada"] == jornada
]

for _, partido in partidos.iterrows():
    st.write(
        f"{partido['local']} vs {partido['visitante']}"
    )

    mostrar_partido(
        partido["local"],
        partido["visitante"],
        modelo,
        goles_max,
        partido["fecha"]
    )
    


