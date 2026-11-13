# Weighted Tail Underflow Guard

## Iteración 2026-10-17: recepción acotada y coherencia del contrato

El mismo comando run.sh añade `src.packet.decode(payload: bytes)`. Ver
[informe-recepcion.md](informe-recepcion.md). La iteración anterior se conserva
debajo como contexto histórico; los crudos se regeneran al ejecutar el pipeline.

```python
from src.consumer import decide, encode
from src.packet import decode, PacketError
packet = decide([0.0, 5e-324], "0", alpha=.5, weights=[3.0, 1.0])
received = decode(encode(packet).encode("utf-8"))
assert received["breach"] is True  # no consumir sólo es_float=0
```

Recepción v1: máximo32768 bytes UTF-8; enteros racionales como strings canónicos
reducidos de hasta2048 caracteres (incluido signo); denominador positivo.
Se rechazan claves duplicadas/desconocidas, campos ausentes, tipos incorrectos,
NaN/Infinity/overflow, discrepancias racional-float/decisión/flag y estados de
rechazo tratados como decisión numérica. Un rechazo válido conserva breach=null.
JSON integers nativos no forman parte de este perfil v1 (es_float se emite como
token float). Los tokens float se limitan a128 caracteres y las razones a1024
caracteres ASCII imprimibles. Los límites son política explícita, no un estándar
universal ni garantía de tiempo real. Payloads demasiado grandes se rechazan
antes de decodificar; enteros string se acotan antes de convertirlos a int.

**Límite crucial:** esto valida consistencia interna, NO origen, autenticidad,
frescura ni ES verdadero. Una falsificación coherente puede pasar: se entrega
control negativo ejecutado. No hay servidor, firma ni verificación de escenarios.
El emisor previo sigue opt-in y sin límites nuevos; para entradas no confiables
hay que acotar también el ingreso de escenarios/umbrales, no sólo esta recepción.

Outputs nuevos: packet-accuracy.csv, packet-mutations.json, packet-performance.csv,
packet-summary.json y packet-negative-control.json. 390 paquetes válidos aceptados,
114 mutaciones incompatibles rechazadas; 68 tests totales; notebook de siete
celdas ejecutadas. La figura histórica compara ES, no detección de mutaciones.

## Iteración 2026-10-16: contrato de decisión y transporte

El mismo comando run.sh incluye ahora `src.consumer.decide` y
`src.consumer.encode`. Reutiliza el guard integrado en PR #39, sin cambiarlo.
Ver [informe del consumidor](informe-consumidor.md) para resultados actuales;
el informe de 2026-10-15 conserva el registro histórico de esa ejecución.

```python
from src.consumer import decide, encode
packet = decide([0.0, 5e-324], "0", alpha=.5, weights=[3.0, 1.0])
assert packet["es_float"] == 0 and packet["breach"] is True
payload = encode(packet)
```

Contrato v1: `breach` significa estrictamente ES > umbral. El umbral debe ser
string decimal/racional finito. Si hay racional retenido, se compara antes de
redondear; si no, `comparison_basis=binary64-output` declara que sólo se compara
el resultado float existente, no un ES matemáticamente certificado. Numerador y
denominador viajan como strings, nunca números JSON de precisión limitada.
Un rechazo por política/cap tiene `status=rejected`, `breach=null`, sin ES.
Datos inválidos provocan ValueError, no una decisión aceptada. `encode` rechaza
NaN/Infinity; es un serializador, NO un validador de paquetes arbitrarios.
No convierte en confiables payloads externos ni impide ignorar deliberadamente
el contrato. No hay API HTTP ni autenticación.

Nuevos outputs: consumer-accuracy.csv (388 decisiones), consumer-performance.csv
(112 mediciones), consumer-summary.json, consumer-examples.json. Notebook con
cinco celdas ejecutadas, incluidos ejemplo de decisión y tabla comparativa.
Pruebas actuales: 34, con tres propiedades generativas de 100 ejemplos cada una.
Cobertura desglosada en results/coverage.json y tests.txt; las métricas históricas
inferiores corresponden al núcleo original.

MVP del 2026-10-15: entrada Python protegida frente a underflow de NumPy, con rechazo explícito o fallback racional. Continúa los PR #32 y #35, ya integrados. No modifica el baseline: su comportamiento y sus límites permanecen auditables.

## Instalación y reproducción: un comando

Desde la raíz del **repo completo**, con Python 3.12 y venv:

```bash
bash 03-financial-risk/02-market-and-model-risk/weighted-tail-underflow-guard/run.sh
```

Instala el entorno local fijado en requirements.lock.txt, ejecuta Ruff, mypy (src y benchmarks), pytest con cobertura de src.guard, 388 casos numéricos, benchmark y notebook con salidas reales. Requiere internet para la instalación inicial; experimentos sin red ni datos privados. Verificado en Linux x86-64, Python 3.12.14, NumPy 2.1.3. No se promete reproducción bit a bit de tiempos ni de aritmética en plataformas no verificadas.

## API y contrato

```python
from src.guard import guarded_tail
r = guarded_tail([1e308, 0.0], weights=[1e-300, 1e300])
print(r.es, r.backend, r.fallback_reason)  # ~4e-291, fraction, underflow...
```

- Pérdidas finitas, positivas/negativas; pesos no negativos y normalizados internamente; inputs interpretados como binary64, no decimales ideales.
- El camino habitual ejecuta el motor real del PR #32 dentro de `np.errstate(under='raise')`, restaurando el estado previo al salir.
- `policy='exact'` (default): recalcula desde **los inputs originales**, nunca desde pesos ya dañados, con Fraction y masa de cola fraccionaria.
- `policy='raise'`: lanza TailUnderflowError. También se rechaza un fallback que exceda max_exact_scenarios=4096 filas de entrada. El presupuesto limita sorpresas de costo, no es un umbral estadístico.
- El resultado informa backend, motivo, exact_es (solo fallback), output_rounds_to_zero. Si este último flag es True, **no debe consumirse solo r.es**: el racional no nulo no cabe en float; hay que usar la fracción, cambiar escala/unidad o rechazar el resultado.
- El guard captura eventos de underflow de NumPy; **no es un detector universal de todo error de redondeo**. El camino float64 conserva las limitaciones de precisión del baseline.

## Verificación y outputs

- src/guard.py: cálculo exacto, guard y políticas; src/sources.py: comparadores reales, sin demos.
- tests/: analíticos, inputs inválidos, presupuesto, restauración de errstate y dos propiedades generativas de 100 ejemplos cada una.
- benchmarks/config.json: seed, exponentes, tamaños y repeticiones fijados.
- results/accuracy.csv y fixtures.json: referencia hinge racional independiente importada del aporte C++, numeradores/denominadores, motivos y flags.
- results/performance.csv: tiempo separado de tracemalloc, orden de métodos aleatorizado por réplica con seed; pico de asignaciones Python/NumPy, **no RSS ni memoria nativa completa**. Se conserva la medición piloto con orden fijo en initial-fixed-order-performance.csv.
- results/comparison.svg: pérdidas a cero y costo del fallback; notebook.ipynb: tres celdas ejecutadas con IPython en proceso, capturando stdout/display_data reales sin sockets.
- results/tests.txt, coverage.json, lint.txt y types.txt: evidencia de ejecución. La cobertura declarada es del guard, no todo el pipeline.
- informe.md, referencias.bib y MVP.md: método, resultados, límites y ocho referencias primarias.

Comandos individuales después de instalar: `.venv/bin/python -m pytest -q`, `.venv/bin/python -m benchmarks.run`, `.venv/bin/python benchmarks/notebook.py`.

## Equidad y alcance

Se ejecuta el baseline real, no uno artificialmente debilitado. La referencia minimiza la función hinge de CVaR en aritmética racional; el fallback integra átomos ordenados en racionales: implementaciones distintas. La comparación incluye always_exact como ablación: el fallback puede ser mucho más lento que el baseline, que en los casos extremos devuelve un valor incorrecto.

Los casos adversariales no estiman la frecuencia de fallos en mercados reales. No hay pronóstico, calibración de pesos, IFRS 9/SFC/FRTB ni prueba de superioridad económica. No se modifica C++, por lo que no se ejecutan nuevos sanitizers C++ en este ciclo. No se altera la semántica de los aportes anteriores ni se garantiza soporte de sus futuros cambios sin revisar esta auditoría.
