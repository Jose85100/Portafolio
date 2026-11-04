# Informe crítico: replay bitemporal de vínculos delta

1. **Título y línea:** auditoría point-in-time de identidades; continuación del gate de revisiones completas del 3-nov.
2. **Hipótesis/novedad incremental:** replay ordenado por tiempo efectivo, condicionado al corte de disponibilidad, coincide con oráculo; evento tardío sobre vigencia vieja no debe reactivar relación posterior. Es una adaptación de ingeniería, no método científico original.
3. **Estado del arte:** temporal DB distinguish valid/transaction time (Clifford-Isakowitz; Jensen-Snodgrass; Torp et al.); ML leakage (Kapoor-Narayanan); validaciones temporales (scikit-learn). Matriz `prior_art_delta1104.md`; seis fuentes listadas en `referencias.bib`; verificación bibliográfica heredada de auditoría 3-nov, limitada a metadata/abstract y documentos oficiales.
4. **Brecha:** el gate anterior solo aceptaba snapshot/full replacement, sin reconstruir cambios incrementales.
5. **Diseño/config:** ledger sintético 3 eventos/arista, semilla 1104, 1/10/100/1000 aristas; query y corte fijados en `config_delta1104.json`; no datos personales.
6. **Implementación/fórmula:** `src/delta_replay.py`; para cada arista `x`, filtrar `A_e<=c, V_e<=t`, luego escoger `e* = argmax V_e`; estado activo si `action(e*)=link`. Ties contradictorios y event_id repetido bloquean. Se conservan disponibilidad y eficacia separadas.
7. **Tests/benchmarks:** `bash run_delta_audit.sh`: 4 tests, Ruff, mypy strict, benchmark; notebook 2/2 code cells. Sin property-based ni cobertura reportada.
8. **Resultados/figura:** raw/summary en `results/delta1104`; baseline de última llegada re-activa falsamente todos los vínculos en contrajemplo; error: 1, 10, 100, 1000 falsas admisiones en 3, 30, 300, 3000 eventos. Replay mediano local: 4,597; 29,554; 373,784; 4,635,865 ns. PNG de costo log-log; benchmark sintético no es dato real.
9. **Análisis crítico:** prueba refuta el orden de llegada como sustituto de vigencia; no demuestra que ese bug prevalezca en pipeline real.
10. **Límites/sesgos:** timestamps se tratan como confiables; no autentica fuente, equivale pares a identidad relacional, no modela esquema/correcciones complejas, no mide leakage predictivo.
11. **Comando:** desde la carpeta de proyecto, `bash run_delta_audit.sh`.
12. **Referencias:** BibTeX en `referencias.bib`; referencias temáticas en `prior_art_delta1104.md`.
13. **Rúbrica 1–5 (novedad, rigor, reproducibilidad, código, claridad, impacto, honestidad, MVP):** 2,3,4,3,3,2,5,3. Ampliada (profundidad, aporte defendible, calidad experimental, utilidad, reproducibilidad, honestidad): 3,2,3,3,4,5.
14. **Siguiente iteración:** acordar semántica de event sourcing y autenticidad con dueño de datos; extender solo con fixtures aprobados.

Madurez: M1 incremental local; sin validación/operación. Qué sabemos: una llegada tardía puede contradecir el orden efectivo. Qué construimos: replay pequeño, determinista y refutable. Qué permite: probar fixture delta con tiempos bifocales; no autoriza uso productivo.
