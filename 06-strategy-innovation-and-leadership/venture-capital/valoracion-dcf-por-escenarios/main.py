import numpy as np
import pandas as pd

anos = 7
escenarios = {
    "fracaso": dict(prob=0.55, ingreso0=0.4, crecimiento=0.15, margen=-0.30, multiplo=0.0, quema_extra=0.0),
    "base":    dict(prob=0.35, ingreso0=0.5, crecimiento=0.70, margen=0.12, multiplo=5.0, quema_extra=0.0),
    "exito":   dict(prob=0.10, ingreso0=0.6, crecimiento=1.10, margen=0.22, multiplo=8.0, quema_extra=0.0),
}


def valor(esc, tasa):
    ingreso = esc["ingreso0"]
    flujos = []
    for _ in range(anos):
        ingreso *= 1 + esc["crecimiento"]
        esc = {**esc, "crecimiento": esc["crecimiento"] * 0.78}  # crecimiento que decae
        flujos.append(ingreso * esc["margen"])
    valor_salida = ingreso * esc["multiplo"]
    t = np.arange(1, anos + 1)
    return float((np.array(flujos) / (1 + tasa) ** t).sum() + valor_salida / (1 + tasa) ** anos)


tasa = 0.30
print(f"Tasa de descuento: {tasa:.0%} (millones de USD)")
total = 0.0
for nombre, esc in escenarios.items():
    v = valor(esc, tasa)
    total += esc["prob"] * v
    print(f"  {nombre:8s} prob={esc['prob']:.2f} valor={v:8.2f}")
print(f"Valor esperado ponderado: {total:.2f}")

print("Sensibilidad del valor esperado a la tasa de descuento:")
for tasa_s in (0.20, 0.25, 0.30, 0.35, 0.40):
    ve = sum(e["prob"] * valor(e, tasa_s) for e in escenarios.values())
    print(f"  tasa {tasa_s:.0%}: {ve:7.2f}")
