# Bien público y coste fiscal: matching no significa financiación gratis

MVP pequeño nuevo: dos agentes aportan voluntariamente a un bien público. Se compara no intervención, subsidio que ignora distorsión fiscal y una corrección analítica, contrastada con optimización escalar independiente.

**S2 local**, sin validación empírica. Impuestos fijos se anuncian antes de elegir y equilibran el presupuesto **solo en el Nash previsto**, no ante toda desviación; si los agentes internalizan impuestos marginales, este es otro juego. λ es una pérdida real adicional supuesta, no un parámetro fiscal estimado.

## Reproducir

Desde esta carpeta, Python 3.11+, venv y PyPI:

```bash
bash run.sh
```

Corre tests, cobertura, ruff/mypy, 30 casos determinísticos y notebook ejecutado en IPython limpio en proceso, sin kernel/socket. No simulación larga ni datos externos.

## Evidencia ejecutada

Ancla θL=1, θH=2, coste fiscal adicional λ=0,5:

| Política | Provisión G | Bienestar neto normalizado |
|---|---:|---:|
| No intervenir |1,000000|1,079442|
| Ignorar coste fiscal |2,000000|0,962504|
| Internalizar coste fiscal |1,290994|1,113975|

La política ingenua pierde 0,116938 unidades frente a no intervenir; la corrección gana 0,034533. No son efectos causales estimados. Cuando λ≥1 en el ancla, el óptimo elimina el subsidio y no hay mejora estricta. Transferencias públicas no se cuentan como ganancias de recursos.

![Sensibilidad fiscal](results/comparison.png)

Se guardan `src/`, tests, configuración, 30 casos, oráculo, hashes/versiones, tiempos escalares, figura, notebook ejecutado, cinco referencias verificadas e informe de 14 puntos con tres ideas comparadas. No cubre warm glow, ingreso limitado, competencia fiscal, incertidumbre o equilibrio presupuestario fuera del Nash previsto. Dependencias directas fijadas, no lock transitivo por hash.
