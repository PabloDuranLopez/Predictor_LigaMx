# -*- coding: utf-8 -*-
"""
Actualizacion automatica del proyecto Liga MX.

Que hace (pensado para correr 1 vez al dia, p.ej. 23:30 CDMX):

  1) Consulta los resultados de las jornadas pendientes en El Pais (datos Opta).
  2) Llena SOLO resultado_local / resultado_visitante en data/predicciones.csv
     de los partidos que ya terminaron.
  3) Cuando TODOS los partidos de una jornada terminaron y ya paso al menos
     un dia desde el ultimo, entonces:
        - agrega esos partidos a data/ligamx.csv
        - elimina la jornada de data/partidos_predecir.csv
        - reentrena el modelo ejecutando generar_predicciones.py

Uso:
    python auto_actualizar.py            # ejecuta de verdad
    python auto_actualizar.py --dry-run  # solo muestra que haria, sin escribir
"""

import os
import re
import io
import csv
import sys
import subprocess
import unicodedata
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
LIGAMX = os.path.join(DATA, "ligamx.csv")
PREDECIR = os.path.join(DATA, "partidos_predecir.csv")
PREDICCIONES = os.path.join(DATA, "predicciones.csv")

# --- Configuracion del torneo ---
LEAGUE_URL = (
    "https://elpais.com/deportes/resultados/futbol/"
    "mexico_apertura/2026/jornada/regular-a-{n}/"
)
SEASON_TAG = "2026"        # valor para la columna "temporada" de ligamx.csv
TORNEO = "Apertura"
UTC_OFFSET_HOURS = -6      # America/Mexico_City (sin horario de verano)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "es-MX,es;q=0.9",
}

# indices de columnas
P_JORNADA, P_LOCAL, P_VISIT, P_RLOCAL, P_RVISIT = 1, 2, 3, 14, 15   # predicciones.csv
D_JORNADA, D_FECHA, D_HORA, D_LOCAL, D_VISIT = 0, 2, 3, 4, 6       # partidos_predecir.csv


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def norm(s):
    s = str(s).strip().lower()
    s = "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    )
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


ALIASES = {
    "atlante": "atlante",
    "rayados": "monterrey", "monterrey": "monterrey",
    "xolos": "tijuana", "tijuana": "tijuana", "club tijuana": "tijuana",
    "atlas": "atlas",
    "cruz azul": "cruz azul", "la maquina": "cruz azul",
    "toluca": "toluca", "diablos rojos": "toluca",
    "chivas": "guadalajara", "guadalajara": "guadalajara",
    "gallos blancos": "queretaro", "queretaro": "queretaro", "gallos": "queretaro",
    "santos laguna": "santos laguna", "santos": "santos laguna",
    "pachuca": "pachuca", "tuzos": "pachuca",
    "tigres": "uanl", "tigres uanl": "uanl", "uanl": "uanl",
    "puebla": "puebla",
    "pumas": "unam", "unam": "unam", "pumas unam": "unam",
    "atletico san luis": "atletico san luis", "san luis": "atletico san luis",
    "leon fc": "leon", "leon": "leon",
    "bravos": "fc juarez", "fc juarez": "fc juarez", "juarez": "fc juarez",
    "america": "america",
    "necaxa": "necaxa",
}


def canon(name):
    return ALIASES.get(norm(name), norm(name))


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh))


def write_csv(path, rows, trailing_newline=False):
    # Se usa el modulo csv para citar correctamente campos con comas
    # (por ejemplo la columna "matriz" de predicciones.csv).
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerows(rows)
    txt = buf.getvalue()
    if not trailing_newline and txt.endswith("\r\n"):
        txt = txt[:-2]
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(txt)


def now_mx():
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=UTC_OFFSET_HOURS)


def parse_utc(s):
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=None)
        except Exception:
            pass
    return None


# --------------------------------------------------------------------------
# Scraper El Pais
# --------------------------------------------------------------------------
def scrape_jornada(n):
    url = LEAGUE_URL.format(n=n)
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    partidos = []
    for b in soup.select("[data-competition]"):
        tms = b.select(".a_sc_tn")
        if len(tms) < 2:
            continue
        st = b.select_one(".a_sc_st")
        gl = b.select_one(".a_sc_gl")
        partidos.append({
            "home": tms[0].get_text(strip=True),
            "away": tms[1].get_text(strip=True),
            "status": norm(st.get_text(strip=True)) if st else "",
            "score": gl.get_text(strip=True) if gl else "",
            "dt": b.get("data-datetime"),
        })
    return partidos


def parse_score(txt):
    m = re.match(r"^\s*(\d+)\s*-\s*(\d+)\s*$", txt or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


# --------------------------------------------------------------------------
# Incorporar jornadas completas a ligamx y quitar de predecir
# --------------------------------------------------------------------------
def incorporar(completadas, jornadas, idx):
    lig = read_csv(LIGAMX)
    nxt = 0
    for r in lig[1:]:
        m = re.match(rf"^{SEASON_TAG}/(\d+)$", r[0])
        if m:
            nxt = max(nxt, int(m.group(1)))

    lineas = []
    for jn in completadas:
        for r in jornadas[jn]:
            fila = idx.get((jn, canon(r[D_LOCAL]), canon(r[D_VISIT])))
            gl = fila[P_RLOCAL] if fila else ""
            gv = fila[P_RVISIT] if fila else ""
            nxt += 1
            lineas.append(
                f"{SEASON_TAG}/{nxt},{TORNEO},{jn},{r[D_FECHA]},{r[D_HORA]},"
                f"{r[D_LOCAL]},{r[D_VISIT]},{gl},{gv},FALSE,,,"
            )

    b = open(LIGAMX, "rb").read()
    assert not b.endswith(b"\r\n")
    with open(LIGAMX, "ab") as fh:
        fh.write(b"\r\n")
        fh.write("\r\n".join(lineas).encode("utf-8"))
    print(f"[auto] ligamx.csv: +{len(lineas)} filas.")

    part = read_csv(PREDECIR)
    dhead, drows = part[0], part[1:]
    drows2 = [r for r in drows if r[D_JORNADA] not in completadas]
    write_csv(PREDECIR, [dhead] + drows2)
    print(f"[auto] partidos_predecir.csv: -{len(drows) - len(drows2)} filas.")

    print("[auto] Reentrenando y regenerando predicciones...")
    env = dict(os.environ)
    env["MPLBACKEND"] = "Agg"
    subprocess.run(
        [sys.executable, os.path.join(BASE, "generar_predicciones.py")],
        cwd=BASE, env=env, check=True,
    )
    print("[auto] generar_predicciones.py ejecutado.")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main(dry_run=False):
    hoy = now_mx().date()
    print(f"[auto] Fecha Mexico: {hoy}  (dry_run={dry_run})")

    pred = read_csv(PREDICCIONES)
    phead, prows = pred[0], pred[1:]

    idx = {}
    for r in prows:
        if len(r) <= max(P_JORNADA, P_LOCAL, P_VISIT, P_RLOCAL, P_RVISIT):
            continue
        idx[(str(r[P_JORNADA]), canon(r[P_LOCAL]), canon(r[P_VISIT]))] = r

    part = read_csv(PREDECIR)
    dhead, drows = part[0], part[1:]

    jornadas = {}
    for r in drows:
        if len(r) <= max(D_JORNADA, D_FECHA, D_HORA, D_LOCAL, D_VISIT):
            continue
        jornadas.setdefault(str(r[D_JORNADA]), []).append(r)

    resultados_nuevos = 0
    completadas = []

    for jn, filas in sorted(jornadas.items(), key=lambda kv: int(kv[0])):
        fechas = []
        for r in filas:
            try:
                fechas.append(datetime.strptime(r[D_FECHA], "%Y-%m-%d").date())
            except Exception:
                pass
        if fechas and min(fechas) > hoy:
            continue  # la jornada aun no empieza

        print(f"[auto] Jornada {jn}: consultando resultados...")
        try:
            scraped = scrape_jornada(int(jn))
        except Exception as e:
            print(f"[auto]   ERROR al consultar J{jn}: {e}")
            continue

        finales = {}
        ultima = None
        for m in scraped:
            sc = parse_score(m["score"])
            if m["status"] == "finalizado" and sc is not None:
                finales[(canon(m["home"]), canon(m["away"]))] = sc
                dt = parse_utc(m["dt"])
                if dt:
                    d = (dt + timedelta(hours=UTC_OFFSET_HOURS)).date()
                    ultima = d if ultima is None or d > ultima else ultima

        # 1) llenar resultados en predicciones
        for r in filas:
            k1 = (canon(r[D_LOCAL]), canon(r[D_VISIT]))
            k2 = (canon(r[D_VISIT]), canon(r[D_LOCAL]))
            if k1 in finales:
                gl, gv = finales[k1]
            elif k2 in finales:
                gv, gl = finales[k2]
            else:
                continue
            fila = idx.get((jn, canon(r[D_LOCAL]), canon(r[D_VISIT])))
            if fila is None:
                continue
            if fila[P_RLOCAL] == "" and fila[P_RVISIT] == "":
                fila[P_RLOCAL], fila[P_RVISIT] = str(gl), str(gv)
                resultados_nuevos += 1
                print(f"[auto]   + J{jn}: {r[D_LOCAL]} {gl}-{gv} {r[D_VISIT]}")

        # 2) jornada completa? (todos finalizados y >= 1 dia despues)
        pendientes = [
            r for r in filas
            if (canon(r[D_LOCAL]), canon(r[D_VISIT])) not in finales
            and (canon(r[D_VISIT]), canon(r[D_LOCAL])) not in finales
        ]
        if not pendientes and ultima is not None and (hoy - ultima).days >= 1:
            completadas.append(jn)
            print(f"[auto]   J{jn} COMPLETA (ultimo {ultima}) -> reentrenar")
        else:
            print(f"[auto]   J{jn} pendiente ({len(pendientes)} partidos).")

    print(f"[auto] Resultados nuevos: {resultados_nuevos}")
    print(f"[auto] Jornadas completas: {completadas}")

    if dry_run:
        print("[auto] DRY-RUN: no se escribio nada.")
        return

    if resultados_nuevos:
        write_csv(PREDICCIONES, [phead] + prows, trailing_newline=True)
        print("[auto] predicciones.csv actualizado.")

    if completadas:
        incorporar(completadas, jornadas, idx)


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
