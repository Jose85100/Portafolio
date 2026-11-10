# Motores numéricos de referencia

Seis funciones ejecutables en Python estándar. Entradas ilustrativas; no contienen ponderaciones, límites o anexos regulatorios oficiales.

| Función | Alcance | Exclusiones |
|---|---|---|
| weighted_rwa | Suma exposición por ponderador suministrado | Mitigantes, neteo, CCF, métodos IRB, mercado y operacional |
| ecl | Default futuro con supervivencia y descuento anual | Stage 3, staging, escenarios y medición IFRS 9 completa |
| empirical_es | Cola empírica con masa fraccionaria | Calibración, VaR regulatorio y capital de mercado |
| cash_path | Caja acumulada por flujos firmados | IRL, LCR, NSFR y comportamiento de depósitos |
| operational_losses | Poisson compuesto con severidad exponencial | Calibración, colas extremas y capital operacional |
| kri_status | Umbrales con dirección y dato desconocido | Persistencia, aprobaciones y límites legales |

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s 03-financial-risk/08-regulatory-risk-systems/engines -p 'test_*.py' -v
```

Las pruebas contrastan casos manuales, supervivencia, escala, traslación, descuento, dirección, simulación e inputs inválidos. El chequeo Monte Carlo usa semilla fija y tolerancia amplia; no valida la distribución de pérdidas de una entidad real.
