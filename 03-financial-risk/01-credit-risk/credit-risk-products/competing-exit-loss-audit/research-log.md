# Investigación acumulativa — 30 octubre 2026

Base0b2e582; PR105 integrado, solo PR107 de informe abierto al inspeccionar. Se leyeron README raíz, arquitectura/madurez, contratos de productos, src/model.py y negativos29. No hay cambios globales ni contrato compartido modificado.

| Tres ideas | Valor | Decisión |
|---|---|---|
| Calendario e integración de descuento | Cierra explícita limitación29; verdad cerrada e invariancia | Elegida |
| Ajustar hazards a cohortes censuradas | Validez externa | Aplazada: no dataset identificado ni autorizado |
| Selección dependiente PD/prepago | Realismo | Aplazada: exige identificación y covariables |

Original29 se conserva; se añade API separada por semántica de entrada, en la misma línea y carpeta. No crea supuesto avance de teoría. Corrección incremental de aproximación al cierre bajo intensidades constantes por tramo. No añadir C++: coste de otra implementación no resuelve la brecha de calendario en este tamaño.

## Roadmap con criterio de cierre
1. `src/calendar.py`: añadir EAD lineal dentro del tramo con integral independiente y prueba invariancia. Continuar si error<1e-10, ajustar si falla semántica de pagos; cerrar extensión si datos no distinguen EAD condicional.
2. `tests/test_calendar.py`: cohortes censuradas temporales solo cuando exista dataset real con licencia y origen verificables; separar ajuste/evaluación y calibración por causa.
3. `benchmarks/calendar_config.json`: estimar sensibilidad conjunta de PD/prepago; no atribuir causalidad a curvas simuladas y no integrar engineIFRS sin contrato revisado.

## 31oct2026 — EADcondicional afín
Base48dae19; revisados README/arquitectura/madurez, metodología04 recién integrada, informes29/30, notebook30/src/calendar y negativos. CeroPRabiertos al inicio. Matriz de3candidatas y5fuentes en informe31. ElegidaEADafín por hito1delroadmap30; hazardscontinuos aplazados por alcance, calibración censurada aplazada sin datos autorizados. Pregunta/mecanismo acumulados: separa error tiempo de descuento30 de error exposición31. Se conservaAPI30 yEADconstante como casooriginal. Hnumérica confirmada en36regímenes; negativosflat/creciente conservados; sin aporteoriginaldisciplinar.

Hoja de ruta actualizada: fixturepagosdiscretos→criterio invariancia del contrato;curvadescuento por tramo→mismoerror<1e-8;calibración→solo después datasetlicenciado con fecha y separación temporal. Evidencia real pendiente, no ascenderprograma completo.

## 1 de noviembre de 2026 — Eventos de pago y fuerzas por tramo
Basefff631e, ciclo31 integrado, ceroPRabiertos al inicio; se leyeron informe31, fórmula/código afín, notebook y negativos. Las tres ideas comparadas están en informe1101: evento/curva elegido por hitos de roadmap; EADestocástica requiere identificación; calibración censurada bloqueada sin datos licenciados. Sigue pregunta central: separar discretización de cambio de contrato. API nueva compone la anterior; no modifica shared ni risk-engines. Hnumérica36regímenes sostenida; negativo: suavizar pagos produce otro contrato y no se atribuye ganancia algorítmica. Mapa:29masas→30descuento→31exposiciónafín→1101saltos/curvaportramos. Mantiene fórmula original y su caso plano.

Roadmap verificable: fixturecalendario real autorizado con convención día en tests; contrato temporal de curvas/hazards en config; LGDpor evento solo con oráculo/semántica definidos. Continuar con invariancia y error<1e-6; ajustar si defaultatómico; no operar ni calibrar sin fuentes autorizadas.

## 2 de noviembre de 2026 — Fechas y disponibilidad declarada
Base85c51286, incremento1nov integrado y ceroPR abiertos al inicio. Se leyeron informe1101, código/notebook y negativos/roadmap; no se cambia shared ni risk-engines. Tres candidatas comparadas en informe1102: contrato fechas/procedencia elegido por roadmap; ACT/ACT/festivos aplazados por semántica; calibración real bloqueada por datos autorizados ausentes. Pregunta acumulada: distinguir cálculo, contrato e información disponible. Mapa:29masas→30descuento→31EADafín→1101eventos→1102fechas/unidades/sellos temporales.

Se conservan fórmulas y APIs anteriores. H invariancia<1e-12 y6/6gate se sostiene en fixtures sintéticos; negativo relevante: no gana precisión al integrador y no autentica la veracidad de un sello. Roadmap: fixture real autorizado con licencia; zona contractual separada si procede; pruebas externas antes de ACT/ACT. Continuar con invariancia/rechazo, ajustar por convención, no operar con fuentes no verificables.

## 3 de noviembre de 2026 — Producto de EAD y LGD afines
Base2370925, cinco dominios2nov integrados y ceroPR abiertos al iniciar. Revisados código, fórmulas, notebook, negativos y roadmap2nov; no cambia shared ni risk-engines. Tres candidatas en informe1103: autenticidad sin anclas externas no certificable, zona contractual útil pero menor alcance financiero, LGDafín elegida por hito pendiente1nov y mecanismo verificable. Pregunta acumulada: separar discretización, contrato, disponibilidad y ahora variación temporal de severidad.

Mapa:29masas→30descuento→31EADafín→1101eventos→1102fechas/sellos→1103productoEAD×LGD. Se conserva API original y LGDconstante. Herror<1e-8 se sostiene en27 casos; negativo relevante: productodemedias puede sobreestimar o subestimar según pendientes y coincide si alguna trayectoria constante. No originalidad científica acreditada. LGD representa pérdida a fecha de default, no doble descuento de recuperación.

Roadmap: fuenteLGD explícita antes de conectar al adaptador de fechas; contrato/licencia de recuperaciones antes de calibrar; cross-check externo antes de curvas no afines. Continuar con invariantes/recuperación del caso previo; ajustar si semánticaLGD no corresponde; no usar como modelo real sin datos/revisión.
