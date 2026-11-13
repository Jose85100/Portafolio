# Informe técnico — recuperación transaccional ante fallos sintéticos

## Pregunta y brecha

El proyecto padre documenta S1 y D3–D6 pendientes. Este MVP reduce alcance a **efectos y checkpoints locales en SQLite**. Pregunta falsable: ¿una escritura atómica y deduplicada elimina efectos repetidos después de un crash simulado, frente a reejecución ingenua y a checkpoints separados?

## Prior art

Garcia-Molina y Salem (1987) establecen compensaciones en sagas; Helland (2007) analiza la ausencia de transacciones globales; Gray y Reuter (1992) cubren atomicidad y recuperación; Chandy y Lamport (1985) snapshots; Akidau et al. (2015) trade-off entre corrección, latencia y coste; Fischer et al. (1985) límites de consenso. **No se reivindica algoritmo novedoso**: contribución incremental es una comparación falsable, pareada y reproducible de tres políticas con failpoint explícito.

## Diseño

- 8 semillas [11,23,37,41,59,67,71,83], 80 trabajos por semilla y política, 2 efectos por trabajo.
- Probabilidad 0.65 de un fallo por trabajo; ubicación del fallo uniforme entre los pasos 0 y 1.
- Mismas fallas por semilla para las tres políticas, pero las fronteras de commit difieren deliberadamente.
- `naive`: no recupera progreso. `split`: checkpoint separado, falla en la ventana vulnerable. `atomic`: mismo commit para efecto y progreso, UNIQUE(job_id,step).
- Métricas: duplicados / efectos esperados, finalización, efectos ausentes, ms/job, tiempo de recuperación y memoria pico Python.
- IC 95 % descriptivo con aproximación normal entre ocho semillas, no intervalos poblacionales generalizables.
- Figura SVG y CSV/JSON regenerables con `bash run.sh`.

## Análisis crítico

- El contraste de corrección favorece estructuralmente `atomic` porque su garantía está codificada en el esquema; **no es evidencia de novedad científica**.
- Ablación negativa `split`: separar checkpoint del efecto **no basta** si hay fallo entre commits.
- Ablación `naive`: reiniciar desde cero produce duplicados con fallos, aun si termina el trabajo.
- `atomic` no garantiza exactamente-una-vez fuera de la base SQLite: un API remoto puede ejecutar un efecto antes de perder su respuesta. Requiere idempotency keys externas o outbox.
- Los fallos no matan realmente el proceso; se inyectan excepciones después de commits y se abre nueva conexión. No hay prueba de durabilidad frente a corte eléctrico.
- Tiempos dependen de filesystem, cache, SQLite y máquina; no extrapolar a cargas operativas.
- `tracemalloc` mide asignaciones Python, no toda la memoria nativa de SQLite.
- No hay datos reales, privacidad sensible ni interacción con modelos fundacionales.
- SQLite no modela red, concurrencia, aislamiento distribuido ni ataques. Incluir autenticación, autorización, secretos y límites de recursos antes de M3.

## Seguridad, sesgos y gobernanza

Los identificadores de jobs y payloads son sintéticos; no se registra PII. Validación de longitud de job_id evita entradas no acotadas, y las consultas usan parámetros SQL. Faltan controles RBAC, gestión de secretos, protección contra saturación, cifrado, retención, auditoría inmutable y análisis adversarial. Los escenarios sintéticos uniformes podrían subestimar fallos correlacionados y cargas con colas largas.

## Madurez y gates

**Componente M2 local**: implementación, tests, contrato, baseline y resultados; no M3. Proyecto padre permanece S1 en los demás entregables. Requiere validación independiente, CI remota, fallos reales, multiworker y efectos externos antes de elevar madurez.

## Resultados ejecutados (2026-10-14)


| Política | Duplicados | Duplicación | ms/job | Recuperación ms | Pico Python KiB |
|---|---:|---:|---:|---:|---:|
| naive | 623 | 48.67% | 0.5869 | 0.3509 | 5.16 |
| split | 430 | 33.59% | 0.6309 | 0.3846 | 5.31 |
| atomic | 0 | 0.00% | 0.6252 | 0.3445 | 5.49 |

Se registraron 430 fallos por política y 640 trabajos por política; 1.920 trabajos en total. Tests: 6/6. Cobertura: 97 % de statements en `src/` (5 líneas sin cubrir de `src/__main__.py`, que se ejecutó separadamente con `bash run.sh`). Fuente: `results/raw.csv`, `results/summary.json`, `results/coverage.json`. El rendimiento temporal no es una afirmación de mejora robusta; se requiere repetir en hardware dedicado.
