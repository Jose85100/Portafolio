# Contrato de MVP — 2026-10-19

Qué es: prototipo S2 del mercado estático de liquidación de un activo con
enumeración por regímenes y contabilidad. Amplía el componente S2 existente,
sin elevar el programa completo a S3. El modelo dinámico fiscal sigue S1.

Cómo corre: desde la raíz del repo:

```bash
bash 01-economics-and-econometrics/05-macrofinance/01-sovereign-bank-strategic-nexus/fire-sale-price-audit/reproduce.sh
```

Qué produce: tests, cobertura, lint/tipos,7 CSV,2 JSON,figura PNG y notebook
ejecutado. Mide precios, residual, ventas, impago, identidad de balance,
estabilidad de Picard, censos omitidos, costo de pared y asignación Python.

Qué NO cubre: red interbancaria acoplada simultáneamente al mercado, varios
activos, solvencia regulatoria, capital endógeno, colateral, gobierno estratégico,
estimación estructural, identificación, datos reales, intervalos certificados,
probabilidades de selección, bienestar ni óptimos de política.

Madurez por componente:

| Componente | Estado |
|---|---|
| Clearing interbancario estático anterior | S2, no modificado |
| Mercado de un activo y censo de raíces | S2 en este ciclo |
| Acoplamiento simultáneo red/precio | S1 |
| Juego gobierno-bancos, feedback fiscal | S1 |
| Identificación y validación empírica | S1, no ejecutadas |
| Programa completo | S2 parcial, no S3/S4 |

Checklist ejecutado: [x]src; [x]comando único; [x]test pasa; [x]baseline
numérico; [x]salida guardada; [x]README/informe/referencias/MVP;
[x]subcarpeta05-macrofinance correcta; [x]madurez declarada.

No se declara exhaustividad numérica fuera del alcance del modelo. Si el
residual o la separación fallan el solver rechaza, no inventa resultados.
