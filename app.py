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
        "Club San Luis": "atleticosl",

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


df = cargar_datos()



@st.cache_resource
def entrenar_modelo(df):

    modelo = DixonColes(xi=0.0065)

    modelo.fit(df)

    return modelo



with st.spinner("Entrenando modelo..."):

    modelo = entrenar_modelo(df)

st.success("Modelo entrenado")

equipos_disponibles = [equipo for equipo in modelo.teams
    if obtener_escudo(equipo) is not None
]

equipos_disponibles = sorted(equipos_disponibles)

col1, col2 = st.columns(2)

with col1:

    local = st.selectbox(
    "Equipo local",
    equipos_disponibles)

with col2:

    visitante = st.selectbox(
    "Equipo visitante",
    equipos_disponibles)
    
st.divider()

col1, col2, col3 = st.columns([3,1,3])


with col1:

    c = st.columns([1,2,1])

    with c[1]:
        st.image(
            obtener_escudo(local),
            width=170
        )

    st.markdown(
        f"<h2 style='text-align:center'>{nombre_equipo(local)}</h2>",
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        "<h1 style='text-align:center; margin-top:90px;'>VS</h1>",
        unsafe_allow_html=True
    )

with col3:

    c = st.columns([1,2,1])

    with c[1]:
        st.image(
            obtener_escudo(visitante),
            width=170
        )

    st.markdown(
        f"<h2 style='text-align:center'>{nombre_equipo(visitante)}</h2>",
        unsafe_allow_html=True
    )
st.divider()

goles_max = st.slider(
    "Máximo de goles",
    3,
    10,
    7
)



if st.button("Predecir partido"):

    st.header("Resumen del modelo")

    st.dataframe(modelo.summary())

    st.header("Goles esperados")

    lam, mu = modelo.expected_goals(
        local,
        visitante
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "λ Local",
        f"{lam:.3f}"
    )

    c2.metric(
        "μ Visitante",
        f"{mu:.3f}"
    )

    st.header("Marcador más probable")

    marcador = modelo.predict_score(
        local,
        visitante,
        goles_max
    )

    st.success(
        f"{local} {marcador[0]} - {marcador[1]} {visitante}"
    )

    st.header("Probabilidades")

    st.dataframe(
        modelo.win_prob(
            local,
            visitante,
            goles_max
        )
    )

    st.header("Matriz de probabilidades")

    modelo.score_matrix(
        local,
        visitante,
        goles_max
    )

    st.pyplot()
    


