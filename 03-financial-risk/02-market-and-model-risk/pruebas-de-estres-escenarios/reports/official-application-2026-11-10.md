# Estrés oficial de tasa y estrés inverso: aplicación observada

## Pregunta de negocio

¿Qué pérdida aproximada habría generado el mayor choque diario observado en el rendimiento a 10 años y qué shock de tasa alcanzaría una pérdida de 10% para una exposición larga estilizada?

## Fuente y transformación

Se utilizaron 715 observaciones diarias del [U.S. Treasury](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?page=0&type=daily_treasury_yield_curve), del 2024-01-02 al 2026-11-10. El rendimiento par a plazo constante se convierte en un P&L de primer orden con duración modificada fija de 8 años y nocional ilustrativo de USD 10 millones: `P&L ≈ −D_mod × Δy × nocional`.

## Resultado observado

- El mayor aumento diario del rendimiento fue **19 pb** el 2024-04-10, equivalente a una pérdida aproximada de **USD 152.000 (1,52%)** para la posición larga estilizada.
- El mayor descenso diario fue **−19 pb** el 2024-08-02, equivalente a una ganancia aproximada de USD 152.000 bajo el mismo proxy lineal.
- El estrés inverso de 10% requiere un aumento de **125 pb** en un día bajo duración constante. Ningún cambio diario del periodo observado alcanza ese nivel.

La ausencia de un episodio de 125 pb en esta ventana no vuelve imposible el escenario. La serie no incluye episodios anteriores a 2024 y no representa una cartera de renta fija real.

## Decisión y límites

El resultado sirve como contraste observado para la dimensión de tasas y como control de escala del estrés inverso. No permite reemplazar el laboratorio controlado de escenarios multifactores: esta fuente no mide conjuntamente acciones, USD/COP y spreads de crédito. Tampoco incluye convexidad, carry, roll-down, cupón, movimientos de curvas por tenor ni riesgo de base. Antes de usarlo en límites, se necesitan instrumentos y sensibilidades reales, shocks conjuntos, calibración de escenarios y validación independiente.

El [runner reproducible](../official_application.py) guarda cambios diarios, ranking de pérdidas, salida resumen, fuente y hashes. La [figura observada](figures/treasury-historical-stress.png) muestra ganancias y pérdidas aproximadas del factor.
