import os
import json
import numpy as np
import pandas as pd
import sys
from clases_funciones import DixonColes



df = pd.read_csv("data/ligamx.csv")
df["fecha"] = pd.to_datetime(df["fecha"])



partidos = pd.read_csv("data/partidos_predecir.csv")

partidos["fecha"] = pd.to_datetime(partidos["fecha"])




partidos["local"] = partidos["local"].replace({
    "América":"America",
    "León":"Leon",
    "Mazatlán":"Mazatlan"
})

partidos["visitante"] = partidos["visitante"].replace({
    "América":"America",
    "León":"Leon",
    "Mazatlán":"Mazatlan"
})



modelo = DixonColes(xi=0.0065)
modelo.fit(df)



ruta = "data/predicciones.csv"

if os.path.exists(ruta) and os.path.getsize(ruta) > 0:

    historial = pd.read_csv(ruta)

    historial["fecha"] = pd.to_datetime(historial["fecha"])

else:

    historial = pd.DataFrame()

if not historial.empty:

    historial = historial[
        ~historial.set_index(["fecha", "local", "visitante"]).index.isin(
            partidos.set_index(["fecha", "local", "visitante"]).index
        )
    ]

nuevas_predicciones = []

if partidos.empty:
    print("No hay partidos pendientes para predecir.")
    sys.exit()
    
for _, partido in partidos.iterrows():

    fecha = partido["fecha"]
    jornada = partido["jornada"]
    local = partido["local"]
    visitante = partido["visitante"]

    
    lam, mu = modelo.expected_goals(
        local,
        visitante
    )

    marcador = modelo.predict_score(
        local,
        visitante,
        goles_max=10
    )

    probs = modelo.win_prob(
        local,
        visitante,
        goles_max=10
    )
    
    prob_local = probs.iloc[0][local]
    prob_empate = probs.iloc[0]["Empate"]
    prob_visitante = probs.iloc[0][visitante]

    if prob_local >= prob_empate and prob_local >= prob_visitante:
     signo_pred = 1          # gana local
    
    elif prob_visitante >= prob_local and prob_visitante >= prob_empate:
      signo_pred = -1         # gana visitante
    else:
     signo_pred = 0          # empate

    matriz = modelo.predict(
        local,
        visitante,
        goles_max=10
    )

    # ---- CALCULOS ADICIONALES: Over/Under y Top 5 marcadores ----

    mascara_over = np.fromfunction(lambda i, j: i + j > 2.5, matriz.shape)
    prob_over25 = float(matriz[mascara_over].sum())
    prob_under25 = 1 - prob_over25

    prob_over15 = float(matriz[np.fromfunction(lambda i, j: i + j > 1.5, matriz.shape)].sum())
    prob_under15 = 1 - prob_over15

    prob_over05 = float(matriz[np.fromfunction(lambda i, j: i + j > 0.5, matriz.shape)].sum())
    prob_under05 = 1 - prob_over05

    total_goles = lam + mu

    idx_flat = np.argsort(matriz, axis=None)[::-1][:5]
    top5 = []
    for k in idx_flat:
        g_local, g_vis = np.unravel_index(k, matriz.shape)
        top5.append(f"{int(g_local)}-{int(g_vis)}:{matriz[g_local, g_vis]:.3f}")
    top5_str = "|".join(top5)

    nuevas_predicciones.append({

        "fecha":fecha,

        "jornada":jornada,

        "local":local,

        "visitante":visitante,

        "pred_local":marcador[0],

        "pred_visitante":marcador[1],
        
        "signo_pred": signo_pred,

        "xg_local":lam,

        "xg_visitante":mu,

        "prob_over05": prob_over05,
        "prob_under05": prob_under05,
        "prob_over15": prob_over15,
        "prob_under15": prob_under15,
        "prob_over25": prob_over25,
        "prob_under25": prob_under25,
        "total_goles": total_goles,
        "top5": top5_str,

        "prob_local":probs.iloc[0][local],

        "prob_empate":probs.iloc[0]["Empate"],

        "prob_visitante":probs.iloc[0][visitante],

        "momio_local":probs.iloc[0][f"Momio {local}"],

        "momio_empate":probs.iloc[0]["Momio Empate"],

        "momio_visitante":probs.iloc[0][f"Momio {visitante}"],

        "matriz":json.dumps(
            matriz.tolist()
        ),

        "resultado_local":partido["goles_local"],

        "resultado_visitante":partido["goles_visitante"]

    })

nuevas = pd.DataFrame(nuevas_predicciones)

if historial.empty:

    salida = nuevas

else:

    salida = pd.concat(
        [historial,nuevas],
        ignore_index=True
    )
salida = salida.sort_values(["jornada", "fecha"]).reset_index(drop=True)
    
salida.to_csv(
    ruta,
    index=False
)

print("Predicciones actualizadas.")