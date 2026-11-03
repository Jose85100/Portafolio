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

31oct: herramienta `project_affine` añade extremos EADcondicionales en dinero por tramo; `bash run.sh`produce `results/affine.csv`, `affine_metrics.json`, `affine.png`, notebookejecutado. Quéno: saldoaleatorio/censura/calibración/provisiones/operación. `informe31.md` distingue madurezcomponenteS2sintético deM2revisión ymadurezprograma.

1nov: APIreutilizable `project_term_structure` acepta fuerzas de descuento por evento y endpointsEADcon saltos. `bash run.sh` instala/reproduce CSV/JSON/figura y notebookejecutado,22tests. No cubre defaultatómico/prioridad de pagos, curvasnegativas, calibración ni operación. Fuerzaplana recupera31; diferencia suave/discreto se etiqueta cambio de contrato.

2nov: `project_dated` valida fechas civiles y disponibilidad declarada antes de usar el motor existente. `bash run.sh` instala/reproduce lectura de `benchmarks/dated_fixture.json`,27 tests, CSV/JSON/figura y notebook ejecutado. No cubre ACT/ACT, festivos, intradía, verdad de la procedencia o autorización real; no mejora precisión del baseline numérico, añade contrato temporal verificable.

3nov: `project_loss_path` valora EAD/LGD afines deterministas y fuerzas por evento, reutiliza motor y recupera LGD constante. `bash run.sh` instala/reproduce32 tests, CSV/JSON/figura y cuaderno ejecutado. No cubre recuperaciones reales calibradas, LGD fuera[0,1], incertidumbre, fuenteLGD autenticada ni integración automática con fechas2nov. La diferencia frente a producto de medias es covariación temporal de escenarios, no descubrimiento de dependencia causal.
