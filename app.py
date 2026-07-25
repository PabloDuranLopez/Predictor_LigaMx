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

st.write("Hola soy Pablo Duran, soy estudiante de Actuaría y Matemáticas en la Universidad Nacional Autónoma de México (UNAM), con profundo interes en Machine Learning, Estadística Bayesiana y las Finanzas Cuantitativas. Me gusta construir modelos desde cero para entender a profundidad cómo funcionan. He desarrollado implementaciones propias de prediccion (tradicional y enfoque bayesiano) de despacho en incidentes viales del C5, prediccion de tumores malignos, diabetes, asi como el pricing de derivados financieros")
st.write("Este es un proyecto mas, siendo compartido con ustedes de forma educativa, y que claro este proyecto no es una sugerencia de apuestas")

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


# Normalizar nombres para que coincidan con el modelo
jornadas["local"] = jornadas["local"].replace({
    "América": "America",
    "León": "Leon",
    "Mazatlán": "Mazatlan"
})

jornadas["visitante"] = jornadas["visitante"].replace({
    "América": "America",
    "León": "Leon",
    "Mazatlán": "Mazatlan"
})

with st.spinner("Entrenando modelo..."):

    modelo = entrenar_modelo(df)



st.divider()

jornada = st.selectbox(
    "Selecciona la jornada",
    sorted(jornadas["jornada"].unique())
)
st.divider()

goles_max = 10

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
    st.success(
    f"{nombre_equipo(local)} {marcador[0]} - {marcador[1]} {nombre_equipo(visitante)}"
)

    probs = modelo.win_prob(
        local,
        visitante,
        goles_max
    )

    c1, c2, c3 = st.columns(3) 
    
    with c1: 
        st.markdown(f"""
    <div style="text-align:center;">
        <h3> Local</h3>
        <h1>{probs.iloc[0][local]:.1%}</h1>
        <h2>{probs.iloc[0][f'Momio {local}']:+.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
    <div style="text-align:center;">
        <h3> Empate</h3>
        <h1>{probs.iloc[0]['Empate']:.1%}</h1>
        <h2>{probs.iloc[0]['Momio Empate']:+.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    with c3: 
        st.markdown(f"""
    <div style="text-align:center;">
        <h3> Visitante</h3>
        <h1>{probs.iloc[0][visitante]:.1%}</h1>
        <h2>{probs.iloc[0][f'Momio {visitante}']:+.0f}</h2>
    </div>
    """, unsafe_allow_html=True)
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
    


