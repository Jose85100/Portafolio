# Informe crítico: Collateral Liquidity Choice

Fecha de ejecución: 2026-10-22. Madurez del componente: **S2 (prototipo
ejecutable)**. Madurez del programa `01-sovereign-bank-strategic-nexus`: **S2**;
este experimento amplía evidencia sintética y no eleva el programa completo.

## Pregunta, hipótesis y aporte incremental

¿Puede una elección conjunta y transparente entre liquidación y deuda
colateralizada reducir el costo privado de cubrir un faltante, frente al
baseline de liquidar solamente? En el fixture preregistrado (`g=0.4`, `s=1`,
`q0=1`, `a=0.5`, piso `=0.1`, fracción pignorable `=0.3`, tasa `=0.1`) el
umbral fue una reducción de al menos 50 % y concordancia con una grilla densa
dentro de `1e-5`.

El aporte es pequeño y verificable: un solucionador determinista que enumera
fronteras y puntos estacionarios de un problema unidimensional por tramos, y
un benchmark reproducible contra liquidación pura y búsqueda en grilla. No se
reivindica un nuevo teorema, un equilibrio de red ni prioridad bibliográfica.

## Modelo y supuestos

Para venta `x`, precio terminal `q(x)=max(q_floor,q0-a*x)`, efectivo de venta
`q(x)x`, préstamo mínimo `l=max(g-q(x)x,0)` y restricción
`l <= theta*q(x)*(s-x)`. El objetivo privado reducido es
`(q0-q(x))*x + r*l`. Se supone un banco tomador de la regla de colateral pero
con impacto lineal de su propia venta, activos homogéneos, obligación cierta,
una sola fecha y ausencia de default estratégico. No hay identificación
causal ni datos reales. El costo no es bienestar social: omite acreedores,
externalidades, riesgo y distribución.

## Estado del arte y cobertura

Bichuch y Feinstein formalizan redes con liquidaciones y deuda colateralizada;
Brunnermeier y Pedersen conectan liquidez de mercado y de fondeo; Shleifer y
Vishny estudian ventas forzadas y crédito; Feinstein analiza mecanismos de
liquidación en redes. `referencias.bib` contiene seis registros con DOI,
arXiv o URL.

La búsqueda del 2026-10-22 cubrió consultas dirigidas en arXiv, páginas de
revistas/DOI, NBER, CEPR, SSRN, Semantic Scholar y Papers with Code. La
cobertura fue selectiva, no exhaustiva: algunos índices devolvieron metadatos
duplicados o sin implementación comparable. No encontrar un benchmark
idéntico no significa que no exista.

## Diseño y resultados ejecutados

Seed: `20261022`. Entorno: Python 3.12.14, Linux 6.18.55 x86_64. Se evaluaron
56 configuraciones (`theta` por tasa), 50 problemas aleatorios con grilla de
50,001 puntos, cinco tamaños de grilla de estabilidad y tres escalas de 100 a
10,000 problemas (tres repeticiones). `tracemalloc` mide solo asignaciones de
Python, no RSS total.

| Método, fixture principal | Venta | Préstamo | Precio | Costo privado |
|---|---:|---:|---:|---:|
| Elección conjunta | 0.209839 | 0.212177 | 0.895081 | 0.043234 |
| Solo liquidación | 0.552786 | 0 | 0.723607 | 0.152786 |
| Grilla 200,001 | 0.209840 | 0.212176 | 0.895080 | 0.043234 |

La elección conjunta redujo la liquidación 62.0 % y el costo 71.7 % frente al
baseline. La diferencia de costo con la grilla principal fue `1.66e-7`. En 50
casos aleatorios, la máxima brecha `costo_grilla-costo_solver` fue `9.21e-6`;
es no negativa dentro de la discretización, como se esperaba. Con un millón
de puntos, los errores de liquidación y costo fueron `2.68e-7` y `3.50e-8`.

El solucionador tardó medianas de 0.00658, 0.0711 y 0.777 segundos para 100,
1,000 y 10,000 casos. La grilla de 101 puntos tardó 0.0580, 0.640 y 6.276
segundos: aceleraciones aproximadas de 8.1–9.0x, con memoria Python máxima
similar (2,724,144 frente a 2,723,488 bytes a 10,000 casos). La grilla es un
baseline aproximado, no un competidor estructural completo.

## Pruebas y controles

Ruff, `mypy --strict`, ocho pruebas unitarias/edge cases y 100 ejemplos
property-based pasaron. Cobertura combinada medida: 97 % (142 statements, 28
branches). También pasaron las 8 pruebas del núcleo común, 9 del MVP
`fire-sale-contagion` y 8 de `coupled-clearing`. Los logs crudos están en
`results/`.

El notebook tiene 11 celdas, cinco celdas de código ejecutadas y outputs
visibles. Por restricciones del kernel del contenedor, el generador ejecuta
cada celda secuencialmente en un namespace compartido y serializa outputs con
`nbformat`; no se fingió una ejecución Jupyter externa.

## Fallos y ablaciones negativas

Dos conjeturas usadas inicialmente para redactar tests fueron refutadas antes
del cierre:

1. Colateral abundante con tasa positiva **no** implica préstamo puro. Con
   `theta=1`, la solución aún vende 0.0909 porque evita parte del interés.
2. Impacto de precio nulo **no** implica mezcla sobre la frontera de colateral.
   Bajo este objetivo privado la venta no cuesta, por lo que vender 0.4 domina.

Ambos tests fueron corregidos para codificar el resultado económico real, y
las salidas se preservan en `ablations.csv`. Las otras ablaciones sí dan los
límites esperados: préstamo puro cuando `r=0`, y liquidación pura con `r=2`.

## Limitaciones, sesgos y riesgos

- El precio lineal y el haircut constante son formas funcionales impuestas.
- El préstamo no altera endógenamente tasa, haircut ni precio.
- No hay red, múltiples bancos, incertidumbre, rollover ni dinámica.
- El selector de candidatos es validación numérica, no prueba general de
  optimalidad para funciones fuera de las implementadas.
- Resultados sintéticos no son evidencia empírica ni recomendación de política.
- Minimizar costo privado puede aumentar externalidades no modeladas; por ello
  no se interpreta la caída de costo como mejora de bienestar.

## Reproducibilidad y conclusión

Desde la raíz del repositorio:

```bash
bash 01-economics-and-econometrics/05-macrofinance/01-sovereign-bank-strategic-nexus/collateral-liquidity-choice/reproduce.sh
```

El umbral preregistrado se cumple en el fixture y el solucionador coincide con
la aproximación densa. La conclusión se limita al modelo sintético declarado.
