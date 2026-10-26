# Simulaciones de las propuestas prioritarias

Scripts reproducibles con semilla fija (NumPy 2.x, SciPy 1.x). Son diagnósticos de diseño, no calibraciones con datos reales.

| Script | Propuesta | Salida |
|---|---|---|
| `sim21_es_backtest.py` | 2.1: poder del test Z2 de Acerbi–Székely frente a Kupiec | `out21.txt` |
| `sim24_adaptive_var.py` | 2.4: VaR con cobertura adaptativa (ACI) frente a estático | `out24.txt` |
| `sim61_higham_psd.py` | 6.1: proyección de Higham y efecto en el cuantil 99,9 % | `out61.txt` (incluye una primera corrida exploratoria, superada por la siguiente) |
| `sim61_check.py` | 6.1: separación entre ruido aditivo y error muestral | `out61_check.txt` (resultado final) |

Ejecución: `python3 <script>` desde esta carpeta.
