"""Ejecuta el laboratorio IFRS 9 sobre una cartera sintética determinista."""
from src.ifrs9_engine import cartera_sintetica, ecl_componentes, ponderar_escenarios

cartera = cartera_sintetica()
pesos = {"base": .60, "adverso": .30, "severo": .10}
ponderado = ponderar_escenarios(cartera, pesos)
base = ecl_componentes(cartera, "base")
print(base.groupby("stage").agg(exposicion=("ead", "sum"), ecl=("ecl", "sum"), cuentas=("loan_id", "size")).round(2))
print(f"ECL ponderada: {ponderado.ecl_ponderada.sum():,.0f}")
