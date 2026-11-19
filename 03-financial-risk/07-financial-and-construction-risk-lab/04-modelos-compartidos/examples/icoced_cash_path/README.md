# Índice DANE y trayectoria de caja con deuda hipotética

Este ejercicio conecta `project_cash_path` con el derivado ICOCED ya versionado en el [companion de costos](../../../02-construction-enterprise-risk/01-project-cashflow-at-risk/observed-icoced-cost-scenarios/README.md). Fuente: DANE, [ICOCED anexo 7.2, septiembre de 2026](https://www.dane.gov.co/files/operaciones/ICOCED/anex-ICOCED-sep2026.xlsx), consultado el 10-nov-2026. El índice de concreto común de Bogotá-Cundinamarca AR, base dic-2021=100, contiene 57 meses de enero 2022 a septiembre 2026. El CSV derivado se verifica contra SHA-256 `b2e0b7bb52b8b7b588bc7c0bafefc4e54510906694da34a35b3c692de85a4daa`, con control de meses únicos, continuidad, índice positivo y peso.

Para cada ventana histórica móvil de 24 meses, el costo base hipotético de 100 millones COP mensuales se multiplica por `1 − 0,10112 + 0,10112 × índice_t / índice_inicial`. El peso 10,112% es el de la canasta DANE de 2021: **no es la participación observada de concreto en ninguna obra**. Recaudos de 116, servicio de deuda de 15 y caja inicial de 10 millones COP son hipotéticos. CFADS = recaudos − costo; la caja resta el servicio de deuda. El piso es cero y no hay financiación automática, inflación de otros costos ni movimientos intrames.

```bash
python3 03-financial-risk/07-financial-and-construction-risk-lab/04-modelos-compartidos/examples/icoced_cash_path/run.py
```

El [resultado reproducido](results.json) contiene 34 ventanas solapadas; 10 presentan caja negativa y la mayor financiación inicial necesaria es COP 11,15 millones. El menor DSCR de período es aproximadamente 0,867. Las ventanas son escenarios históricos solapados, no probabilidades ni observaciones de proyectos; no validan pronósticos, pérdidas reales o covenants. Se requieren presupuestos, calendario, pagos, caja y deuda por obra para esa validación.

## Sensibilidad a la participación de concreto

Para mostrar cuánto dependen los resultados del supuesto de composición, el runner repite las ventanas con participación hipotética de 0%, 10,112% y 20%. Las ventanas con faltante son respectivamente 0, 10 y 12; el máximo aporte inicial es COP 0, 11,15 y 55,30 millones. Solo 10,112% corresponde al peso de referencia DANE; 0% y 20% son supuestos ilustrativos, no datos de una obra. Los conteos de ventanas solapadas no son probabilidades.
