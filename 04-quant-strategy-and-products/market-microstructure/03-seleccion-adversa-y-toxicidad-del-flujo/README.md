# Selección adversa y toxicidad del flujo

**Estado: idea de investigación.** Esta carpeta organiza la propuesta existente; no afirma implementación, datos, resultados ni validación.

## Propuesta

- Medir si las transacciones ejecutadas preceden movimientos desfavorables, condicionando por spread, tamaño y hora.
- Aporte: separar costo de spread, impacto transitorio y permanente.

## Contraste propuesto

**Referencia:** Order flow firmado como único proxy de toxicidad.

**Enfoque planteado:** Separar spread, impacto permanente y markout condicional al estado de mercado.

**Evaluación propuesta:** Demostrar calibración de markout y señal incremental sobre spread/proxy simple.

**Prueba decisiva:** pendiente de definir con hipótesis falsable, datos, métrica y criterio de aceptación.

[Volver al área](../README.md) · [Metodología común](../../METODOLOGIA_BASE_E_INNOVACION.md)
