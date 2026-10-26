# OPE con soporte deficiente: identificación y evidencia finita

Un logger que nunca elige cierta acción no revela su recompensa, aunque haya millones de logs. Este MVP tabular separa **masa objetivo estructuralmente no soportada** de **celdas soportadas pero todavía no observadas**. Devuelve una envolvente de valor mediante intervalos simultáneos por celda para recompensas en [0,1], en vez de extrapolar silenciosamente.

## Reproducción

Python 3.12 y pip, desde esta carpeta:

```bash
bash run.sh
```

Instala herramientas de notebook fijadas y ejecuta 11 tests, 320 evaluaciones de diseño/mundo, 1.280 comparaciones y notebook. Núcleo de biblioteca estándar. Entorno preparado: `PYTHON=/ruta/python SKIP_INSTALL=1 bash run.sh`.

## Experimento que puede refutar una evaluación puntual

Dos mundos producen exactamente el mismo log bajo soporte deficiente. Sólo difieren en una recompensa nunca observada. El valor real de la política objetivo es 0,28 o 0,68; la masa desconocida vale 0,40. En n=2.000:

- IPS truncado, SNIPS sobre soporte y midpoint deciden en todos los casos y se equivocan en el 50% de mundos pareados.
- La envolvente cubre el valor en 80/80 evaluaciones, ancho medio 0,513 y abstención del 100% ante el umbral 0,50. Eso **no son 80 decisiones acertadas**.
- Control con soporte completo: a n=2.000 el ancho cae a 0,146 y la envolvente decide en el 100%, sin errores observados. A n=200 es conservadora y todavía se abstiene.

El sesgo medio de midpoint es casi cero al mezclar ambos mundos, pero su RMSE sigue en 0,20: cancelar sesgos no identifica una política.

## Supuestos y alcance

Se conocen la distribución poblacional de contextos y la política de logging randomizada; objetivo fijo independiente de logs; recompensas IID condicionales a contexto/acción y acotadas en [0,1]; muestra de tamaño fijo. No se infiere probabilidad cero sólo porque una acción no apareció. No se estiman propensiones, distribución de contextos, modelos de recompensa ni efectos causales en datos observacionales reales.

La envolvente usa Hoeffding por celda y unión de eventos; confianza 95% por diseño/muestra, no simultánea entre todos los experimentos ni válida tras parada adaptativa. El baseline IPS se etiqueta truncado cuando falta soporte: no se presenta como estimador insesgado. SNIPS normaliza soporte observado y tampoco recupera acciones inexistentes.

MVP del pilar causal 05; no repite conformal predictivo, outbox o process mining. La contribución es una auditoría reproducible de identificación conocida, no un estimador original frente a literatura OPE.

`results/` conserva estadísticas suficientes, huellas de logs, ejemplos, CSV/JSON y dos SVG. `informe.md` desarrolla 14 puntos y tres ideas comparadas. Componente S2 ejecutado, candidato M2 local sujeto a revisión técnica; programa amplio parcial. Sin datos operativos ni despliegue. Notebook ejecutado con IPython in-process, no kernel aislado.
