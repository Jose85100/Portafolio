# Atribución Euler de ES (MVP de investigación)

Calcula contribuciones por componente a Expected Shortfall para pérdidas aditivas en una distribución finita. El corte de la cuantil VaR es fraccionado; los empates reciben la masa restante proporcionalmente a su peso. La API está en `src/es_attribution.py`, datos generativos y análisis en `run.py`, contrato/config en `benchmarks/config.json`.

Desde la raíz del repositorio, ejecutar un solo comando:

```bash
bash 04-quant-strategy-and-products/risk-engines/es-attribution-audit/run.sh
```

El runner ejecuta tests unitarios y generativos deterministas, compileall, Ruff/mypy si están instalados y regenera escenarios, métricas, sensibilidad y figura. No necesita datos de Drive ni dependencias externas para calcular; matplotlib es opcional para `attribution.png`. Python 3.12 probado. La carpeta `results/` conserva la corrida y los datos crudos.

La corrida usa 5.000 escenarios sintéticos dimensionalmente ilustrativos y semilla fija. No son observaciones empíricas, retornos de mercado, series de BanRep/SFC ni calibración. Ver `informe.md` para derivación, contraste de tres ideas, resultados, límites prudenciales, madurez y roadmap; `prior-art.md` para la revisión de base; `MVP.md` para alcance; `references.bib` para referencias.
