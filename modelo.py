"""
Modelo de transporte RedSalud (Parte 2 del proyecto).

Todos los datos (costos, capacidades, demandas y límite de ruta) entran como
parámetros: nada está fijo dentro del modelo. La app de Streamlit llama a
`resolver_transporte` con los valores que el usuario escribe en la interfaz.
"""
import pandas as pd
import pulp

# Escenario inicial: solo se usa como valores predeterminados de la interfaz
CENTROS = ["Medellín", "Rionegro", "Bello"]
HOSPITALES = ["Hospital Norte", "Hospital Central", "Hospital Oriente", "Hospital Sur"]

COSTOS_INICIALES = {
    "Medellín": [8, 12, 15, 11],
    "Rionegro": [14, 10, 9, 16],
    "Bello":    [11, 13, 14, 8],
}
CAPACIDADES_INICIALES = {"Medellín": 140, "Rionegro": 120, "Bello": 130}
DEMANDAS_INICIALES = {"Hospital Norte": 90, "Hospital Central": 100,
                      "Hospital Oriente": 80, "Hospital Sur": 100}
LIMITE_RUTA_INICIAL = 30
RUTA_LIMITADA = ("Rionegro", "Hospital Central")


def resolver_transporte(costos: pd.DataFrame, capacidades: dict, demandas: dict,
                        limite_ruta: float, ruta_limitada=RUTA_LIMITADA) -> dict:
    """
    costos: DataFrame (filas = centros, columnas = hospitales) con costo unitario.
    capacidades: {centro: capacidad máxima semanal}
    demandas: {hospital: demanda semanal}
    limite_ruta: máximo de unidades en la ruta Rionegro -> Hospital Central.
    """
    centros = list(costos.index)
    hospitales = list(costos.columns)

    modelo = pulp.LpProblem("RedSalud_Transporte", pulp.LpMinimize)

    # Variables de decisión: x[i, j] = unidades enviadas del centro i al hospital j
    x = {(i, j): pulp.LpVariable(f"x_{i}_{j}".replace(" ", "_"), lowBound=0)
         for i in centros for j in hospitales}

    # Función objetivo: minimizar el costo total de transporte
    modelo += pulp.lpSum(float(costos.loc[i, j]) * x[i, j]
                         for i in centros for j in hospitales), "Costo_total"

    # Capacidad máxima de cada centro
    for i in centros:
        modelo += pulp.lpSum(x[i, j] for j in hospitales) <= capacidades[i], f"Cap_{i}"

    # Satisfacción completa de la demanda de cada hospital
    for j in hospitales:
        modelo += pulp.lpSum(x[i, j] for i in centros) == demandas[j], f"Dem_{j}".replace(" ", "_")

    # Capacidad máxima de la ruta Rionegro -> Hospital Central
    o, d = ruta_limitada
    if o in centros and d in hospitales:
        modelo += x[o, d] <= limite_ruta, "Limite_ruta_Rionegro_Central"

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))
    estado = pulp.LpStatus[modelo.status]  # Optimal, Infeasible, Unbounded, Not Solved...

    cap_total = sum(capacidades.values())
    dem_total = sum(demandas.values())

    resultado = {
        "estado": estado,
        "capacidad_total": cap_total,
        "demanda_total": dem_total,
        "costo_total": None,
        "envios": None,
        "uso_centros": None,
    }

    if estado == "Optimal":
        envios = pd.DataFrame(
            [[round(x[i, j].value() or 0, 2) for j in hospitales] for i in centros],
            index=centros, columns=hospitales,
        )
        utilizada = envios.sum(axis=1)
        uso = pd.DataFrame({
            "Capacidad máxima": [capacidades[i] for i in centros],
            "Capacidad utilizada": utilizada.values,
            "Capacidad no utilizada": [capacidades[i] - utilizada[i] for i in centros],
        }, index=centros)
        uso["% utilización"] = (uso["Capacidad utilizada"] / uso["Capacidad máxima"] * 100).round(1)

        resultado.update({
            "costo_total": pulp.value(modelo.objective),
            "envios": envios,
            "uso_centros": uso,
        })

    return resultado


if __name__ == "__main__":
    # Prueba rápida por consola con el escenario inicial
    costos = pd.DataFrame(COSTOS_INICIALES, index=HOSPITALES).T
    r = resolver_transporte(costos, CAPACIDADES_INICIALES, DEMANDAS_INICIALES, LIMITE_RUTA_INICIAL)
    print("Estado:", r["estado"])
    print("Costo mínimo:", r["costo_total"])
    print(r["envios"])
    print(r["uso_centros"])
