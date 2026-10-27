# Funding Lead-Time Gate

Elegir cuándo solicitar un giro de una línea comprometida cuando el desembolso demora. La regla usa caja observada, no conoce el flujo futuro del período. El monto recibido se registra como caja **y deuda**, nunca como ingreso.

Componente S2 sintético dentro del programa18 (que conserva su alcance de diseño). No es un sistema operacional ni una recomendación de fondeo real.

## Reproducir

Python3.12, desde esta carpeta:

```bash
bash run.sh
```

Instala versiones directas fijadas en `.venv`, ejecuta6tests/cobertura, ruff, mypy, benchmark y notebook. Entorno existente: `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`. Ejecución local usó venv con paquetes científicos preexistentes y herramientas fijadas; segundo contenedor limpio no probado. Dependencias transitivas sinhash. NoAPI ni datos privados.

## Decisión sintética

| Política | Masa de escenarios con brecha | Costo esperado |
|---|---:|---:|
| No solicitar |0,50|0|
| Reactiva: caja≤2 |0,50|0,132|
| Caja≤4 |0,30|0,362|
| Seleccionada: caja≤6 |0|0,740|
| Caja≤8 |0|0,980|

Se compra anticipación por costo adicional0,608 frente al baseline reactivo. La masa0es dentro de3escenarios diseñados, no probabilidad real ni garantía. Con demora4, ningún umbral del menú es factible; bajo burn externo−4por período, la política elegida también falla.

`config.json` define caja inicial8, giro8, comisión0,5, interés2%por período sintético y demora2. La línea es cierta y comprometida; no tiene revocación ni amortización dentro del horizonte. La regla queda fijada exante en menú finito y minimiza costo sujeto a brecha≤10% de masa de escenarios.

## Contabilidad parcial y orden de eventos

Cada período: llega fondeo pendiente; se observa caja; si cumple umbral se solicita y paga comisión; se verifica piso; al cierre se aplica flujo operativo neto e interés y se verifica piso otra vez. Para demora0, comisión y fondeo son una misma transacción. La identidad de liquidez es caja−deuda=caja inicial+flujos netos−costos; no es un estado financiero completo. Interés solo sobre principal desembolsado. No solicitud que llegue fuera del horizonte.

El simulador continúa aritméticamente después de una brecha **solo para diagnóstico**. No significa que la empresa pueda operar insolvente. Una brecha en apertura inicial se registra como período−1.

## Artefactos y límites

`src/`, tests (oracle cerrado y no anticipación), CSVtrayectorias/umbrales/demoras, JSON/PNG, notebook ejecutado,5referencias y `informe.md`14puntos. Datos deterministas por escenario, sin estimación de probabilidades; no hay validación causal ni regulatoria. No costos de compromiso, vencimiento, repago, activos, covenant, colateral, decisiones de dividendos o garantía de acceso a crédito.

Notebook ejecutado realmente en IPython en proceso, namespace fresco y outputs rich capturados; noQA de kernelJupyter. Figura inspeccionada; interfaznotebook completa no inspeccionada.
