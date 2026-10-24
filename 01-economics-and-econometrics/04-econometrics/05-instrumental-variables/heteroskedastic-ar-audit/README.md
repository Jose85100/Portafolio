# AR heterocedástico: HC1/HC3 frente a F convencional

Extensión nueva de [weak-iv-inference-audit](../weak-iv-inference-audit/): la auditoría anterior impone homocedasticidad. Este MVP prueba la consecuencia de romperla y añade covarianzas HC1/HC3 al contraste de pendiente reducida de Anderson–Rubin.

**Madurez S2 local**, evidencia sintética. HC1/HC3 se calibran con χ²₁ **asintótico**; no conservan garantía finita exacta del F gaussiano homocedástico. No se certifica dominio completo ni operación real.

## Comando único

Desde esta carpeta, Python3.11+, venv y acceso a PyPI:

```bash
bash run.sh
```

Instala dependencias directas fijadas en `.venv`, ejecuta tests/coverage, ruff, mypy, simulación, costes, genera y ejecuta notebook con IPython limpio en proceso. No requiere credenciales o datos externos. IPython sin kernel/socket queda explícito en metadatos.

## Resultado ejecutado

2.000 réplicas por escenario; β verdadero y nulo=1, c=1, α=5%. Las tasas son rechazos, **no estimación de un efecto empírico**.

| Escenario | F homocedástico | HC1 | HC3 |
|---|---:|---:|---:|
| IID n100 | 4,80% | 5,55% | 4,75% |
| Heterocedástico n100 | 24,00% | 6,65% | 5,90% |
| IID n1000 | 5,50% | 5,55% | 5,55% |
| Heterocedástico n1000 | 23,90% | 5,55% | 5,55% |
| Heterocedástico, exclusión inválida n1000 | 99,65% | 96,25% | 96,05% |

En heterocedasticidad n1000, diferencia HC3−F=−18,35pp, SE pareado0,866pp. En homocedasticidad, ventaja de tamaño desaparece. Exclusión inválida rompe también HC3: no se presenta como potencia ni test de validez del instrumento.

![Comparación de rechazos](results/comparison.png)

## Artefactos y límites

`src/robust.py`, `src/baseline.py` (F anterior reducido, origen explícito), `tests/`, `config.json`, `results/replications.csv` (10.000 filas), `summary.json` con hashes/versiones/hardware, `costs.csv`, notebook ejecutado y siete referencias reales verificadas. `informe.md` desarrolla los14 puntos.

No cubre series/clusters/HAC, varios instrumentos, intervalos invertidos, poder bajo β alternativo, datos reales ni producción. Las cotas MC no sustituyen validación empírica; HC3 puede fallar en muestras pequeñas o alto leverage.
