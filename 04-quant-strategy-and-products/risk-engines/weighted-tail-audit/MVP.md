# Contrato del MVP

**Qué es:** API central C++17 de ES ponderado por masa fraccionaria, CLI, tests y benchmark de paridad con el aporte Python y un oráculo racional independiente.

**Cómo corre:** `bash 04-quant-strategy-and-products/risk-engines/weighted-tail-audit/run.sh`, desde la raíz del repositorio completo. Linux/Python 3.12/g++/gcov/make; instalación inicial de herramientas mediante pip.

**Qué produce:** código C++ ejecutado, al menos un CTest, 4.024 comprobaciones, ocho unittest Python, 207 fixtures verificables, 84 mediciones de tiempo, RSS propio y diagnóstico wait4, CSV/JSON/SVG, gcov, metadatos y documentación. Fallo explícito si la tolerancia numérica o el baseline equivalente no coinciden.

**Qué no cubre:** pronóstico, estimación poblacional, calibración de pesos, IFRS 9/SFC/FRTB, pybind11, producción, concurrencia/TSan, portabilidad validada fuera de Linux. No se cambian los resultados de los motores antiguos. Detección de fugas local limitada por el entorno, con fallo conservado; CI la habilita.

**Madurez:** prototipo validado numéricamente (no publicación científica ni producto de producción). La definición de ES, la precisión extendida y la suma compensada son prior art. La contribución es extensión integrada + contrato numérico + nuevo benchmark del repositorio.

**Checklist:** src real, un comando, tests, baseline con números, salida verificable, README/informe/BibTeX/MVP y carpeta correcta. El informe declara métricas observadas y límites.
