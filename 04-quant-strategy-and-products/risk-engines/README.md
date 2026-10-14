# Quant Risk Platform — C++17

Tres motores ejecutables de riesgo cuantitativo en C++17, con clases, componentes reutilizables, manejo de excepciones, CMake y pruebas.

## Compilación

\`\`\`bash
cmake -S 04-quant-strategy-and-products/risk-engines -B build/quant -DCMAKE_BUILD_TYPE=Debug
cmake --build build/quant --parallel
ctest --test-dir build/quant --output-on-failure
./build/quant/credit_risk 100000
./build/quant/market_risk 100000
./build/quant/liquidity_risk 100000
\`\`\`

## Credit Risk Engine
Modelo gaussiano de un factor: \(A_i=\sqrt{\rho_i}Z+\sqrt{1-\rho_i}\epsilon_i\), default si \(A_i<\Phi^{-1}(PD_i)\), pérdida \(L=\sum D_iLGD_iEAD_i\). Calcula EL analítica, EL simulada, error estándar, VaR y ES. LGD y EAD deterministas; no representa IFRS 9 completo ni capital regulatorio. Complejidad O(SN).

## Market Risk Engine
Pérdidas normales IID \(L=-V\sigma Z\), VaR/ES empíricos y función de backtesting Kupiec con pronósticos ex ante. El conteo de excepciones sobre el propio conjunto usado para calcular VaR es **descriptivo, no backtesting válido**. Para uso real: pronósticos fuera de muestra, volatilidad dinámica, EVT y validación de ES. Complejidad O(S log S).

## Liquidity Risk Engine
Trayectoria \(C_{t+1}=C_t+I_t-O_t-M_t\); primer déficit, probabilidad de déficit y máximo déficit de caja. Shocks compartidos elevan salidas y llamadas de margen. No calcula LCR/NSFR, no incorpora fondeo contingente ni liquidez intradía. Complejidad O(SH).

## Ingeniería
Código compartido en \`include/quant/risk.hpp\`, aplicaciones CLI separadas y pruebas de invariantes. Los tres motores utilizan semillas fijas, verifican parámetros y no requieren dependencias externas. Las implementaciones son prototipos cuantitativos reproducibles, **no productos listos para producción**: faltan configuración de portafolios reales, ingestión de datos, logging, perfiles de rendimiento, calibración, validación independiente y controles de despliegue.

## Integración temática
- Crédito: \`03-financial-risk/01-credit-risk/credit-risk-products\`.
- Mercado: \`03-financial-risk/02-market-and-model-risk\`.
- Liquidez: \`03-financial-risk/03-market-liquidity-research\`.

Esta carpeta constituye la biblioteca central para evitar duplicación de código.

## ES de escenarios ponderados — MVP validado numéricamente

[Weighted Tail Audit](weighted-tail-audit/) añade la API pública `include/quant/weighted_tail.hpp` con probabilidades desiguales, VaR inversa-CDF y ES fraccionario. Incluye CLI, oráculo racional, paridad Python/C++, benchmark contra expansión equivalente, pruebas generativas, ASan/UBSan y cobertura. No sustituye `quant::tail` ni cambia los motores existentes; no calcula capital regulatorio.

Desde la raíz del repo, en Linux con Python 3.12/g++/gcov/make:

```bash
bash 04-quant-strategy-and-products/risk-engines/weighted-tail-audit/run.sh
```
