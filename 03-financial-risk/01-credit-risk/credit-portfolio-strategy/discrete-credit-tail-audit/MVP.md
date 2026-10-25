# MVP
- Qué: distribución finita por convolución de Bernoullis independientes, VaR/ES de átomos, auditoría de normal y MonteCarlo.
- Cómo: `bash run.sh`, Python 3.12 desde esta carpeta.
- Salidas: src,tests,results CSV/JSON/figura, notebook ejecutado y documentación. Núcleo stdlib sin scipy.
- No cubre: PD/LGD estimadas, correlación, migración, descuento, provisión, capital regulatorio, pesos fraccionarios o grid>20000. Fallar explícitamente no equivale a redondear silenciosamente.
- Estado: prototipo sintético de componente; revisión independiente aparte, no operación.
- Entorno: requisitos directos fijados; instrucciones venv y límites enREADME.
