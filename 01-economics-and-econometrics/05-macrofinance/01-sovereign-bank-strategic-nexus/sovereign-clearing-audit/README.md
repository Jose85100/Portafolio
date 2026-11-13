# Sovereign Clearing Audit — 2026-10-18

**Componente estático S2**, nuevo en Sovereign–Bank Strategic Nexus. Programa **S2
parcial**: el juego dinámico, precios endógenos, garantías e identificación empírica
siguen S1. Sin resultados empíricos de Colombia ni estimación estructural completa.

## Instalar y reproducir con un comando desde la raíz

```bash
bash 01-economics-and-econometrics/05-macrofinance/01-sovereign-bank-strategic-nexus/sovereign-clearing-audit/reproduce.sh
```

Entorno: Linux/macOS, bash, Python **3.12**, módulo venv e internet para PyPI. El script
crea .venv, instala requirements fijados, corre tests/cobertura, ruff y mypy de src,
suite común, benchmark y notebook con outputs. environment-lock.txt registra también
dependencias transitivas; puede instalarse ese lock para replicar sus versiones.
No credenciales ni datos externos. Debe conservarse el notebook hermano
`../../04-liquidity-contagion-network/notebooks/01-estimation-and-robustness.ipynb`.
El notebook nuevo ejecuta cálculos y narrativa con IPython en proceso (sin sockets
de kernel); puede abrirse en Jupyter desde esta carpeta.

## Pregunta, brecha e hipótesis falsable

El laboratorio semanal **ya implementa Eisenberg–Noe**: no se presenta como novedad.
Faltaba un componente modular del programa soberano con balances, contrato de parada,
oráculos independientes y reconciliación de recursos. La contribución incremental
local es esa integración y sus controles negativos, no un algoritmo EN nuevo.

H1: con anclas moderadas, ancho L1≤1e-8, discrepancia L1 frente al oráculo racional
≤ancho+1e-12 y discrepancia LP–racional <1e-7 en30 redes; reproducción del notebook
semanal en sus cinco escenarios con diferencia de impago bruto <1e-8. El script
falla si se incumple. En redes casi cerradas el método debe **rechazar por presupuesto**
si no cierra las cotas, no fabricar precisión.

## Modelo y contrato

L[i,j] es deuda de i con j; deuda fuera de red l_i; pbar_i=sum_j L[i,j]+l_i;
Pi[i,j]=L[i,j]/pbar_i. Activos disponibles x_i(h)=cash_i+(1-h)*sovereign_i.

$$p=\min(\bar p,x+\Pi^Tp).$$

Responsabilidad limitada, pago proporcional, prioridad de deuda y ausencia de costos
de quiebra. Cada deudor debe una cantidad positiva fuera de red: beta=max filas(Pi)<1.
Activos soberanos liquidables al precio fijo supuesto; **no** colateral, haircuts
endógenos, fire sales ni feedback del banco al soberano.

Dos iteraciones, desde0 y pbar, dan cotas en aritmética exacta; el código flotante
las contrasta con HiGHS y Fraction. **No** es aritmética de intervalos con redondeo
dirigido ni prueba formal de precisión. Si no cierra el ancho, lanza RuntimeError.
El oráculo racional enumera conjuntos de default y está limitado a seis bancos.

## Resultados y baselines

- Ring principal3 bancos, obligaciones1 cada uno, deuda externa.1, exposición soberana
  concentrada. Haircut total: impago bruto~1 frente a déficit de una pasada~.1;
  acreedores externos pierden~.1. No interpretar1 como pérdida social multiplicada.
- Contraste directo con la función real del notebook semanal, sin editarlo.
- Residual solo y éxito nominal de LP no certifican error de pagos: caso casi cerrado
  con residual~1.5e-9 y error L1~1.5; cotas rechazan tras10000 iteraciones.
- Benchmarks 8/32/128 bancos, tres repeticiones por método; residual ajustado incluido
  para comparar precisión global. Es una familia de redes simple, no complejidad general.

Salidas: `results/stress.csv`, `payments.csv`, `oracles.csv`, `weekly_regression.csv`,
`near_closed.csv`, `timing.csv`, config/metadatos/hashes, figura y logs. `notebook.ipynb`
ejecutado; `informe.md` explica fallos, límites y literatura; `MVP.md` delimita alcance.
Memoria: tracemalloc mide asignaciones Python, **excluye RSS y memoria nativa HiGHS**.

OLS y expected_credit_loss del núcleo común resuelven problemas distintos: se ejecuta
su suite de regresión, pero no se comparan como si fueran solvers de clearing.
