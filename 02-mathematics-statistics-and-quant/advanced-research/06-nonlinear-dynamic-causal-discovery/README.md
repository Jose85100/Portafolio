# Confusión temporal: auditoría de predicción frente a intervención

**Componente S2 acotado, programa06 parcialmente implementado.** El prototipo cubre una esquina lineal gaussiana con confusor conocido; nonlinearidad, feedback y causal discovery general permanecen como investigación S1. No se afirma validación empírica ni operación.

Desde esta carpeta, Python3.12:

```bash
bash run.sh
```

Instala dependencias fijadas en entorno aislado `.venv`, ejecuta lint, tipos, seis tests, cobertura, benchmark y notebook con salidas reales. `MATH_ENV` permite elegir otro entorno. Notebook ejecutado secuencialmente en un namespace nuevo de IPython; no se afirma prueba con kernel Jupyter separado.

## Aporte del ciclo25oct

El diseño previo pedía distinguir predicción e intervención bajo confusión. Ahora hay un DGP con lags alineados, regresión anidada con F-test, oráculo independiente `scipy.stats.linregress`, identidad FWL y experimento con200 réplicas por configuración. Es un banco de falsación local, no un nuevo algoritmo de causal discovery.

A n=500 y efecto causal cero, el modelo sin control rechaza ausencia de asociación en200/200 réplicas, pero la intervención SCM no cambia Y. Controlar Z en su lag correcto reduce rechazos a9/200 (4.5%, intervalo MC95%2.08–8.37%) y estima pendiente media−0.00627. Con efecto0.3, el control correcto estima0.30008 y rechaza en200/200.

La regresión omitida detecta una asociación real: no se llama falso positivo del test predictivo. El error sería atribuir ese rechazo al efecto causal. Proxy ruidoso y lag incorrecto tampoco identifican el efecto en estos ejemplos.

- [Notebook ejecutado con ecuaciones](notebook.ipynb).
- [Informe de14 puntos y comparación de3ideas](informe.md).
- [Fuentes verificadas](fuentes.md) y [BibTeX](referencias.bib).
- `src/`: generador, test y benchmark; `tests/`: invariantes, oracle y degeneración.
- `results/`:4800 ajustes sobre1200 datasets independientes, CSV/JSON, figura y cobertura.

Los datos son sintéticos, con verdad impuesta. El contraste exacto requiere errores gaussianos IID independientes del diseño completo; la calibración se afirma solo para el modelo con control correcto. La ablación de lag erróneo no cumple esa condición global y sus p-valores se reportan como diagnóstico sin garantía exacta. No es un VAR general ni implementación de PCMCI. EL=83 no aplica y quant-libraries permanece intacto.
