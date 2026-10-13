# Agentes que llaman herramientas: confiabilidad bajo fallas, sobrecarga y bucles

Patrones de resiliencia para agentes con herramientas (reintentos con *jitter*, presupuesto de reintentos, cortacircuitos, idempotencia, sagas, guardas de presupuesto y de bucles), implementados con reloj virtual y probados por simulación contra **fórmulas exactas**.

## Hallazgos (medidos en el notebook)

- Éxito 1−pⁿ y amplificación (1−pⁿ)/(1−p): la simulación coincide con error máximo < 0,01.
- Con fallas permanentes, reintentar desperdicia carga: con 50 % permanentes, 5 intentos cuestan 3,2× para ganar 15 puntos de éxito.
- El *jitter* completo reduce el pico de la manada atronadora **6 veces** (decorrelado, 14 veces).
- **Falla metaestable:** con colapso por congestión, reintentos agresivos (n=5) dejan el servicio en 64 % de éxito tras desaparecer el disparador, mientras que sin reintentos se recupera de inmediato; el **presupuesto de reintentos** (10 %) lo devuelve a 100 %.
- Sin clave de idempotencia los duplicados siguen una serie geométrica (0,65 efectos de más por operación con 40 % de respuestas perdidas); la **misma clave por operación** los elimina.
- Las sagas cumplen el invariante de estado neto (0 violaciones en 80.000); el atasco decae como cʳ con los reintentos de compensación.
- El detector de bucles tiene falsos positivos q^(k−1) y no ve bucles creativos: el presupuesto es la guarda de última instancia.

## Estructura

```text
src/        librería (módulos: `policies` (reintentos, presupuesto de reintentos, cortacircuitos, `BudgetGuard`, `LoopDetector`), `sim` (servicio con capacidad finita y colapso, herramientas con efectos laterales), `saga` y `agent`.)
tests/      pruebas unitarias (unittest)
docs/       ARCHITECTURE.md (diagrama y decisiones de diseño)
notebook.ipynb   desarrollo completo con pruebas automáticas (assert) y lecturas calculadas desde los datos
main.py     demostración corta
```

## Cómo ejecutar

```bash
python3 main.py                                   # demostración corta
python3 -m unittest discover -s tests             # pruebas unitarias
python3 -m unittest tests.test_notebooks          # (desde la raíz del repo) ejecuta el notebook de principio a fin
```

## Datos

Simulación con semilla fija y verdad conocida; sin datos reales ni confidenciales.

## Límites

- Modelo de capacidad por intervalos de 1 s; la dinámica real de colas es más rica.
- Fallos independientes; en producción hay correlación por dependencias comunes.
- Los agentes son guionados (sin LLM): se evalúa la infraestructura de control, no la calidad de las decisiones.
