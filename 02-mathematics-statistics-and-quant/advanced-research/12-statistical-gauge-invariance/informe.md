# Informe crítico — certificado de invariancia gauge

## 1. Tema y pregunta

Diagnóstico numérico de no identificabilidad por escala: ¿la nulidad de Fisher identifica la órbita `(u,v) ~ (c u,v/c)` y una sección canónica elimina la variación paramétrica sin alterar `u vᵀ`?

## 2. Hipótesis falsable y métrica

Preespecificamos tres puertas: residual relativo `||Jg||/||g|| <= 1e-10`, cambio máximo de predicción tras fijar gauge `<= 1e-12` y reducción del rango de `log(||u||/||v||)` de al menos 99.9%. Además, un punto regular debe tener nulidad uno y el caso degenerado `u=0` debe exhibir nulidad mayor, evitando una falsa certificación como simetría exclusivamente de escala.

## 3. Estado del arte y brecha

La no identificabilidad de factorizaciones y su tratamiento mediante geometría cociente están establecidos; la Fisher también se usa para diagnosticar direcciones poco distinguibles. Las referencias verificadas se listan en `referencias.bib` y su uso exacto en `fuentes.md`. La brecha local era operativa: el programa 12 solo tenía diseño S1, sin certificado ejecutable que enlazara acción de grupo, Jacobiano, Fisher, caso singular y gauge fixing. No se afirma una brecha universal ni novedad algorítmica.

## 4. Proposición validada

Para `mu(u,v)=vec(u vᵀ)`, `Dmu(u,v)[du,dv]=vec(du vᵀ + u dvᵀ)`. Por tanto, para `g=(u,-v)`, `Jg=0`. Si ambos factores son no nulos, la ecuación `du vᵀ + u dvᵀ=0` implica `du=a u` y `dv=-a v`, de modo que el núcleo tiene dimensión uno y `rank(J)=m+n-1`. Con ruido gaussiano iid, `F=JᵀJ/sigma²` tiene el mismo núcleo. En `u=0`, todas las perturbaciones de `v` son invisibles y la nulidad aumenta.

## 5. Diseño experimental

`config.json` fija semilla 20261021; formas 8×6, 32×24 y 96×64; ruido gaussiano 0.01 y 0.05; 20 réplicas por configuración (120 filas); siete escalas entre 1e-6 y 1e6. Baselines: Jacobiano central por diferencias finitas y factores equivalentes sin fijar escala. BLAS se limita a un hilo. Los tiempos son de pared y la memoria es pico Python medido por `tracemalloc`, no RSS total.

## 6. Implementación

`src/gauge.py` contiene la media, Jacobiano analítico y numérico, Fisher, certificado espectral, tangente gauge, sección balanceada y estimador rango uno SVD. `src/benchmark.py` genera datos, conserva cada semilla y materializa CSV, JSON y PNG. El criterio espectral es relativo a la mayor magnitud propia y a precisión de máquina; no sustituye un análisis simbólico general.

## 7. Tests y benchmarks

Los tests cubren invariancia de órbita con propiedades aleatorias, igualdad analítico-numérica, nulidad exacta, caso degenerado, canonicidad, recuperación SVD y entradas inválidas. Los resultados reales de pytest y cobertura están en `benchmarks/tests.txt` y `benchmarks/coverage.json`; lint y tipos forman parte de `make run`. En el contenedor local, los sockets de ZeroMQ están bloqueados: `make run` ejecuta las celdas y captura outputs reales mediante `InteractiveShell` en proceso. El workflow vuelve a ejecutar el mismo notebook con un kernel `nbclient` convencional; esa segunda ruta queda pendiente de confirmación por CI antes de afirmar que pasó.

## 8. Resultados

- Residual gauge máximo: `2.538e-17`.
- Cambio máximo de predicción: `1.534e-15`.
- Reducción mínima de inestabilidad: `100.000000%`.
- Error relativo máximo del Jacobiano frente al baseline: `3.134e-11`.
- En 96×64, sigma=0.05: analítico `1.833` ms, diferencias finitas `12.428` ms, speedup mediano `6.77x`.
- Nulidad: regular `1`, degenerado `u=0` `2`.

Todas las puertas preespecificadas pasaron: `True`. La figura usa ejes y unidades explícitas y no interpreta dispersión entre réplicas como intervalo de confianza.

## 9. Qué funcionó y qué no

El generador conocido aparece en el núcleo con error de redondeo; la sección SVD colapsa una órbita de doce órdenes de magnitud a un representante numéricamente único y conserva la predicción. El caso negativo funciona: la nulidad extra impide etiquetar toda singularidad como la simetría de escala prevista. El baseline numérico aproxima bien el Jacobiano, pero es más costoso; no es un competidor estadístico, sino una referencia de implementación.

## 10. Limitaciones

El detector conoce la parametrización y evalúa un punto estimado; no descubre el grupo. La nulidad local no prueba una simetría global y puede mezclar mala escala, fronteras o degeneraciones. Solo se estudia rango uno, observación completa, ruido iid gaussiano y una sección SVD. Los tiempos dependen del equipo, `tracemalloc` omite memoria nativa de BLAS y 20 réplicas no sustentan inferencia poblacional. No hay datos financieros reales ni validación externa.

## 11. Alcance reducido

Se abandonó deliberadamente el objetivo amplio de detectar simetrías automáticas en mezclas, redes y modelos factoriales generales. El MVP certifica una única acción de escala conocida y demuestra un fallo explícito cuando la nulidad tiene otra causa.

## 12. Cómo correr

`make run` desde esta carpeta. El comando instala un entorno aislado y reproduce tests, benchmark, reporte, figura, notebook y auditoría.

## 13. Rúbrica (1–5)

| Dimensión | Nota | Justificación |
|---|---:|---|
| Novedad incremental | 3 | Integración reproducible, no algoritmo nuevo. |
| Rigor matemático/estadístico | 4 | Proposición exacta, umbrales y caso negativo; alcance simple. |
| Reproducibilidad | 5 | Un comando, semillas y dependencias fijadas. |
| Calidad de código | 4 | Tipos, lint, propiedades y errores explícitos. |
| Claridad del informe | 4 | Trazabilidad de pregunta a límites. |
| Impacto potencial | 3 | Base extensible a factores económicos, aún sintética. |
| Honestidad | 5 | No se confunde nulidad local con simetría global. |
| MVP ejecutable | 5 | Código, tests, baselines, salidas y notebook. |

## 14. Próxima iteración

Extender a rango `r>1` con acción `GL(r)`, comparar sección SVD con optimización cociente y añadir un factor económico sintético con perturbaciones casi no identificables.
