# 1. Guardia condicional contra falsa convergencia por aliasing

CICLO_DIARIO del 24 de octubre de 2026. Extensión nueva sobre el MVP de firmas del día anterior, sin duplicar su auditoría de Chen.

## 2. Hipótesis y novedad incremental
Una regla que para cuando dos áreas poligonales coinciden puede confundir aliasing con convergencia. Si existe una cota externa válida de velocidad, una regla basada en intervalo de error debe certificar signos compatibles con verdad analítica o abstenerse. Criterio registrado en config_guard.json: cero signos certificados erróneos en los ocho casos y 200 grillas irregulares; registrar también falsas mesetas. Novedad local: control de parada con supuesto de regularidad auditable y contraejemplo cuando falla, no nuevo teorema de firmas ni prioridad mundial.

## 3. Estado del arte con fuentes
Chevyrev–Kormilitzin y Lyons fundamentan firmas e información de orden; Hambly–Lyons distingue firma completa y equivalencia tree-like. Reizenstein–Graham y Kidger–Lyons ofrecen bibliotecas eficientes. Esos métodos no se vuelven a presentar como invención. Las cinco fuentes primarias se reabrieron el 24 de octubre y se registran en fuentes_guard.md; BibTeX reutilizable en referencias.bib. La cota conservadora siguiente se deriva aquí explícitamente; no se atribuye sin evidencia a una fuente particular.

## 4. Brecha
El prototipo del 23 detectaba aliasing retrospectivamente comparando muestras densas. No tenía una política de refinamiento con condición suficiente para interpretar el signo de área de la curva continua. La extensión separa estabilidad entre mallas, garantía bajo regularidad y presupuesto insuficiente.

## 5. Diseño y configuración
Círculos sintéticos k=1,2,4,8 vueltas, orientaciones ±1, tiempo [0,1], área exacta ±πk y velocidad L=2πk. Duplicación de malla desde cuatro segmentos hasta 4096. Comparadores: fijo de ocho segmentos; parada por diferencia de áreas <=1e-10; refinamiento por cota; mismo guardia con presupuesto ocho. Además 200 grillas irregulares independientes generadas con semilla 20261024 y tamaños16/32/64/128. No se presentan como muestra de desempeño real.

## 6. Implementación, ecuación y demostración
Para curva planar L-Lipschitz, cada arco i tiene longitud <=LΔt_i. Tras trasladar el origen al inicio del arco, la contribución de la cuerda al área es cero. La distancia al inicio del arco es <=LΔt_i, y la variación del arco <=LΔt_i; usando |u∧v|<=||u||||v||:

`|A_arco - A_cuerda| <= 1/2 sup||x-x_i|| Var(x) <= (L Δt_i)^2/2`.

Sumando segmentos: `|A_continua - A_polígono| <= B = L² Σ Δt_i²/2`.

Esto también vale para curvas abiertas cerradas por su cuerda final. Si A_polígono>B, signo positivo; si A_polígono<-B, negativo; en otro caso, abstenerse. `src/aliasing_guard.py` implementa cota, chequeos de entradas/secantes y refinamiento; `src/benchmark_guard.py` guarda experimentos crudos. El programa comprueba secantes compatibles con L, pero eso es solo una condición necesaria. Coste O(n) y memoria O(n) por curva planar; reevalúa todos los nodos tras duplicar, sin caché. Los segmentos finales reportados no son total de consultas: total = suma(n_j+1).

La demostración es analítica en aritmética exacta; implementación float64 sin redondeo dirigido. No se afirma certificación formal intervalar de máquina en fronteras numéricas. Los ejemplos tienen margen amplio.

## 7. Tests y benchmarks ejecutados
`bash run_guard.sh` crea entorno aislado con pins, ejecuta Ruff sobre módulos nuevos/ejecutor/tests, mypy sobre dos módulos, unittest completo (12 tests: siete anteriores y cinco nuevos), cobertura del nuevo núcleo, benchmark y notebook_guard.ipynb. Nuevos tests: grillas irregulares y orientación reversa; falsa meseta; presupuesto insuficiente; inválidos y curva constante; supuesto falso que pasa secantes. Cobertura medida del módulo aliasing_guard: 47/49 sentencias, 96%; no es cobertura del repositorio ni garantía de corrección. Tiempo y pico de asignaciones Python tracemalloc, no RSS, guardados por caso. Sanitizers no aplican, no hay código C/C++ nuevo.

## 8. Resultados reales

| Método | Casos | Signos erróneos no nulos | Sin signo | Segmentos finales medios |
|---|---:|---:|---:|---:|
| Fijo8 | 8 | 0 | 4 | 8 |
| Meseta | 8 | 0 | 4 | 2052 |
| Guardia con L válido | 8 | 0 | 0 | 30 |
| Guardia presupuesto8 | 8 | 0 | 6 | 8 |

Meseta declara convergencia falsa en cuatro casos (cuatro/ocho vueltas, ambas orientaciones), con error máximo25.132741. El guardia certifica ocho signos; error máximo de área2.505324: certificar signo no es estimar área con precisión1e-10. En grillas irregulares,200/200 verdades dentro de cota,114 signos certificados sin error y86 abstenciones. CSV crudos: results/guard_comparison.csv y guard_irregular.csv. Figura results/guard_audit.png; resumen guard_summary.json. Tiempos y memoria no fundamentan promesa de superioridad global: parada por meseta y signo tienen objetivos diferentes.

## 9. Análisis crítico y ablaciones negativas
Eliminar cota convierte parada en meseta y acepta área0 pese a vueltas ocultas. Limitar a ocho segmentos hace abstenerse al guardia en seis casos, resultado preferible a fabricar certeza. Usar L falso6.2 para curva de siete vueltas (L real43.9823) pasa secantes y certifica signo -1 aunque el área continua sea+21.9911: evidencia explícita de que L no se aprende de muestras finitas. El comparador fijo no emite signos erróneos en estos ocho casos, pero no ofrece cota y no resuelve cuatro casos; no se oculta ese resultado.

## 10. Limitaciones, sesgos y madurez
Círculos adversariales elegidos, no evaluación universal. La cota es conservadora y puede abstenerse mucho. L externo es fuerte; si no se conoce, la API no garantiza detección de aliasing. Sin inferencia causal, datos financieros, operación ni reconstrucción de caminos. S2 acotado del componente13; no se promueve a S3/S4 o M2 por agregar simulaciones. EL=83 no aplica. Notebook ejecutado realmente con IPython in-process y namespace fresco por restricción conocida de sockets; metadata lo declara. No se afirma prueba con kernel Jupyter separado.

## 11. Cómo correr
En esta carpeta, Python3.12: `bash run_guard.sh`. Crea .venv-guard e instala requirements.txt, no necesita datos externos. GUARD_ENV permite elegir entorno aislado. `bash run.sh` conserva el experimento anterior y su ampliación académica; no fue sustituido.

## 12. Referencias BibTeX
`referencias.bib` contiene cinco entradas verificadas DOI/arXiv/URL. `fuentes_guard.md` registra fecha, cobertura y relación metodológica. No se afirma revisión exhaustiva ni réplica de bibliotecas externas.

## 13. Rúbrica1–5
Novedad2 (control local con matemáticas elementales conocidas); rigor4 (derivación, contraejemplo, invariantes; no intervalos de máquina); reproducibilidad4 (pins y ejecución real in-process); código4; claridad4; impacto3 (solo método sintético); honestidad5; MVP completo4. Autoevaluación, no certificación externa.

## 14. Siguiente iteración
Siguiente iteración recomendada: sustituir cota global por presupuestos locales de variación conocidos y evaluar curvas no circulares.

1. `advanced-research/13-path-signatures-hidden-dynamics`: incluir curva de área cero con L válido para cuantificar abstención inevitable.
2. `advanced-research/13-path-signatures-hidden-dynamics`: implementar redondeo dirigido antes de reclamar intervalos de máquina.
3. `advanced-research/13-path-signatures-hidden-dynamics`: comparar caché de nodos y refinamiento local manteniendo el mismo contrato de garantía.
