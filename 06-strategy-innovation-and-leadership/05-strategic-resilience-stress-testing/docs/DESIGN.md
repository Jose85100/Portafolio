# Nota de diseño: 05-strategic-resilience-stress-testing

## Pregunta y criterio de decisión

El motor compara alternativas de decisión mediante un modelo explícito. Se diseñó para que sus supuestos puedan discutirse y las salidas puedan reproducirse con datos sintéticos antes de considerar una aplicación real.

## Formulación

```text
C_t=C_{t−1}+Ingresos_t−Costos_t; τ=inf{t:C_t<C_min}; P(τ≤H)=Σ_s p_s·1{τ_s≤H}
```

## Arquitectura

```mermaid
flowchart LR
  A["Parámetros y escenarios"] --> B["Validación"]
  B --> C["Motor de decisión"]
  C --> D["Métricas y política"]
  D --> E["Pruebas de invariantes"]
```

La ejecución es local y no depende de servicios externos.

## Supuestos que importan

Escenarios discretos exógenos; el retraso de cobro omite flujos pendientes después del horizonte y no modela deuda ni impuestos.

## Estrategia de validación

Probar shocks de ingresos y costos, covenant estricto, retrasos y horizontes.

El directorio `tests/` contiene pruebas de referencia, pero todavía no sustituye una campaña de sensibilidad, una validación empírica ni un análisis de rendimiento.

## Lectura económica y estratégica

La solvencia contable no garantiza liquidez; el primer incumplimiento puede preceder al agotamiento total de caja.

## Riesgos metodológicos

- Los parámetros se introducen manualmente; no existe una calibración a datos reales.
- Los resultados cambian si los escenarios o las probabilidades están mal especificados.
- No hay optimización multiobjetivo, evaluación de incertidumbre paramétrica ni análisis causal identificado.
- No hay integración productiva ni controles de autorización para decisiones de negocio.

## Reproducir

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/05-strategic-resilience-stress-testing/tests -v
```
