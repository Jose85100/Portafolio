# Nota de diseño: 01-capital-allocation-real-options

## Pregunta y criterio de decisión

El motor compara alternativas de decisión mediante un modelo explícito. Se diseñó para que sus supuestos puedan discutirse y las salidas puedan reproducirse con datos sintéticos antes de considerar una aplicación real.

## Formulación

```text
V_t(s)=max{(s-K)^+,e^{-r}[pV_{t+1}(us)+(1-p)V_{t+1}(ds)]}
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

El árbol representa valor presente del proyecto bajo probabilidades físicas. No es una valoración libre de arbitraje; el descuento es un supuesto exógeno.

## Estrategia de validación

Convergencia frente a horizonte y tamaño del paso, sensibilidad a p, r, volatilidad y coste hundido.

El directorio `tests/` contiene pruebas de referencia, pero todavía no sustituye una campaña de sensibilidad, una validación empírica ni un análisis de rendimiento.

## Lectura económica y estratégica

Un aumento del valor de esperar puede retrasar proyectos con NPV inmediato positivo.

## Riesgos metodológicos

- Los parámetros se introducen manualmente; no existe una calibración a datos reales.
- Los resultados cambian si los escenarios o las probabilidades están mal especificados.
- No hay optimización multiobjetivo, evaluación de incertidumbre paramétrica ni análisis causal identificado.
- No hay integración productiva ni controles de autorización para decisiones de negocio.

## Reproducir

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/01-capital-allocation-real-options/tests -v
```
