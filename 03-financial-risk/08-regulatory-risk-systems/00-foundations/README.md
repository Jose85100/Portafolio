# Fundamentos comunes

## Tres objetos diferentes

1. Pérdida económica: estimación de pérdida bajo una distribución o escenario.
2. Deterioro contable: reconocimiento conforme al marco contable y al perímetro aplicable.
3. Capital prudencial: recursos y exposiciones definidos por reglas regulatorias.

No sumar ni intercambiar ECL, RWA y pérdida inesperada. IFRS 9 no equivale al SARC ni un ratio de investigación al indicador regulatorio.

## Convenciones matemáticas

- Pérdida positiva; exposición y capital en una moneda común por corrida.
- PD condicional h_t; supervivencia S_0=1, S_t=S_(t-1)(1-h_t); default marginal q_t=S_(t-1)h_t.
- ECL de investigación = suma_s w_s suma_t q_(s,t) LGD_(s,t) EAD_(s,t)/(1+r_s)^t.
- Las probabilidades de escenario suman uno. PD y LGD pertenecen a [0,1]. No confundir PD acumulada, marginal y condicional.
- Stage 1: eventos de default posibles en 12 meses, con pérdidas asociadas durante la vida; no simplemente flujos de caja perdidos durante 12 meses. Stage 2 requiere horizonte lifetime. Stage 3 necesita recuperaciones/descuentos explícitos y no se implementa en este núcleo.
- ES empírico: integral de la cola de la función cuantil; manejar masa fraccionaria en el percentil.
- Brecha de caja: flujos contractuales más supuestos conductuales identificados; no etiquetar como IRL/LCR/NSFR.

## Disciplina de evidencia

Datos sintéticos sirven para verificar invariantes, no para estimar desempeño real. Datos proxy requieren licencia, fecha de descarga y análisis de representatividad. No se han añadido datos de clientes. Los notebooks futuros deben incluir benchmark, sensibilidad, robustez, falsación y limitaciones.
