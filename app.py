import streamlit as st
import pandas as pd

from clases_funciones import DixonColes

st.set_page_config(
    page_title="Liga MX Predictor",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Predicción de partidos Liga MX")
st.write("Modelo Dixon-Coles con decaimiento temporal")



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



col1, col2 = st.columns(2)

with col1:

    local = st.selectbox(
        "Equipo local",
        modelo.teams
    )

with col2:

    visitante = st.selectbox(
        "Equipo visitante",
        modelo.teams
    )

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


    "streamlit, numpy, pandas, scipy,matplotlib"