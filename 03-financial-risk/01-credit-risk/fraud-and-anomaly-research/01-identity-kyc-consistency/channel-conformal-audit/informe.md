# Auditoría KYC por canal — 23 de octubre de 2026

## 1. Título
Rangos conformales por canal con empates y resolución mínima de alerta.

## 2. Hipótesis y novedad incremental
H: en el escenario estacionario heterocedástico, calibrar por canal reduce la brecha absoluta de FPR al menos 3 pp frente a pooled. Local al repositorio: auditoría aislada del score fijo con rangos conservadores y pruebas de abstención. No es nuevo algoritmo conformal ni nueva garantía teórica.

## 3. Estado del arte
Bates et al. estudian p-valores de outliers; no implementamos su calibración condicional ni FDR múltiple. Angelopoulos/Bates y Foundations explican rangos y estratificación. Limits advierte que validez marginal no da validez individual. Beyond exchangeability motiva la ablación de deriva. Cinco registros verificados por buscador en páginas originales, referencias.bib; cobertura no exhaustiva.

## 4. Brecha
Los notebooks KYC existentes trabajan Bayes/calibración y decisiones económicas; faltaba una auditoría mínima de falso positivo por canal con score congelado, empates discretos y falta de resolución finita.

## 5. Diseño/config
`benchmarks/config.json`: semillas 0–59, calibración 499/canal, prueba inliers 2.000/canal y outliers 500/canal, alpha=.05, escalas 1/4, score |normal| redondeado a una decimal, anomalías con desplazamiento 3 sigma. Canales predeterminados, mismos datos para ambos métodos. Semillas son bloques independientes; el error estándar de tasas medias se calcula entre semillas, no fingiendo independencia de todas las alertas que comparten calibración. Normalidad es DGP sintético, no hipótesis necesaria para validez de rangos.

## 6. Implementación
`p=(1+#{cal>=score})/(n+1)`, alertar p<=alpha. Ordenación O(n log n), consulta O(log n); empates conservadores. Calibración y prueba independientes; score sin entrenamiento. `ChannelCalibrator` valida canales y falla ante desconocidos. No se usa regla aprendida para elegir grupos. Si hay contaminación de calibración o deriva, la garantía no se conserva automáticamente.

## 7. Tests y benchmarks
Cinco tests: oráculo manual, enumeración exacta leave-one-out con/sin empates, monotonicidad/permutación, grupos escasos, entradas inválidas y canal desconocido. 100% cobertura medida de 24 sentencias del núcleo, no de todo el proyecto. Ruff src/tests/benchmarks pasa; mypy núcleo pasa. Tiempo y memoria medidos en metrics.json: aproximadamente cuatro segundos, 1,25 MB pico tracemalloc para el bucle; RSS incluye intérprete y bibliotecas. No se mide latencia de despliegue ni escalabilidad distribuida. C++/sanitizers no aplican.

## 8. Resultados
| Método estacionario | FPR canal sigma1 | FPR sigma4 | Detección sigma1 | Detección sigma4 |
|---|---:|---:|---:|---:|
| Pooled | 0,000% | 9,754% | 0,017% | 90,913% |
| Canal | 4,630% | 5,020% | 84,077% | 85,090% |
Brecha FPR 9,754pp ->0,390pp, reducción 9,364pp; H supera 3pp. `summary.csv` incluye SE entre semillas. Estas cifras son desempeño del escenario diseñado, no estimación de desempeño bancario.

## 9. Análisis crítico/ablations negativas
Drift multiplica dispersión de inliers por 1,7: FPR canal 24,107% y 24,846%, falla el nominal. Con nueve calibraciones/canal, p mínimo .1: todas las alertas desaparecen, incluyendo anomalías. Pooled también carece de resolución (.0526). No se oculta caída de detección en canal4 de 90,913 a85,090%; mantener detección uniforme no es objetivo garantizado. No hay comparación con IsolationForest: la pregunta aísla calibración, no aprendizaje del score.

## 10. Limitaciones y riesgos
Intercambiabilidad por canal y referencia inlier aprobada son supuestos fuertes; no validamos etiquetas retrasadas, adversarios, sesgo de selección o múltiples contrastes. No hay garantía FDR de lote, garantía por persona o protección jurídica/ética derivada de las tasas por canal. Canales operativos no equivalen a grupos protegidos. Calibración sintética balanceada; grupos reales desbalanceados requieren nueva evaluación. No usar para rechazar crédito automáticamente. No afirmar que anomalía implica fraude.

## 11. Comando
`bash run.sh` instala versiones y reproduce desde esta carpeta. Notebook ejecutado con IPython in-process por restricción ZeroMQ: real secuencial, outputs capturados; no se simula kernel. Dependencias transitivas resueltas por pip no están completamente bloqueadas. Plataforma/versiones concretas en metrics.json.

## 12. Referencias
Cinco entradas BibTeX verificadas en referencias.bib y registro de alcance en benchmarks/prior-art.md.

## 13. Rúbrica (autoevaluación, no certificación)
Novedad2/5, rigor4, reproducibilidad4, código4, claridad4, impacto3, honestidad5, MVP4. Límites: datos sintéticos, garantías marginales, inspección notebook no render completo, tipos solo núcleo y dependencias transitivas sin lock completo.

## 14. Siguiente iteración
Siguiente iteración recomendada: calibración temporal por canal con referencias inlier aprobadas. Tres tareas: (1) en este proyecto añadir drift detector y abstención; (2) en 01-identity-kyc-consistency validar scores congelados sobre cohortes temporales; (3) en loss-minimization-engine integrar costes/capacidad humana con evaluación independiente.

## Checklist
Código real, comando único, tests, baseline numérico, resultados crudos/figura, notebook con ejecución real, README/informe/referencias/MVP/config/entorno presentes. Revisión independiente del ciclo pendiente; no se afirma publicado ni operacional.
