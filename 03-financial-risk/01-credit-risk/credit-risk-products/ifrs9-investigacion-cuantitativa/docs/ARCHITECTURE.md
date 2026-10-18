# Arquitectura de la plataforma multimodelo

## Qué se implementa

El paquete `src/multimodel` agrega familias intercambiables sin sustituir la implementación anual de `src/ifrs9_engine.py`. La primera conserva su función didáctica y su notebook; el motor nuevo trabaja mensualmente y toma los stages como entrada explícita. No hay una carpeta por cada combinación: los componentes se reutilizan para evitar divergencias entre copias.

| Módulo | Responsabilidad | Resultado |
|---|---|---|
| `contracts.py` | Rangos, finitud, dimensiones, pesos, supervivencia | Rechazos explícitos e identidades comunes |
| `pd.py` | Logit anual, hazard mensual, Markov | Matriz contrato × mes de primer default |
| `lgd.py` | Workout segmentado, logit fraccional, flujos | LGD descontada **a default** |
| `ead.py` | Anualidad, prepago independiente, CCF | Exposición al inicio del mes, sin multiplicar por supervivencia de default |
| `staging.py` | Política SICR cuantitativa y cualitativa | Stage y motivo, índices preservados |
| `engine.py` | Integración, escenarios, Stage 3, matriz simplificada | ECL por contrato, escenario y contribución mensual |
| `data.py` | Generadores deterministas y escenarios de referencia | Datos sintéticos con semilla explícita |
| `validation.py` | Calibración, scoring y bootstrap pareado | Evidencia fuera de muestra |
| `experiment.py` | Ajuste sólo en entrenamiento y factorial 3×3×2 | 18 configuraciones con stages fijos |

## Contrato de integración

`pd_model.predict_curve(loans, macro)` devuelve **masas marginales**, no hazards ni probabilidades acumuladas. `lgd_model.predict(loans, macro, ead)` y `ead_model.predict(loans, macro)` devuelven matrices alineadas. La fila i corresponde a la posición i del DataFrame; no se unen componentes por un índice implícito diferente. `run_ecl` exige IDs únicos, escenarios nombrados sin duplicación, pesos válidos y horizonte suficiente para todas las vidas contractuales.

Los outputs son:

- `loans`: ECL ponderada y stage por ID, en el orden de entrada.
- `scenarios`: ECL por ID/escenario, peso, base de cálculo, ECL12 y lifetime (NaN deliberado para diagnósticos de default futuro en Stage 3).
- `monthly`: mes, masa marginal, LGD, EAD, contribución y selección de horizonte para activos vivos.
- `models`: IDs de PD, LGD y EAD. Los parámetros ajustados y hashes de código quedan en `results/multimodel` tras ejecutar la CLI.

No se descuenta el mismo intervalo dos veces: LGD incorpora tiempo entre default y recuperación; ECL incorpora tiempo entre reporte y default. La EAD no contiene supervivencia de default; ésta ya entra en la masa marginal. En el adaptador CPR sólo incorpora retención por prepago bajo independencia explícita.

## Staging y comparabilidad

`classify` recibe PD de origen y actual sobre la misma vida remanente comparable. El laboratorio **supone** esas entradas: no reconstruye una PD de origen desde un score actual. La evaluación SICR usa simultáneamente cambio relativo ≥2 y absoluto ≥2 puntos porcentuales; watchlist o DPD ≥30 son respaldo; deterioro informado o DPD ≥90 prevalecen. Son reglas de investigación configurables, no una determinación de política contable. PD origen cero y actual positiva se manejan mediante razón infinita más el umbral absoluto, sin epsilon arbitrario.

El factorial mantiene stages constantes para aislar componentes. El notebook integrado evalúa umbrales por separado. No hay curas, persistencia temporal ni reemplazo automático de la política por el mejor score.

## Ejecución y portabilidad

Desde esta carpeta:

```bash
python run_multimodel.py --config configs/reference.json --output results/multimodel
python -m unittest discover -s tests -v
```

Dependencias numéricas: las de `requirements-runtime.txt` en la raíz. Para notebooks instalar además `nbformat`, `nbclient`, `ipykernel` y `matplotlib`, o usar el conjunto de investigación del repositorio. Los notebooks resuelven la raíz desde su carpeta; no requieren rutas del entorno de desarrollo ni credenciales. No hay descargas en la corrida.

El horizonte de referencia es 36 meses. Los escenarios de muestra y parámetros de política están centralizados en `data.standard_scenarios` y `staging.classify`; la configuración JSON controla semilla y tamaños. No es un DSL de política: cambios de supuestos deben revisarse como código y regenerar evidencia.
