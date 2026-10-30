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
