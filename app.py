"""
RedSalud – Optimización de la distribución de medicamentos (Parte 3).
Ejecutar localmente:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

from modelo import (CENTROS, HOSPITALES, COSTOS_INICIALES, CAPACIDADES_INICIALES,
                    DEMANDAS_INICIALES, LIMITE_RUTA_INICIAL, resolver_transporte)

st.set_page_config(page_title="RedSalud · Distribución", page_icon="💊", layout="wide")

st.title("RedSalud: plan de distribución de medicamentos")
st.write("Modifica los datos del escenario y pulsa **Optimizar distribución** "
         "para obtener el plan de envíos de menor costo.")

# ---------------------------------------------------------------- Entradas
st.header("Datos del escenario")

col_cap, col_dem, col_ruta = st.columns(3)

with col_cap:
    st.subheader("Capacidad de los centros")
    capacidades = {c: st.number_input(c, min_value=0, value=CAPACIDADES_INICIALES[c],
                                      step=5, key=f"cap_{c}") for c in CENTROS}

with col_dem:
    st.subheader("Demanda de los hospitales")
    demandas = {h: st.number_input(h, min_value=0, value=DEMANDAS_INICIALES[h],
                                   step=5, key=f"dem_{h}") for h in HOSPITALES}

with col_ruta:
    st.subheader("Restricción de ruta")
    limite_ruta = st.number_input("Máximo de unidades Rionegro → Hospital Central",
                                  min_value=0, value=LIMITE_RUTA_INICIAL, step=5)
    st.caption("Límite temporal por capacidad vehicular.")

st.subheader("Costos unitarios de transporte")
st.caption("Edita cualquier celda. Filas: centros de distribución. Columnas: hospitales.")
costos_iniciales = pd.DataFrame(COSTOS_INICIALES, index=HOSPITALES).T
costos = st.data_editor(
    costos_iniciales,
    width="stretch",
    column_config={h: st.column_config.NumberColumn(h, min_value=0, step=1, required=True)
                   for h in HOSPITALES},
    key="costos",
)

# ---------------------------------------------------------------- Optimizar
cap_total = sum(capacidades.values())
dem_total = sum(demandas.values())

if st.button("Optimizar distribución", type="primary"):
    st.session_state["resultado"] = resolver_transporte(costos.astype(float), capacidades,
                                                        demandas, limite_ruta)

# ---------------------------------------------------------------- Resultados
st.header("Resultados")

if "resultado" not in st.session_state:
    st.info("Pulsa **Optimizar distribución** para calcular el plan con los datos de arriba.")
    st.stop()

r = st.session_state["resultado"]

# Aviso si se editaron datos después de la última optimización
if r["capacidad_total"] != cap_total or r["demanda_total"] != dem_total:
    st.info("Los datos cambiaron desde la última optimización. "
            "Pulsa **Optimizar distribución** para actualizar los resultados.")

# Advertencia de capacidad insuficiente
if r["demanda_total"] > r["capacidad_total"]:
    faltante = r["demanda_total"] - r["capacidad_total"]
    st.error(f"⚠️ Con las condiciones ingresadas no existe capacidad suficiente para satisfacer "
             f"completamente la demanda: la demanda total ({r['demanda_total']:,}) supera la "
             f"capacidad total ({r['capacidad_total']:,}) en {faltante:,} unidades.")

estados = {"Optimal": "Óptima", "Infeasible": "Infactible", "Unbounded": "No acotada",
           "Not Solved": "No resuelta", "Undefined": "Indefinida"}
estado_txt = estados.get(r["estado"], r["estado"])

utilizacion = (r["demanda_total"] / r["capacidad_total"] * 100) if r["capacidad_total"] else 0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Costo mínimo total",
          f"${r['costo_total']:,.0f}" if r["costo_total"] is not None else "—")
m2.metric("Capacidad total disponible", f"{r['capacidad_total']:,}")
m3.metric("Demanda total", f"{r['demanda_total']:,}")
m4.metric("Utilización de la capacidad",
          f"{utilizacion:.1f} %" if r["estado"] == "Optimal" else "—")
m5.metric("Estado de la solución", estado_txt)

if r["estado"] != "Optimal":
    if r["demanda_total"] <= r["capacidad_total"]:
        st.warning("El modelo no encontró una solución factible. Revisa el límite de la ruta "
                   "Rionegro → Hospital Central: puede impedir atender toda la demanda.")
    st.stop()

st.subheader("Cantidades óptimas enviadas (unidades)")
envios = r["envios"].copy()
envios["Total enviado"] = envios.sum(axis=1)
envios.loc["Total recibido"] = envios.sum(axis=0)
st.dataframe(envios.style.format("{:,.0f}"), width="stretch")

st.subheader("Uso de la capacidad por centro")
st.dataframe(r["uso_centros"].style.format({"Capacidad máxima": "{:,.0f}",
                                            "Capacidad utilizada": "{:,.0f}",
                                            "Capacidad no utilizada": "{:,.0f}",
                                            "% utilización": "{:.1f} %"}),
             width="stretch")
st.bar_chart(r["uso_centros"][["Capacidad utilizada", "Capacidad no utilizada"]])

st.subheader("Rutas activas")
rutas = (r["envios"].stack().reset_index()
         .set_axis(["Centro", "Hospital", "Unidades"], axis=1)
         .query("Unidades > 0"))
rutas["Costo unitario"] = [costos.loc[c, h] for c, h in zip(rutas["Centro"], rutas["Hospital"])]
rutas["Costo de la ruta"] = rutas["Unidades"] * rutas["Costo unitario"]
st.dataframe(rutas.reset_index(drop=True), width="stretch", hide_index=True)
