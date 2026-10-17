# MVP 2026-10-17: receptor acotado del contrato de decisión de ES

## 1. Pregunta e hipótesis falsable

¿Puede un receptor rechazar paquetes ES internamente inconsistentes sin rechazar
las salidas válidas del consumidor del repo? Criterio fijado: aceptar390 paquetes
válidos y rechazar todas las114 mutaciones definidas, con cero discrepancias
contra las etiquetas del corpus. No se plantea eficacia ante ataques reales ni
seguridad universal; un control negativo debe demostrar el límite de autenticidad.

## 2. Revisión del repo, brecha y prior art

Base main cd464aa9bd842b9307206020def4371d3197471f, PR42 integrado. Se revisaron
la arquitectura03-financial-risk/04-risk-engines, el guard, el consumidor y sus
benchmarks previos. La brecha no es otra fórmula: encode produce JSON pero no
valida paquetes entrantes. El parser estándar tampoco verifica que la decisión
concuerde con la fracción o que rechazo implique breach=null.

RFC8259 y Python documentan interoperabilidad y comportamiento de JSON;
Fraction permite comparar los racionales sin tolerancias que oculten subnormales.
ES discreto se apoya en Acerbi–Tasche; BIS/ECB son contexto de integridad de datos,
no certificación. NIST distingue reproducibilidad numérica. Búsqueda parcial en
benchmarks/prior-art.md, once referencias BibTeX verificables. No se afirma
prioridad científica ni que no existan validadores similares. La novedad local
es integración de invariantes ES, recepción acotada y benchmark de mutaciones.

## 3. Diseño experimental

Distribuciones empíricas sintéticas, pesos conocidos no negativos y pérdidas
firmadas interpretadas como binary64; no hay mercado real, activo ni régimen
estimado. Se reutilizan las388 fixtures y sus salidas de decide con umbral0,
más dos rechazos legítimos por política/presupuesto:390 paquetes válidos.

Se seleccionan con seed20261017 seis casos float64 y seis fraction, IDs guardados
en packet-summary.json. Nueve mutaciones por seleccionado: decisión, flag,
float, backend, versión, tipo de decisión, campo extra, denominador0 y clave
duplicada. Dos rechazos×tres mutaciones añaden seis: total114. Todas son JSON
sintácticamente admisible para el parser Python; son incompatibles con este
contrato. Corpus crudo completo en packet-mutations.json; etiquetas construidas
por reglas conocidas, no aprendizaje ni dataset representativo de atacantes.

Baseline: json.loads real, sin debilitarlo. Su función es parsear, no detectar
incoherencias de riesgo: no se presenta su aceptación como bug de Python.
Tratamiento: src.packet.decode, parser más perfil estricto e invariantes.
Control negativo separado: alterar coherentemente ES/racional/decisión. Ambos
receptores deben aceptarlo: no hay datos ni firma que prueben la falsificación.

Escalabilidad: umbrales con1/32/512/2000 dígitos; payloads311..2310 bytes;
siete réplicas por método/tamaño, orden aleatorio, warmup excluido.56 filas.
Tiempo separado de memoria tracemalloc (no RSS ni toda asignación nativa).
Python3.12.14, NumPy2.1.3, Linux6.18.55 x86_64/glibc2.39, AMD EPYC9V74;
dependencias/versiones/plataforma en resultados heredados y hashes del nuevo
código/inputs en packet-summary.json. No comparación entre máquinas.

## 4. Implementación

decode recibe bytes, verifica máximo32768 antes de decodificar UTF-8, rechaza
claves duplicadas mediante hook, constantes no finitas, números nativos enteros
ajenos al perfil, tokens float>128 caracteres y overflow. Exige campos exactos
según estado. Fracciones: enteros string ASCII canónicos de máximo2048 caracteres
incluido signo, denominador positivo y representación reducida, antes de int.

Comprueba float(fracción)==es_float, decisión estricta, flag de no
representabilidad y coherencia de backend/base/razón. Para binary64-output,
el racional debe ser exactamente Fraction(es_float); no certifica el ES real.
Un rechazo válido conserva breach=None y no tiene campos de ES. Razones limitadas
a1024 caracteres ASCII imprimibles. Errores devuelven PacketError, nunca riesgo0.
No se cambia src.guard ni src.consumer; receptor opt-in, sin servicioHTTP.

Comando único desde raíz con Python3.12/venv:

```bash
bash 03-financial-risk/02-market-and-model-risk/weighted-tail-underflow-guard/run.sh
```

Instala lock heredado y ejecuta Ruff/formato/mypy, pytest, todos los benchmarks
y notebook. Internet para instalación inicial; no imagen hermética/hashes de
ruedas. CI dedicada existente cubre el mismo comando. No nuevo C++/sanitizers.

## 5. Resultados ejecutados

| Población | json.loads acepta | Receptor acepta |
|---|---:|---:|
|390 paquetes válidos |390 |390 |
|114 mutaciones incompatibles |114 |0 |
|1 falsificación coherente, control negativo |1 |1 |

Cero rechazos de válidos y cero aceptaciones de mutaciones en ESTE corpus.
La falsificación aceptada se conserva en packet-negative-control.json, sin
ocultarla ni incluirla entre paquetes que se afirme poder rechazar.

Medianas de tiempo locales (ms):

| Dígitos umbral / bytes | Parser | Receptor |
|---|---:|---:|
|1 /311 |0.004717 |0.011948 |
|32 /342 |0.005058 |0.013450 |
|512 /822 |0.005608 |0.019048 |
|2000 /2310 |0.007351 |0.080749 |

Picos tracemalloc:311 bytes de payload, parser2879/receptor3511 bytes;
2310 bytes de payload, parser6919/receptor7478 bytes. Ver crudo completo.
El receptor hace más trabajo y es más lento: no se reclama una optimización.
No se infiere significancia de siete muestras ni una cota temporal garantizada.

La figura comparison.svg pertenece al motor ES reejecutado, NO a esta comparación.
Aquí una tabla de conteos es más precisa que representar detección como curva
estadística sin población probabilística. El notebook conserva la figura previa
y añade dos celdas ejecutadas con el ejemplo y los conteos de recepción.

## 6. Pruebas, cobertura y notebook

68 tests pasan:34 anteriores+34 nuevos. Cinco propiedades Hypothesis×100
ejemplos deterministas entre todos los módulos; dos nuevas: roundtrip singleton
y rechazo al invertir la decisión. Casos límite: UTF-8 inválido, JSON malformado,
duplicados, tamaño, anidación excesiva, NaN/Infinity/overflow, token largo,
fracciones inválidas/no reducidas, estado incoherente y falsificación coherente.

packet.py:85/85 sentencias y48/48 ramas,100%. Tres módulos medidos:171/171
sentencias,70/72 ramas; combinado99.18%. Dos ramas defensivas del guard no
cubiertas. Cobertura no prueba ausencia de vulnerabilidades ni todas las
combinaciones de condiciones. Ruff, formato y mypy pasan.

Notebook: siete celdas realmente ejecutadas top-to-bottom con IPython in-process,
outputs stream/display_data conservados, nbformat validado; nuevos outputs
inspeccionados (390/114/114/0/0 y control negativo). Guía jupyter-notebooks
aplicada; referencias compartidas inaccesibles. No revisión gráfica en visor:
esa comprobación de presentación queda pendiente y no se simula.

## 7. Análisis crítico y límites

1. Valida coherencia interna, NO verdad del ES: falta recomputación contra inputs.
2. Sin autenticación, firmas, identidad de modelo, timestamp, prevención replay
   ni política de vigencia. Un emisor coherentemente falso pasa (control real).
3. Receptor opt-in; no impide consumir json.loads directamente ni ignorar un
   estado rejected. Null no se debe convertir a False en sistemas downstream.
4. Los límites acotan entrada pero no certifican DoS resistance ni tiempo real.
   JSON se parsea antes de validar forma; RecursionError se rechaza, no hay parser
   streaming ni carga de concurrencia. Payload ya está en memoria al llamar.
5. Es perfil v1 más estricto que JSON general: enteros nativos, campos extra,
   fracciones no reducidas y razones Unicode se rechazan por política, no porque
   JSON/RFC los prohíba. Puede rechazar futuros emisores legítimos no compatibles.
6. Limita RECEPCIÓN, no inputs de decide: un umbral upstream no confiable o una
   población grande aún requiere presupuestos de ingreso antes de calcular ES.
7. El racional de fastpath certifica el float recibido, no un ES matemáticamente
   exacto. Conversión ya redondeada de un token decimal no se puede reconstruir.
8. Datos sintéticos y mutaciones dirigidas:114/114 no es tasa de detección fuera
   de muestra, ni eficacia contra atacantes adaptativos. Sin tests red/crosslang.
9. No hay predicción/backtesting VaR/ES, SFC/IFRS9/FRTB ni mejora financiera.
10. Pipeline regenera tiempos previos; informes fechados conservan registros
    históricos. Coste/memoria y falsificación aceptada se reportan sin seleccionar
    sólo resultados favorables. No se publican resultados de CI no observados.

## 8. Cierre y rúbrica

Checklist MVP completo: src ejecutable, comando único, tests pasan, baseline
numérico, salida CSV/JSON/notebook, README/MVP/informes/BibTeX y carpeta03-risk.
Publicación y estado CI se verifican en el PR. Once referencias en referencias.bib.

Autoevaluación1–5: novedad3; rigor4; reproducibilidad5; código4; claridad4;
impacto3; honestidad5; MVP completo/ejecutable5. No es revisión externa.

Siguiente iteración recomendada: vincular el paquete a escenarios verificables.
1. 03-financial-risk: manifiesto de inputs/modelo/versión y recomputación auditada
   para detectar falsificaciones coherentes, sin confundir hash con autenticidad.
2. 04-quant-strategy-and-products/risk-engines: receptor C++ del perfil v1 con
   corpus compartido, límites y sanitizers.
3. 03-financial-risk: presupuestos de ingreso de escenarios/umbrales y pruebas de
   concurrencia, conservando rechazo como estado distinto de riesgo0.
