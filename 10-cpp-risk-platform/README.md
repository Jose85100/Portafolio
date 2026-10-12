# Quant Risk Platform — C++17

Tres motores ejecutables de riesgo cuantitativo en C++17, con clases, componentes reutilizables, manejo de excepciones, CMake y pruebas.

## Compilación

\`\`\`bash
cmake -S 10-cpp-risk-platform -B build/quant -DCMAKE_BUILD_TYPE=Debug
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
- Crédito: \`01-riesgo-de-credito-productos\`.
- Mercado: \`03-riesgo-financiero-modelos\`.
- Liquidez: \`09-riesgo-mercado-liquidez-avanzado\`.

Esta carpeta constituye la biblioteca central para evitar duplicación de código.
