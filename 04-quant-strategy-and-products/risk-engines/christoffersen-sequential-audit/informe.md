# Informe crítico

## Pregunta, hipótesis y brecha

¿Puede una política secuencial que se abstiene controlar la falsa certeza del Monte
Carlo fijo en el test condicional de Christoffersen? Hipótesis falsable: en 200 seeds
por escenario tendrá cero decisiones distintas al oráculo, mientras el baseline de
999 réplicas tendrá al menos una discrepancia en el escenario próximo a 5%.

El portafolio ya contenía el oráculo exacto y documentaba 32/200 discrepancias del
Monte Carlo fijo, pero no una política de producción que distinguiera incertidumbre
numérica de evidencia estadística. La novedad es incremental y local: una envolvente
ternaria, auditable y con presupuesto explícito de error; no se afirma novedad global.

## Método

Cada permutación condicional genera `X_i=1` si su LR es al menos el observado. En el
look `j`, se usa `delta_j=delta/[j(j+1)]`; la suma de los presupuestos no supera
`delta`. Hoeffding da radio `sqrt(log(2/delta_j)/(2n))`. Se rechaza si el extremo
superior es menor que 5%, no se rechaza si el inferior es mayor, y se abstiene al
llegar a 65.536. La unión de eventos fallidos acota por 1% la probabilidad de una
decisión errónea, bajo independencia del generador.

## Resultados ejecutados

| Escenario | p exacto | Errores fijo / 200 | Errores secuencial / 200 | Indeterminados | Draws medios |
|---|---:|---:|---:|---:|---:|
| Rechazo claro | 0,000985 | 0 | 0 | 0 | 2.048 |
| Frontera | 0,042146 | 32 | 0 | 167 | 65.536 |
| No rechazo claro | 0,503740 | 0 | 0 | 0 | 256 |

La hipótesis se sostuvo en este corpus finito. No es prueba de error cero universal:
la garantía teórica permite hasta 1% y el experimento solo usa 600 trayectorias.

## Fallos y ablaciones negativas

La primera reproducción falló porque el host no incluía CMake; quedó fijado en
`requirements.txt`. El build `Release` desactivó `assert`, detectado por `-Werror`, y
los tests se cambiaron a verificaciones siempre activas. LeakSanitizer falló por
`ptrace`; se registra como no ejecutado. La principal ablación negativa es económica:
el escenario fronterizo consume siempre el máximo y se abstiene 83,5% de las veces.
Forzar una respuesta binaria elimina esa honestidad y reproduce la inestabilidad.

## Limitaciones, sesgos y riesgo de modelo

- Diseño sintético pequeño y condicionado a cuatro excepciones; no representa
  incertidumbre de parámetros VaR ni cambios de régimen.
- Hoeffding es no paramétrica pero conservadora; no se comparó todavía con límites
  binomiales exactos de Gandy/CSM.
- Las semillas no sustituyen evidencia en múltiples tamaños, tasas y clustering.
- Una abstención requiere escalamiento humano o más cómputo; tratarla como “pasa” es
  un riesgo operativo.
- El benchmark mide clasificación frente al oráculo, no pérdida financiera.

## Conclusión

El baseline es barato pero no controla la decisión en la frontera. La política nueva
evita errores observados convirtiéndolos en abstenciones explícitas y termina pronto
cuando la evidencia es clara. Es apropiada como guardrail, no como sustituto del
backtesting regulatorio completo.
