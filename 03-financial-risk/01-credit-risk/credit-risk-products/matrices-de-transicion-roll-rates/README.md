# Matrices de transición y roll rates

Estimación por máxima verosimilitud de una matriz de transición entre estados de mora (al día, 30, 60, 90+ días y default absorbente) y cálculo de la PD acumulada a 12 meses con potencias de la matriz. El laboratorio controlado ilustra la mecánica con historias simuladas; una aplicación complementaria usa saldos agregados observados de la SFC para mostrar cambios de composición de calificaciones, sin inferir migraciones de cuentas.

## Método y contrato

Para conteos de transición mensuales \(N_{ij}\), la estimación usada es \(\widehat P_{ij}=N_{ij}/\sum_jN_{ij}\). Si `al_dia` es el estado inicial y `default` el absorbente, la PD acumulada a \(h\) meses es \((\widehat P^h)_{al\_dia,default}\).

El grano requerido es **cuenta–mes de observación** con `account_id`, `observation_month`, `state_from` y `state_to`. El catálogo se cierra a `al_dia`, `mora_30`, `mora_60`, `mora_90` y `default`; en este laboratorio, default no cura. El [contrato común](../docs/DATA_CONTRACTS.md) y el [DDL SQL](../docs/credit_risk_schema.sql) hacen explícitas esas restricciones. En una cartera real, curas, castigos, prepagos, cierres y censura deben documentarse antes de estimar la matriz.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Referencia observada: cambio agregado de mezcla D+E

La [aplicación SFC de cambio de mezcla](observed-sfc-grade-mix-shift/results/report.md) compara, por producto, la participación de saldos calificados D+E con la del mismo mes un año antes. En agosto de 2026, 32 productos tenían comparación interanual; el mayor aumento fue **2,90 puntos porcentuales** en consumo de bajo monto (participación D+E de 4,88%; 8 entidades reportantes). Esta señal permite priorizar revisión sectorial y formular preguntas de monitoreo.

Los datos SFC son agregados por producto y corte; no enlazan cuentas entre meses. Por ello, el cambio de mezcla no es una transición de estado, tasa de default, roll rate ni PD, y no valida la matriz del laboratorio. La aplicación documenta linaje, cobertura y límites, conserva un snapshot agregado reproducible y genera tabla, resumen y figura desde `build_companion.py`.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
Matriz estimada (filas = estado actual):
         al_dia  mora_30  mora_60  mora_90  default
al_dia    0.940    0.050    0.000    0.000    0.010
mora_30   0.349    0.397    0.255    0.000    0.000
mora_60   0.145    0.104    0.350    0.402    0.000
mora_90   0.047    0.000    0.098    0.457    0.399
default   0.000    0.000    0.000    0.000    1.000
Error absoluto maximo vs matriz verdadera: 0.0068
PD acumulada a 12 meses (cuenta al dia): estimada 0.1653 | verdadera 0.1636
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
