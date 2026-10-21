# Técnicas para mejorar detección y minimizar pérdidas

## Objetivo económico

La métrica final propuesta es pérdida neta por cohorte, considerando fraude no prevenido, costo de la intervención y fricción en clientes legítimos. Aumentar recall puede consumir toda la capacidad o elevar costos; por eso se evalúa junto a AP, calibración, carga y costo.

Para caso `i` y acción `a`, el prototipo calcula:

`C_ia = p_i L_i (1-q_a) + c_a + (1-p_i) f_a`.

`p` es probabilidad de fraude, `L` pérdida condicionada a fraude antes de la intervención y neta de recuperaciones previas, `q` fracción prevenible, `c` costo de ejecutar la acción y `f` fricción monetizada para un caso legítimo. Todos comparten moneda COP y horizonte de decisión. El prototipo supone `q` constante por acción. No representa probabilidad de detección, tiempo de recuperación ni valor causal aprendido.

El beneficio frente a continuar es `B_ia=p_i L_i q_a-c_a-(1-p_i)f_a`. Con `L,q,c,f` constantes, una intervención beneficia si `p_i > (c_a+f_a)/(L_i q_a+f_a)`, salvo denominador cero, que debe resolverse comparando costos directamente. El umbral cambia con monto, eficacia y fricción; 0,5 no es un estándar económico.

Ejemplo: dos casos, `p=0,9;L=100.000` y `p=0,2;L=2.000.000`, eficacia 0,8 y una sola revisión disponible. El segundo tiene mayor pérdida prevenible aunque su probabilidad sea menor. El ejemplo forma parte de las pruebas ejecutables.

## Asignación bajo capacidad

Variables binarias `x_ia`, exactamente una acción por caso:

`min sum_i sum_a x_ia C_ia`, sujeto a `sum_a x_ia=1` y `sum_i sum_a t_a x_ia <= T`.

El motor implementa continuar, verificación adicional y revisión. El algoritmo es MILP; no una ordenación heurística por beneficio/minuto. Esa razón puede fallar para acciones indivisibles. `allow` con cero costo, eficacia y esfuerzo garantiza una solución factible incluso con presupuesto cero. Los IDs duplicados se rechazan para obligar al llamador a consolidar casos.

En escenarios `s`, se transforman `p`, `L` y `q` con multiplicadores explícitos, acotando `p,q` a 1. Dos objetivos implementados:

- **Esperado:** minimizar `sum_s w_s sum_ia x_ia C_ias`, con pesos no negativos que suman 1.
- **Minimax finito:** minimizar `z`, imponiendo `sum_ia x_ia C_ias <= z` para cada escenario. Se protege frente al peor escenario declarado; no frente a cualquier distribución posible.

Se compara costo total por escenario, incluyendo la base de continuar. Los costos se escalan internamente por un millón para el solver y luego se reconcilian en COP. Se exige estado óptimo, integralidad y presupuesto; una solución incompleta provoca error explícito. No se acepta una solución como óptima por tener valores de acciones disponibles.

## Escalera de mejora por técnica

| Técnica | Qué mejora o investiga | Qué se implementa ahora | Condición para adoptarla |
|---|---|---|---|
| Reglas trazables | Baseline y razones auditables | Ranking por señales altas en simulación | Comparar al mismo presupuesto y población |
| Logit regularizado | Relación interpretable entre señales y fraude | Ajustado en entrenamiento temporal | Estabilidad y calibración por cohorte |
| Gradient boosting | Interacciones tabulares | Challenger fijo, sin tuning en test | Aporte fuera de muestra y costo incremental |
| Calibración sigmoidal | Correspondencia score–frecuencia | Ajuste posterior, Brier/log loss/bins | Mejorar en validación; no asumir mejora universal |
| Isolation Forest | Exploración de rareza no supervisada | Canal diagnóstico separado | Evidencia adjudicada antes de decisiones económicas |
| Grafo temporal | Coordinación y reutilización | Conteo temporal unitario; cuatro señales aún simuladas | Mejora sobre individual, campañas nuevas y hubs legítimos |
| Cuantiles de ingreso | Incertidumbre y estacionalidad | Diseño de proyecto 03 | Cobertura por actividad y base monetaria coherente |
| Modelo jerárquico/CUSUM | Cambios en grupos con poca muestra | Diseño de proyecto 04 | Falsas alarmas y dependencia temporal bajo control |
| Aprendizaje con costos por caso | Considerar severidad durante ajuste | Pendiente; costos ya entran en decisión | Mantener probabilidad calibrada o separar score económico |
| PU y muestreo de verificación | Etiquetas incompletas y sesgo de investigación | Protocolo, sin implementación | Identificación, soporte y auditoría de selección |
| Stacking temporal | Combinar especialistas | Pendiente | Predicciones fuera de muestra y calibración sin fuga |
| Efecto de intervención | Estimar `q` por caso/acción | Sensibilidad supuesta | Piloto o identificación causal defendible |

No se pondera la clase positiva por exposición y luego se interpreta el resultado como probabilidad sin una nueva validación. Entrenamiento, calibración y optimización económica cumplen funciones distintas. SHAP o importancia de variables, si se añaden, explicarán la respuesta del modelo y no demostrarán intención ni causalidad.

## Severidad, dependencia y riesgo de cola

El prototipo recibe pérdida por caso como dato sintético. Una evolución útil modelará saldo en riesgo, recuperaciones, costos y tiempo de cobro, separando escenarios y segmentos. Si la pérdida ya es neta de una recuperación, no volver a deducirla.

Para campañas relacionadas, sumar beneficios independientes puede duplicar prevención: revisar un caso puede contener varios. La extensión debe definir acciones por campaña, restricciones de vínculo o beneficios conjuntos y evaluar por caso y solicitud. El motor actual exige casos independientes y no acredita optimalidad para ese problema de red.

Como extensión de investigación se propone `E[C]+lambda*CVaR_alpha(C)` con escenarios de pérdida aleatoria y las variables auxiliares `eta,u_s`, `u_s>=C_s-eta`, `u_s>=0`. La fórmula sería `CVaR=eta+sum_s w_s u_s/(1-alpha)`. **No está implementada:** los escenarios actuales alteran costos esperados; su máximo no es la cola de pérdidas realizadas. Necesita un generador de dependencia y pérdidas, incluido el solapamiento de campañas.

## Comparación que evita conclusiones engañosas

Se registran siete políticas: continuar; ranking por reglas; ranking por probabilidad; asignación económica solo con revisión; asignación económica con logit; asignación económica con boosting calibrado; minimax con boosting calibrado. Todas disponen de 75 minutos diarios; pueden usar menos si no hay beneficio.

Ranking probabilístico frente a asignación económica **solo revisión** aísla el cambio de criterio dentro del mismo menú. Asignación económica completa añade verificaciones más baratas y no debe atribuirse toda su diferencia al ranking. Logit y boosting con el mismo menú permiten comparar modelos dentro del motor, aunque no se elegirá el ganador mirando este test.

El costo se publica de tres formas: predicho por el modelo; esperado bajo la probabilidad verdadera conocida únicamente por el simulador; y condicionado a la etiqueta sintética observada, integrando eficacia supuesta. Ninguna mide pérdidas evitadas observadas en un banco. El intervalo bootstrap pareado por día refleja solo 30 días sintéticos; no incluye incertidumbre del entrenamiento, la severidad, la eficacia o el simulador.

La sensibilidad reevalúa las políticas congeladas al reducir la eficacia, incluso hasta cero. Si verificar no evita pérdidas, costos y fricción pueden superar el beneficio: el resultado debe conservarse aunque contradiga la narrativa de mejora.

## Referencias técnicas

- [Calibración, scikit-learn](https://scikit-learn.org/stable/modules/calibration.html): separación entre ajuste de modelo y calibrador; evaluación de confiabilidad.
- [Average precision, scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html): AP no equivale necesariamente al área trapezoidal PR.
- [MILP, SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html): restricciones, integridad, estado y brecha de solución.

Las ecuaciones, escenarios y comparaciones de esta entrega son una formulación experimental propia. No son una política de rechazo ni una certificación de optimización de una cartera real.
