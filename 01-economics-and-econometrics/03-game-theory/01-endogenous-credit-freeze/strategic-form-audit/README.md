# Strategic Form Audit — 2026-10-16

Componente **S2** de Endogenous Credit Freeze (programa **S2 parcial**; modelo global
continuo e identificación empírica siguen S1). Auditoría incremental de interoperabilidad,
no un nuevo algoritmo de equilibrio ni evidencia empírica.

## Un único comando desde la raíz del repositorio

```bash
bash 01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/strategic-form-audit/reproduce.sh
```

Requiere Linux/macOS, bash, Python **3.12**, módulo venv e internet para PyPI. Crea
un entorno aislado, instala dependencias fijadas, ejecuta lint/mypy, tests con cobertura,
los cuatro suites previos, benchmark y notebook con outputs reales. Se registran todas
las versiones transitivas en `environment-lock.txt`; para réplica exacta de este entorno
se puede instalar ese lock en vez de requirements.txt. No requiere credenciales ni datos
externos. El notebook se ejecuta con IPython en proceso (sin sockets de kernel);
también se puede abrir y ejecutar en Jupyter desde esta carpeta.

## Pregunta e hipótesis prerregistrada en el script

¿La forma estratégica 4x4 reproduce los cinco equilibrios de comportamiento aislados
del caso regular del repo? H1: Nashpy `vertex_enumeration`, tras proyección, recupera
**5/5** vértices con error coordenado ≤1e-8 y regret interino <1e-8. La aserción del
benchmark falla si no se cumple. No se exige completitud para familias degeneradas.

## Modelo y comparación

Mismo juego sintético del repo: dos prestamistas, estado y señales binarios,
u_i=a_i(theta+alpha*a_j-c), señales condicionalmente independientes. Cuatro planes
contingentes por jugador: 00,01,10,11. Matrices ex ante racionales calculadas mediante
suma directa sobre ocho estados, exportadas en orden NFG (jugador uno varía más rápido).
Un parser propio **limitado a ese header** hace round-trip antes de pasar las matrices
a Nashpy 0.0.43. **No se ejecutó Gambit** ni se verificó su parser externo.

Baseline: `../polyhedral-freeze-audit` conserva familias exactas; pruebas de regresión
incluyen mixed, pure y núcleo común `best_response_grid`. No se compara directamente
OLS/bootstrap con un solver de equilibrio: son problemas distintos.

## Artefactos verificables

- `src/strategic.py`: matrices, exportación, parser restringido, lift/proyección, regret ex ante.
- `tests/`: unitarios, 80 casos Hypothesis deterministas, extremos y solver externo regular.
- `benchmarks/run.py`: cuatro casos canónicos, ocho configuraciones seed 20261016,
  dos métodos Nashpy, throughput en lotes 1/2/4, memoria tracemalloc y control negativo.
- `results/`: CSV de cada equilibrio, resumen, timing/memoria, configuración, diagnósticos,
  NFG exactos, hashes, figura y logs. Un fallo del solver **no** significa cero equilibrios.
- `notebook.ipynb`: tablas/figura ejecutadas; `informe.md`, `MVP.md`, `referencias.bib`.

La memoria mide asignaciones Python, no RSS nativo. Tiempos incluyen conversiones y
round-trip, excluyen instalación; escalabilidad sólo throughput de juegos 4x4,
**no** crecimiento en número de jugadores/tipos. Dependencias hermanas deben conservarse.

## Límites

Los pesos sobre planes estratégicos no son únicos para unas mismas marginales por tipo.
Listar vértices no enumera los infinitos puntos de una familia. La tolerancia ex ante
puede ocultar incentivos interinos grandes de tipos raros: se reportan ambos regrets.
No hay estimación estructural, selección de equilibrio, causalidad ni datos bancarios.
