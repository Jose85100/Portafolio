# Incentive Alignment Gate

Auditar si un bono induce la acción que el consejo pretende. El motor13 previo calcula bonus/malus y reparte pago inmediato/diferido, pero no modela la respuesta del ejecutivo; este componente añade esa comprobación con acciones finitas, compatibilidad de incentivos y participación.

Componente S2 sintético; no se recertifica el programa13 ni se presenta como contrato operativo o asesoría laboral/regulatoria.

## Reproducir

Python3.12, desde esta carpeta:

```bash
bash run.sh
```

Crea `.venv`, instala versiones directas fijadas y ejecuta5tests/cobertura, ruff, mypy, benchmark y notebook. Con entorno existente: `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`. Se ejecutó en venv con paquetes científicos disponibles y herramientas fijadas; no se probó segundo contenedor limpio. Transitivas sin hashes. SinAPI ni información privada.

## Decisión sintética

Bono base B=10%del volumen. Una fracción f se difiere y **solo se paga en éxito**; no es mero cambio de fecha. Éxito pagaB y fracaso(1−f)B≥0. Agente neutral al riesgo maximiza bono esperado menos esfuerzo.

| Contrato / decisión | Respuesta | Beneficio neto esperado firma |
|---|---|---:|
| Bono inmediato por volumen |volume_chasing|−22,50|
| No ofrecer este proyecto/contrato |Fuera|0|
| Menor f factible del menú:0,9 |prudent|8,95|

El benchmark fuerte de abstenerse vale0: incremento8,95, no31,45. La diferencia31,45frente a un contrato heredado malo no es evidencia empírica ni rentabilidad real. Objetivo del diseñador: menor diferimiento del menú que cumple margenIC≥0,05, participación, respuesta objetivo y valor neto no negativo; **no** máxima ganancia entre todos contratos.

Con f0,9: utilidad objetivo8,55 vs alternativa8,25, margen0,30. Mínimo continuo para margen0,05:6,05/7≈0,864286;0,9solo es mínimo del menú. Tope0,8hace inviable el objetivo. Añadir una acción omitida rompe alineación y produce−30,73: la seguridad depende del conjunto modelado.

## Artefactos y límites

`config.json` fija2acciones y6contratos sintéticos. `src/incentives.py` es stdlib tipado; tests incluyen oracle analítico, transferencias, responsabilidad limitada, desempates adversos, participación y acción omitida. CSVcontratos/sensibilidad/escalabilidad, JSON, figura y notebook ejecutado.5referencias DOI/URL e informe14puntos.

Sin descuento ni aversión al riesgo, sin salarios fijos, impuestos, garantías legales, manipulación del resultado, renegociación o acciones desconocidas. Probabilidades dadas, no estimadas. La firma puede abstenerse del proyecto, no se afirma que cierre su operación completa. No son recomendaciones reales de remuneración.

Notebook ejecutado realmente en IPython en proceso, namespace fresco y captura rich; noQA de kernelJupyter. PNG inspeccionado; interfaz notebook completa no inspeccionada.
