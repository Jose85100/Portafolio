# Stage3 cash-shortfall audit — 2026-10-18

MVP ejecutado que profundiza el laboratorio IFRS9: distingue default ya ocurrido
de default futuro y separa el descuento incorporado en LGD. No sustituye política
contable, estimación de recuperaciones ni el motor padre, que queda intacto.

## Un comando desde la raíz del repositorio

```bash
bash 03-financial-risk/01-credit-risk/credit-risk-products/ifrs9-investigacion-cuantitativa/stage3-cash-shortfall-audit/run.sh
```

Requiere clon completo, Linux/Python3.12 con venv y acceso al índice de paquetes
para la instalación inicial. Crea .venv e instala requirements.lock.txt (50
versiones fijadas), luego lint/formato/mypy, tests/cobertura, benchmark y notebook.
No hashes de wheels ni imagen de sistema: no se reclama hermeticidad binaria.
No hay datos privados, credenciales, servicios externos ni nuevos binarios C++.

## Pregunta y contrato

Para un activo no POCI ya credit-impaired, con gross carrying amount G al cierre,
recuperaciones netas esperadas C y EIR original r suministrada:

\[
 L=G-\sum_t C_t(1+r)^{-t}
  =(G-\sum_t C_t)+\sum_t C_t[-\operatorname{expm1}(-t\log(1+r))].
\]

La segunda forma conserva la pérdida por demora con r diminuto. No se aplica
otra PD de nuevo default ni otro descuento a LGD ya expresada en valor presente.
La forma EAD×LGD sigue siendo válida si LGD es condicional al estado actual y
coherente con el mismo cierre y descuento; no se refuta esa identidad.

`src.model.shortfall(gross, recoveries, years, eir)` recibe n saldos, matriz
n×periodos y tiempos compartidos desde cierre. Retorna vector ECL, sin staging.
`scenario_shortfall` pondera escenarios×n×periodos con pesos explícitos.
Ámbito restringido: EIR no negativa, recuperaciones netas no negativas y su total
nominal no mayor que G. No inventa PD/recuperaciones a partir de DPD.

## Evidencia

- Motor padre importado y ejecutado realmente, sin reescribirlo: src/baseline.py.
- 432 casos fijados; 372 con referencia positiva; baseline inferior en esos372.
  Los60 casos de referencia0 se conservan. No es tasa de error de una cartera.
- Error relativo máximo frente a Decimal70dígitos:1.32308e-16.
- Caso G100, recuperar60 en2años, EIR10%, PD12m5%, horizonte futuro5años:
  baseline10.21192; certeza con descuento adicional45.83020; cash shortfall50.41322.
- 21 tests, dos propiedades×100 ejemplos. Cobertura src.model100% sentencias
  y ramas; no cobertura de todo el pipeline ni del motor padre.
- 56 filas crudas de tiempo/asignación; tiempos no comparan trabajo idéntico.

## Entregables

src modular; tests; benchmarks/run.py; results/config.json, accuracy.csv,
performance.csv, summary.json, example.json y comparison.svg/png; notebook.ipynb
con tres celdas realmente ejecutadas; informe.md; referencias.bib; MVP.md;
requirements.txt/lock; workflow dedicado. La figura PNG fue inspeccionada.

## Límites de uso

Sólo auditoría matemática/sintética de un caso no POCI ya deteriorado. Sin
clasificación real, cura, write-off, intereses devengados, recuperaciones que
superen nominal, EIR negativa, costos separados, EAD revolving, LGD estimada,
SFC, contabilización gasto/reintegro ni cumplimientoIFRS9 certificado. No todos
los Stage3 se reducen a esta parametrización. El motor padre permanece ilustrativo:
esta auditoría NO migra automáticamente sus resultados. Ver informe crítico.

La copia oficial histórica2016 de B5.5.33 y decisiónIFRIC2019 fundamentan la
identidad; no equivalen a una revisión exhaustiva de la norma vigente en2026.
La edición completa de IFRS Foundation requirió suscripción; se declara la
limitación en benchmarks/prior-art.md, sin eludir acceso.
