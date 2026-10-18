# Revisión y desarrollo semanal — 12–17 de octubre de 2026

Se inspeccionó el inventario del repositorio completo y el historial de la semana en horario de Colombia: **190 commits, incluidos merges**. No se interpreta ese número como 190 aportes independientes. El snapshot de `main` es `41fc967`; la base de trabajo incluye el desarrollo previo del PR #48, commit `865c326`.

## Resultado concreto

- **35 laboratorios económicos** dejaron de usar el mismo DGP OLS genérico: ahora tienen un mecanismo propio, supuestos, comparadores, sensibilidad y resultados recalculados.
- **9 notebooks de auditoría** se ampliaron: familias puras/mixtas/poliédricas, vintages, problema inverso, eventos raros, ES ponderado, IFRS 9 y rebalanceo beneficio/costo.
- **3 notebooks nuevos** acompañan el núcleo numérico, recuperación durable SQLite y los 15 motores ejecutivos.
- **1 notebook adicional se corrigió** durante la regresión: Markowitz podía devolver `None.x` tras fallar todos sus inicios y usaba un inicio incompatible con el tope por activo. Ahora tiene inicios factibles, gradientes analíticos, validación y rechazo explícito.
- Se conservaron los **6 notebooks ampliados previamente**; no se duplicaron sus experimentos.

En total, esta pasada desarrolla o repara **48 notebooks adicionales**. Con los seis anteriores, el PR contiene trabajo sobre **54 notebooks distintos**. El inventario final registra **94 notebooks**: 91 existentes y tres nuevos; los 40 restantes se conservan sin ampliación automática por tener desarrollo extenso.

## Desarrollo por dominio

| Dominio | Trabajo de esta pasada |
|---|---|
| Economía | Phillips con variable omitida, proyecciones locales con respuesta analítica, traslado con rezagos, regímenes observados, productividad y error de capital, regla de política con inercia y combinación fuera de muestra |
| Microeconomía | Demanda con IV, puntos fijos de red, riesgo de caja, matching restringido, subastas, fricciones de pago y ahorro precautorio de dos períodos |
| Juegos | Coordinación bancaria, mejores respuestas de precios, defensa minimax, negociación Nash, subsidios, información compartida e inspección; además tres auditorías BNE recalculadas |
| Econometría | Within, DiD y placebo, IV débil, GARCH oracle, cobertura bayesiana fija, regresión cuantílica LP, impactos espaciales y disponibilidad vintage |
| Macrofinanzas | Agregación multiescenario, pagos interbancarios, spread exacto, capital y RWA, hedge frente a margen, gridlock y precisión con eventos raros |
| Matemáticas | Contracción espectral y cobertura, geometría de propuestas IS, convergencia fuerte acoplada, error MC y convenciones ES |
| Riesgo | Masa fraccionaria ES; PD marginal frente a condicional, EAD amortizante y staging ilustrativo IFRS 9 |
| Quant | Sensibilidad pareada del rebalanceo y corrección del optimizador Markowitz |
| IA | Recuperación SQLite con ventana de fallo, reintentos e identidad; control negativo de efectos externos |
| Dirección | Inputs nuevos y fronteras de decisión para los 15 motores existentes, sin agregar métricas incompatibles en un score |

Los laboratorios estocásticos de economía conservan 40 réplicas por escenario. Los casos de equilibrio o identidades deterministas no adquieren incertidumbre estadística por repetirlos; sus bandas degeneradas se explican. Las bandas de réplicas se distinguen de intervalos de confianza y de escenarios económicos.

## Resultados que cambian una lectura

1. Omitir expectativas correlacionadas cambia la pendiente de Phillips, aunque el ajuste OLS sea preciso; la regresión completa conserva el parámetro del DGP.
2. Un instrumento exógeno pero débil genera una distribución IV muy dispersa: una media o un único intervalo puede ocultarlo.
3. La varianza posterior puede ser pequeña por un prior concentrado aunque una dirección sea poco observada; se contrasta cobertura fija y prior predictiva por separado.
4. El tilt de una sola cola puede tener una varianza teórica enorme y aparentar estabilidad en pocas réplicas; el muestreo directo puede devolver cero.
5. El filtro de rebalanceo puede reducir rotación y empeorar Sharpe. La nueva sensibilidad conserva ese resultado desfavorable.
6. La atomicidad SQLite protege efectos locales a la misma transacción; no convierte un retry de API externa en exactly-once.
7. El motor IFRS 9 sigue siendo ilustrativo: una extensión de horizonte no resuelve por sí sola el tratamiento de créditos ya deteriorados.

## Validación y límites de reproducción

**48/48 notebooks desarrollados o reparados** ejecutaron todas sus celdas de código en orden y pasaron sus asserts; se validó su formato y se guardaron resultados y figuras. Se inspeccionaron las figuras de los desarrollos nuevos y se corrigieron etiquetas/fechas observadas durante QA. Se usó IPython directo en procesos aislados porque el entorno no permitió sockets de kernel Jupyter. No se interpreta esa ejecución como una validación empírica de modelos.

Las suites Python existentes: **45/45** completas en la ejecución local registrada. Las **tres compilaciones C++** y sus pruebas CTest pasaron. El detalle, versiones y cualquier suite pendiente están en [validation.json](validation.json).

La regresión adicional sobre 41 notebooks extensos **no se completó** dentro del presupuesto de 240 segundos por notebook: `gradient-boosting-vs-logit` agotó ese tiempo. Se resolvieron dependencias locales para ARIMA, regularización y GARCH y esos tres reruns pasaron. Se reparó y ejecutó Markowitz. No se afirma que toda la suite de notebooks del repositorio haya pasado en este entorno. La CI del PR es una comprobación separada.

Las versiones del entorno local se registran, y pueden diferir del lock de investigación. Para reproducción bajo el entorno del repositorio:

```bash
python -m pip install -r requirements-research.txt
python scripts/execute_notebooks.py --all --output artifacts/notebooks
```

Para un notebook concreto, ejecutarlo desde su carpeta o usar el script del repositorio con su ruta. Las suites que importan `_path` deben ejecutarse con sus tests en el path o mediante el comando unittest documentado por cada proyecto; no se reinterpretan errores de colección debidos al comando de prueba como errores del modelo.

## Propuestas que siguen siendo propuestas

El inventario también registra **197 hojas documentales sin ejecutable local** según una regla estructural explícita. Incluye fundamentos y diseños; no es una cuenta de productos incompletos ni una evaluación de novedad. No se convirtieron automáticamente todos los diseños en código ni se elevaron a una madurez superior. Las especificaciones de riesgo empresarial, construcción, investigación avanzada e IA conservan sus límites.

## Evidencia navegable

- [Inventario de los 94 notebooks](notebook_inventory.csv): acción, tamaño, ejecución y hash.
- [Inventario documental](documentary_inventory.csv): hojas sin código local, con criterio estructural.
- [Validación y entorno](validation.json): resultados y límites de cada capa.
- [Commits incluidos en la revisión](commit_scope.txt): historial del snapshot auditado.
- [Sensibilidad de los 15 motores ejecutivos](../../06-strategy-innovation-and-leadership/weekly-decision-audit.ipynb).
- [Recuperación durable](../../05-artificial-intelligence-and-computational-systems/10-ai-orchestration-engineering/06-fault-tolerant-ai-execution-recovery/mvp-durable-checkpoints/notebook.ipynb).
- [Convergencia del núcleo numérico](../../02-mathematics-statistics-and-quant/numerical-core/notebook.ipynb).
