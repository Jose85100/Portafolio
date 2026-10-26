# Screening de dos tipos: incentivos y ejecución

Primer componente estático S2 dentro del programa de diseño de mecanismos: menú de cantidad y transferencia con participación (IR) e incentivos (IC), solución analítica y oráculo numérico independiente. Rota de econometría a microeconomía, sin repetir auditorías IV o RD.

**Alcance:** q es capacidad/cantidad normalizada de servicio, t una transferencia. No son tasas de interés, probabilidades de default ni flujos de repago. El modelo no prueba todavía la hipótesis del programa sobre contratos contingentes al flujo. **S2 únicamente del componente**, no del programa completo.

## Reproducir

Desde esta carpeta, Python 3.11+, venv y acceso a PyPI:

```bash
bash run.sh
```

Instala dependencias fijadas, ejecuta tests/cobertura, ruff/mypy, auditoría de 81 economías, costes y notebook narrativo. El notebook se ejecuta secuencialmente en IPython limpio en proceso, sin kernel/socket; conserva outputs y aborta ante errores.

## Resultado sintético ejecutado

Tipos θL=1, θH=2, probabilidad alta p=0,2, coste c=1:

| Diseño o stress | Beneficio esperado, unidades normalizadas |
|---|---:|
| Mejor contrato único, valor ideal IC/IR débil | 0,5000000 |
| Contrato único con participación estricta | 0,4999990 |
| Menú analítico, equilibrio veraz débil | 0,6250000 |
| Menú con descuentos que hacen estricta la selección | 0,6249988 |
| Menú débil, desempates adversos y opción externa | 0,0937500 |
| Menú estricto diseñado para θL=1, pero θL real=0,8 | 0,2499996 |

Mejora de beneficio cercana al 25% solo bajo los supuestos del ejemplo. Desaparece cuando p≥0,5 y se excluye al tipo bajo. Una preferencia mal especificada destruye participación; IC débil no garantiza elección veraz única. Beneficio del principal no equivale a bienestar o inclusión.

![Resultados y falsaciones](results/comparison.png)

La grilla contiene 81 economías y compara solución cerrada con QP de cuatro variables, inicializado en cero. Se conserva error numérico real, no una supuesta validación empírica. Ver `results/grid.csv`, `summary.json`, notebook ejecutado, cinco referencias verificadas e `informe.md` con 14 puntos y selección entre tres ideas.

No cubre competencia, presupuesto, aversión al riesgo, varios periodos, más tipos, impago, flujos contingentes, moral hazard ni operación real. Dependencias directas fijadas; no lock transitivo por hash.
