from collections import defaultdict, deque

# dataset -> insumos de los que se construye
depende_de = {
    "raw_precios": [],
    "raw_macro": [],
    "raw_cartera": [],
    "limpio_precios": ["raw_precios"],
    "limpio_macro": ["raw_macro"],
    "features_riesgo": ["limpio_precios", "limpio_macro", "raw_cartera"],
    "modelo_pd": ["features_riesgo"],
    "reporte_riesgo": ["modelo_pd", "limpio_precios"],
    "tablero_ejecutivo": ["reporte_riesgo"],
}

aguas_abajo = defaultdict(list)
for ds, ins in depende_de.items():
    for i in ins:
        aguas_abajo[i].append(ds)


def alcanzables(inicio, grafo):
    visto, cola = set(), deque([inicio])
    while cola:
        for sig in grafo.get(cola.popleft(), []):
            if sig not in visto:
                visto.add(sig)
                cola.append(sig)
    return visto


def orden_topologico(deps):
    grado = {k: len(v) for k, v in deps.items()}
    cola = deque(sorted(k for k, g in grado.items() if g == 0))
    orden = []
    while cola:
        x = cola.popleft()
        orden.append(x)
        for d in sorted(aguas_abajo.get(x, [])):
            grado[d] -= 1
            if grado[d] == 0:
                cola.append(d)
    if len(orden) != len(deps):
        raise ValueError("Ciclo detectado en el linaje")
    return orden


print("Orden de ejecucion:", " -> ".join(orden_topologico(depende_de)))
print("Aguas arriba de 'tablero_ejecutivo':", sorted(alcanzables("tablero_ejecutivo", depende_de)))
for fuente in ("raw_macro", "raw_precios"):
    print(f"Si falla '{fuente}' se afecta:", sorted(alcanzables(fuente, aguas_abajo)))

depende_de["raw_precios"] = ["tablero_ejecutivo"]  # ciclo artificial
try:
    orden_topologico(depende_de)
except ValueError as e:
    print("Prueba de ciclo:", e)
