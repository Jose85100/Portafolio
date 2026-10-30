# Auditoría acumulativa de sesgo inflacionario y delegación

S2 del componente estático; programa general S1. Ciclo29 se conserva y ciclo30 extiende el mismo código con delegación conservadora. No evidencia empírica ni teoría nueva.

## Reproducir

Desde esta carpeta: `bash run.sh`. Requiere Python3.11+, venv y acceso a PyPI para dependencias fijadas. Instala, ejecuta tests/cobertura/lint/tipos, reproduce ambos experimentos y notebook narrativo con outputs visibles. Alternativa contenedor: usar imagen Python3.11, copiar carpeta, ejecutar el mismo comando; no imagen certificada.

`results/delegation.csv`, `delegation-summary.json`, `delegation.png` y `notebook.ipynb` contienen evidencia nueva. `results/cases.csv` y comparación anterior conservan baseline29. Fórmulas, unidades, sensibilidad y controles negativos están explicados en notebook e informe. `delegation-config.json` registra malla, fuente sintética y seed no aplicable; versiones fijadas en requirements y registradas por experimento anterior. Baseline justo: misma pérdida social λ y mismos shocks; solo cambia peso delegado q. Tres ideas, matriz prior art y clasificación de aporte en informe. No contrato institucional implementado, no estimación/calibración, no agentes heterogéneos o Markov.
