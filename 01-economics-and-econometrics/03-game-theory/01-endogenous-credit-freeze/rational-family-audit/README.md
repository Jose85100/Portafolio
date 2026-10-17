# Rational Family Audit — 2026-10-17

Componente **S2** de Endogenous Credit Freeze (**programa S2 parcial**). Juego global
continuo e identificación empírica permanecen S1. Novedad incremental de auditoría
e integración, no un algoritmo de enumeración científicamente nuevo.

## Único comando desde la raíz del repositorio

```bash
bash 01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/rational-family-audit/reproduce.sh
```

Entorno reproducible: Linux x86_64, Python3.12 con venv y headers de desarrollo,
GNU gcc/g++/ar/ranlib e internet para PyPI. El script crea .venv e instala requirements
fijados. **PyGambit16.4.1 puede compilar desde fuente: la primera instalación tarda
varios minutos y requiere memoria suficiente.** Se especifica el toolchain GNU para
evitar rutas LLVM no disponibles en ciertos builds de Python. No requiere credenciales.
Para una réplica con las mismas dependencias transitivas, instalar environment-lock.txt
en lugar de requirements.txt. Los directorios hermanos y el núcleo común deben conservarse.

El comando ejecuta ruff, mypy de src, tests con cobertura de ramas, cinco suites de
regresión, benchmark y notebook con outputs reales. El notebook se ejecuta mediante
IPython en proceso para evitar sockets de kernel; se abre/rerun en Jupyter desde aquí.

## Pregunta e hipótesis falsable

¿Los extremos racionales de Gambit permiten reconstruir exactamente las mismas familias
de estrategias de comportamiento que el baseline poliédrico del repo, incluso en los
cuatro casos canónicos degenerados/regulares? H1: **igualdad exacta de todos los factores
convexos máximos y sus dimensiones, cero discrepancias**, y regret interino racional
**cero** en los puntos convexos muestreados. El benchmark falla si no se cumple.

## Implementación y economía

Mismo juego finito: dos prestamistas, theta/s0/s1 binarios, prior interior, señales
condicionalmente independientes, u_i=a_i(theta+alpha*a_j-c). No se estima selección,
parámetros ni causalidad. Nash numérico/racional no sustituye un teorema general.

- Reutiliza el exportador NFG racional y matrices ex ante calculadas por suma de estados.
- **Ejecuta el parser real `pygambit.read_nfg` y comprueba sus32 payoffs exactos.**
- Ejecuta `pygambit.nash.enummixed_solve(..., rational=True)`, sin lrs ni CLI -c.
- Proyecta probabilidades a marginales por tipo; verifica simplex sin tolerancias.
- Reconstruye productos de envolventes convexas mediante bicliques máximos del grafo
  de compatibilidad; compatibilidad calculada con payoffs directos, no con las
  restricciones del baseline. Usa hull2D racional independiente y poda por inclusión.
- Compara con `polyhedral-freeze-audit`; conserva perfiles, familias y muestras exactas.

La reconstrucción es **local**, no salida de familias de Gambit. Depende de recibir
todos los extremos necesarios; no certifica una enumeración externa incompleta.
La búsqueda es exponencial y rechaza más de12 marginales distintas por lado; no es
un solver escalable general. Factores de dimensión0/1/2, productos hasta dimensión4.

## Evidencia y límites

`results/summary.csv`, `families.json`, `profiles.csv`, `samples.csv`, `timing.csv`,
`ablations.csv`, `config.json`, NFG exactos, figura, metadatos y hashes. Configuración:
cuatro casos canónicos, perturbación q=.500000001 y ocho juegos racionales seed20261017.
Lotes1/2/4 miden throughput4x4, no escalabilidad dimensional. Memoria `tracemalloc`
**excluye el núcleo C++ de Gambit y RSS nativo**: no concluir eficiencia global de memoria.

`informe.md` documenta resultados ejecutados, costes, controles negativos, literatura
parcial y fallos de entorno. `notebook.ipynb` conserva tablas/figura ejecutadas; `MVP.md`
delimita madurez. No hay datos bancarios reales, modelo continuo ni validación S3.
