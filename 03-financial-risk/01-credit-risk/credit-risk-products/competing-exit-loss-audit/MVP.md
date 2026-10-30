# MVP
- Qué: cronograma de probabilidades activo/default/prepago y pérdida descontada por período.
- Cómo: `bash run.sh`, Python3.12; alternativa SKIP_INSTALL1 con entorno listo.
- Salidas: núcleo tipado, cinco tests, baseline numérico, oráculo racional, CSV/JSON, figura, notebook ejecutado e informe14p.
- No cubre: estimación, censura de datos, Fine-Gray/Cox, IFRS9 completo, staging, SICR, cure, renegociación, recobros, tasas negativas o asesoría de provisión.
- Contrato: probabilidades condicionales mutuamente excluyentes,suma≤1; EAD no ponderada previamente por salidas; descuento fin de período. Calendario uniforme y sin conversión anual/mensual automática.
- Madurez: prototipo sintético de componente, sin elevar todo el dominio aM2/M3.
- Entorno: versiones directas fijadas yvenv; transitivas sinlocktotal.

## Continuidad30
- Añade API de intensidades/año, duraciones/años y pérdida descontada integrada por tramo constante, conservando el motor discreto29.
- Mismo comando reproduce ambos. Nuevos results/calendar.csv,calendar_metrics.json,calendar.png y calendar_notebook.ipynb enseñan derivación y sensibilidad18casos.
- Baseline justo comparte masas/calendario y solo descuenta al cierre. Sesgo anual−3.641841% en escenario sintético; descuento0coincide.
- 11tests y100%85sentencias en ambos núcleos; rúbrica, matrizpriorart y roadmap en informe.md y research-log.md.
- No cubre EAD continua amortizable, ajuste de hazards, censura o validación bancaria. Tipo: reproducción/adaptación incremental local. No se convierte S2/M2 automáticamente.
