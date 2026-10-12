import pandas as pd

rondas = [
    # nombre, inversion (USD M), valoracion pre-dinero (USD M), pool objetivo post-ronda
    ("semilla", 1.5, 6.0, 0.10),
    ("serie A", 8.0, 32.0, 0.12),
    ("serie B", 25.0, 115.0, 0.10),
]
tenedores = {"fundadores": 1.0}
pool = 0.0
post_prev = 0.0
filas = []
for nombre, inv, pre, pool_obj in rondas:
    post = pre + inv
    f = inv / post
    pool_diluido = pool * (1 - f)
    pool_nuevo = max(pool_obj, pool_diluido)
    base = sum(tenedores.values())
    escala = (1 - f - pool_nuevo) / base
    tenedores = {k: v * escala for k, v in tenedores.items()}
    tenedores[f"inv_{nombre}"] = f
    pool = pool_nuevo
    fila = {"ronda": nombre, "post_dinero_M": post, "pool": pool}
    fila.update(tenedores)
    filas.append(fila)
    fila["valor_fundadores_M"] = tenedores["fundadores"] * post

tabla = pd.DataFrame(filas).set_index("ronda").fillna(0)
pd.options.display.float_format = "{:,.3f}".format
print(tabla.to_string())
total = tabla.drop(columns=["post_dinero_M", "valor_fundadores_M"]).iloc[-1].sum()
print(f"Suma de participaciones tras la ultima ronda: {total:.3f}")
print(f"Fundadores: de 100% a {tabla['fundadores'].iloc[-1]:.1%}")
