# MVP
- Qué: cronograma de probabilidades activo/default/prepago y pérdida descontada por período.
- Cómo: `bash run.sh`, Python3.12; alternativa SKIP_INSTALL1 con entorno listo.
- Salidas: núcleo tipado, cinco tests, baseline numérico, oráculo racional, CSV/JSON, figura, notebook ejecutado e informe14p.
- No cubre: estimación, censura de datos, Fine-Gray/Cox, IFRS9 completo, staging, SICR, cure, renegociación, recobros, tasas negativas o asesoría de provisión.
- Contrato: probabilidades condicionales mutuamente excluyentes,suma≤1; EAD no ponderada previamente por salidas; descuento fin de período. Calendario uniforme y sin conversión anual/mensual automática.
- Madurez: prototipo sintético de componente, sin elevar todo el dominio aM2/M3.
- Entorno: versiones directas fijadas yvenv; transitivas sinlocktotal.
