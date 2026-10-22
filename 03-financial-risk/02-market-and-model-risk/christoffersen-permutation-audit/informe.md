# Informe crítico — calibración condicional de Christoffersen

## Pregunta e hipótesis

¿Condicionar en el número observado de excepciones y permutar su posición corrige el conservadurismo del
`LR_ind` asintótico en una ventana regulatoria corta? La hipótesis preregistrada en README exigía que, bajo
IID(1%) y n=250, el chi-cuadrado rechazara menos de 3%, la permutación no aleatorizada no lo corrigiera
materialmente y la versión aleatorizada quedara a menos de dos puntos porcentuales del 5% nominal.

## Diseño ejecutado

Se simularon 2.000 secuencias de 250 hits por escenario. La nula es Bernoulli IID(1%). La alternativa es una
cadena Markov estacionaria con tasa marginal 1%, `p11=35%` y
`p01 = 0.01*(1-0.35)/(1-0.01)`. Cada conteo de excepciones usa una distribución nula común de 1.999
relocalizaciones uniformes. La semilla única es 20261021. Esta reutilización reduce costo sin cambiar la
distribución condicional comparada dentro de cada conteo.

## Resultados ejecutados

| Escenario | Tasa de excepciones | χ² asintótico | Permutación conservadora | Permutación aleatorizada |
|---|---:|---:|---:|---:|
| IID, tamaño | 1,0030% | 1,20% | 1,25% | 4,80% |
| Markov, potencia | 0,9926% | 41,30% | 37,30% | 45,15% |

La tasa marginal realizada difiere solo 0,0104 puntos porcentuales entre escenarios. El experimento central tardó
0,54 s en la corrida final registrada y alcanzó 161.892 KiB de pico RSS del proceso; `results/run.json` conserva
plataforma y versiones. Son cifras
de una ejecución local reproducible, no intervalos universales.

## Interpretación y ablations negativas

1. La hipótesis se sostuvo en esta semilla: 1,20% y 1,25% son muy inferiores al 5%; 4,80% queda a 0,20 puntos.
2. La ablation negativa es sustantiva: contar todos los empates como extremos no mejora el tamaño y reduce la
   potencia observada de 41,30% a 37,30%. “Exacto por permutación” no significa automáticamente “cerca de 5%”.
3. La aleatorización de empates alcanza 4,80% y eleva potencia a 45,15%, pero una decisión individual puede cambiar
   con el uniforme auxiliar. Esto es matemáticamente legítimo en frecuencia y operacionalmente discutible.
4. El benchmark asintótico sigue teniendo utilidad: es determinista, barato y aquí detecta 41,30% de la alternativa.
   La auditoría no justifica reemplazarlo sin una política explícita sobre aleatorización.

## Tests, calidad y reproducibilidad

La corrida final pasó 10 tests, incluidos property-based, igualdad batch/escalar, edge cases, conservación de tasa
Markov y un experimento end-to-end reducido. Cobertura focalizada: 94%, con ramas inválidas restantes. Ruff,
formato y mypy pasaron. `notebook.ipynb` contiene outputs visibles generados por los mismos CSV/JSON y assertions
ejecutados en el constructor.

Un intento inicial de `nbclient` falló porque el entorno bloqueó los sockets ZMQ del kernel (`Operation not
permitted`). Se redujo el mecanismo, no el alcance analítico: el constructor ejecuta lectura, tablas y assertions
en el proceso Python y materializa esos outputs. En un host normal, el notebook sigue siendo legible y rerunnable;
no se atribuye a esa corrida una ejecución de kernel que no ocurrió.

## Riesgos, sesgos y límites

- DGP sintético y primer orden: no cubre volatilidad GARCH, colas cambiantes, múltiples rezagos ni breaks.
- Se ignora el riesgo de estimación del VaR y el solapamiento de horizontes.
- Condicionar en el total descarta deliberadamente información de cobertura incondicional; debe combinarse con
  Kupiec/exacto y con pruebas de severidad/ES.
- 2.000 trials implican error Monte Carlo: cerca de 5%, el error estándar es aproximadamente 0,49 puntos
  porcentuales. No se hizo barrido de semillas, n, p11 o niveles VaR.
- El costo reportado aprovecha caché por conteo y no representa latencia de un servicio distribuido.
- La regla aleatorizada requiere gobernanza de semillas, trazabilidad y política para resultados marginales.
- No hay datos reales ni afirmación de cumplimiento regulatorio.

## Conclusión

El MVP refuta una simplificación práctica: reemplazar el crítico chi-cuadrado por una permutación conservadora no
garantiza corregir el subdimensionamiento cuando los hits son raros. Los empates discretos son el mecanismo. La
aleatorización recupera el tamaño en este benchmark, pero traslada parte del problema desde estadística hacia
gobierno y reproducibilidad de decisiones.
