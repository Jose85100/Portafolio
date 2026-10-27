# Primera ruptura de liquidez y persistencia de flujos

Un saldo final positivo puede ocultar un déficit previo. Este MVP calcula la distribución de primera ruptura de caja con un régimen Markov y compara secuencias persistentes con flujos IID que tienen **los mismos marginales diarios**. El motor C++ existente ya identifica rupturas por trayectoria; aquí se añade un oráculo probabilístico y sensibilidad de reserva, sin modificarlo.

## Reproducir — Python3.12
```bash
bash run.sh
```
Crea .venv, instala versiones directas fijadas, ejecuta tests propios y del laboratorio vecino, cobertura, Ruff, mypy estricto del núcleo, benchmark y notebook. Entorno listo: `SKIP_INSTALL=1 bash run.sh`; PYTHON permite seleccionar otro intérprete. Se recomienda checkout completo por la prueba de integración `../tests`. Dependencias transitivas no totalmente bloqueadas.

## Resultados sintéticos
Reserva6, horizonte20, flujos +1/−2 y probabilidad estacionaria de estrés20% en ambos modelos:

| Modelo | Primera ruptura | Caja final negativa | Reserva mínima para objetivo5% |
|---|---:|---:|---:|
| IID |2,927%|0,998%|5|
| Persistente |25,723%|15,793%|22|

Misma entrada neta esperada diaria +0,4; cambian las secuencias. La probabilidad de haber roto y terminar recuperado es9,930pp en el caso persistente. El criterio de ruptura es caja<0: caja0 sobrevive. Reserva mínima es decisión del modelo y objetivo sintético, NO requerimiento regulatorio ni recomendación bancaria real.

Núcleo stdlib, oráculo exhaustivo de64trayectorias con error observado0, seis tests,60ensayosMC,82registros de reserva y distribución de primera ruptura. Incluye casos negativos: horizonte1 sin diferencia y reserva0 donde persistente reduce riesgo44,315% frente a48,880% IID, figura inspeccionada, notebook real ejecutado con IPython secuencial, cinco fuentes primarias verificadas e informe14p. No se afirma renderHTML completo.

Madurez: componente prototipo sintético verificable; revisión independiente aparte. No se estima matriz de transición, acceso a fondeo, impacto de mercado o reacción endógena de clientes.
