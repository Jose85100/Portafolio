# MVP 2026-10-16: decisión de ES sin perder el racional en el consumidor

## 1. Pregunta e hipótesis

¿Preservar el racional retenido por el guard evita decisiones erróneas de signo
que aparecen al consumir únicamente su float? Hipótesis falsable: en las 388
fixtures ya fijadas, la decisión estricta ES > 0 del contrato coincidirá con el
oráculo racional independiente y sobrevivirá un roundtrip JSON sin cambios;
los rechazos por política/presupuesto no tendrán decisión numérica.

## 2. Estado actual, prior art y brecha

Se revisó main a8199a6864c63d25bd322537f60cc184e8c43bc7, incluida arquitectura
03-financial-risk y risk-engines y los aportes #32/#35/#39. El último ya está
integrado. No se duplica motor ni fórmula: se extiende su proyecto con un
consumidor. El guard conserva Fraction pero `.es` puede ser cero: su uso aislado
ignora evidencia disponible. La nueva API hace la comparación antes de descartar
la fracción y transporta su numerador/denominador como strings.

Acerbi–Tasche fundamenta ES discreto; Python documenta Fraction(float) frente a
Fraction(string), y json allow_nan=False. NIST respalda separar precisión de
reproducibilidad; BCBS239 aporta contexto de integridad de datos, no aprobación
regulatoria. Búsqueda primaria y parcial en benchmarks/prior-art.md; diez entradas
BibTeX con DOI/arXiv/URL. Ni el cálculo racional ni el JSON son nuevos: la novedad
incremental es un contrato de integración y su benchmark contra el consumidor
ingenuo del motor real. No se afirma prioridad ni búsqueda exhaustiva.

## 3. Diseño y configuración

- Inputs: results/fixtures.json, 388 casos sintéticos heredados de la auditoría.
- Distribución empírica finita, pérdidas firmadas, pesos conocidos no negativos,
  positivos en total; alpha propio de cada fixture. Sin régimen ni activo real.
- Los floats de entrada son los valores binarios exactos; no decimales ideales.
- Umbral principal: string "0". Métrica: desacuerdo de decisión contra el signo
  del ES racional del oráculo hinge independiente del algoritmo de cola ordenada.
- Baseline nuevo: `guarded_tail(...).es > 0`, NO el baseline sin guard del día 15.
  Es una ablación realista de consumir sólo el float disponible.
- Tratamiento: `decide` usa el racional retenido cuando existe; si no, compara
  Fraction(es_float) y declara `comparison_basis=binary64-output`.
- Comparación estricta >; igualdad no dispara. Umbral string racional/decimal
  exacto, nunca convertido a float. Ejemplo probado: float(0.1) > decimal 0.1.
- Dos políticas de rechazo: policy=raise y max_exact_scenarios=1 en caso de dos
  filas con underflow. Deben dar breach=null, no False ni ES=0.
- Rendimiento: n=2,32,256,2048; 7 réplicas; seed20261016; orden aleatorio por
  réplica; warmup excluido. Ordinario: pérdidas/pesos unitarios; estrés: un
  subnormal positivo y resto ceros, con pesos 1 y 3; alpha=.5.
- 112 mediciones nuevas. Tiempo sin tracemalloc; memoria en llamada separada.
  Pico de asignación Python/NumPy, no RSS ni toda memoria nativa.
- Python3.12.14, NumPy2.1.3; Linux x86_64/glibc2.39; AMD EPYC9V74. Versiones
  fijadas heredadas; hashes de código/inputs y CPU en consumer-summary.json.

## 4. Implementación y ejecución

src/consumer.py expone decide/encode. Paquete versionado weighted-es-decision/v1,
estado accepted/rejected, decisión bool/null, base de comparación, razón de
fallback y racional en strings. Un rechazo omite ES; datos inválidos siguen
siendo ValueError. encode es serializador estricto, NO validador de paquetes.
No se cambia src.guard ni el baseline histórico. Sin nuevo C++/sanitizers.

Comando único desde raíz (instala y ejecuta todo):

```bash
bash 03-financial-risk/02-market-and-model-risk/weighted-tail-underflow-guard/run.sh
```

Pipeline completo ejecutado con éxito: Ruff, formato, mypy, pytest, auditoría
previa, benchmark consumidor, notebook. Instalación inicial requiere internet;
Python3.12/venv y lock heredados, no imagen binaria hermética ni hashes de ruedas.

## 5. Resultados reales

| Medida | Consumidor float del guard | Contrato |
|---|---:|---:|
| Decisiones erróneas ES > 0 / 388 casos | 29 | 0 |
| Roundtrips JSON iguales | no aplica | 388 |
| Políticas de rechazo sin decisión | no aplica | 2/2 |

Las 29 pérdidas son las salidas finales no representables en float, NO las 78
contribuciones representables que el guard ya rescataba. No se confunden ambos
experimentos ni se reclama mejorar nuevamente aquel baseline.

Ejemplo ejecutado: pérdidas [0,5e-324], pesos [3,1], alpha=.5. ES racional
positivo, float=0; consumidor ingenuo False, contrato True. El racional permanece
reconstruible después del JSON. El caso negativo no se convierte en alerta.

Medianas locales, n=2048, ms:

| Régimen | Float del guard | Contrato + JSON |
|---|---:|---:|
| Ordinario | 0.359030 | 0.402845 |
| Subnormal | 9.111846 | 9.289469 |

Pico de asignación observado en n2048: ordinario231310/231682 bytes;
subnormal404700/404448 bytes, respectivamente. Las diferencias pequeñas no
demuestran ventaja de memoria ni velocidad. El contrato hace más trabajo
(comparación exacta disponible y serialización) y no se presenta como optimización.
En n256 subnormal fue algo más rápido en esta muestra; se conserva como ruido
posible y no se usa para reclamar aceleración. Todos los crudos se entregan.

La figura results/comparison.svg corresponde al motor original reejecutado, no
al nuevo efecto de decisión. El notebook añade una tabla HTML específica del
consumidor; no se disfraza una figura heredada como evidencia nueva.

## 6. Tests, cobertura y notebook

34 tests pasan: 21 heredados y 13 del consumidor. Tres propiedades Hypothesis
con 100 ejemplos deterministas cada una en el conjunto. Casos nuevos: JSON,
rechazos, inputs/umbrales inválidos, NaN, igualdad estricta, decimal contra float,
comparaciones racionales próximas al umbral, valores negativos.

Cobertura consumer.py: 21/21 sentencias y 2/2 ramas (100%). Con guard.py:
86/86 sentencias, 22/24 ramas; combinado98.18%. Dos ramas defensivas del guard
siguen sin cubrirse; no se afirma cobertura del pipeline ni de todos los riesgos.

Notebook ejecutado de arriba abajo mediante IPython in-process, cinco celdas
con stdout/display_data capturados; formato nbformat validado. Se inspeccionaron
los outputs guardados y la tabla HTML 29/0. No se realizó inspección visual en
un visor gráfico del notebook: esa revisión de presentación queda pendiente,
sin afectar los tests y aserciones ejecutados. Guía jupyter-notebooks aplicada;
sus referencias compartidas no estuvieron accesibles.

## 7. Análisis crítico, fallos y límites

1. Fallo reproducido: consumir sólo `.es` puede borrar el signo; la fracción
   existente permite resolverlo sin cambiar el motor.
2. Resultado negativo: transportar un contrato cuesta CPU y bytes; no se mide
   red ni servidores, ni se promete que un tercero respete el contrato.
3. Exactitud sólo sobre los valores binarios originales del fallback. La ruta
   rápida conserva redondeo y puede errar junto a otros umbrales; se declara su
   base. El umbral cero del benchmark no certifica decisiones universales.
4. Rechazo no significa riesgo cero. Un usuario que convierta null a False
   reintroduce el problema: el contrato ayuda, no impone políticas externas.
5. No hay esquema JSON entrante validado, autenticación, límites de payload,
   resistencia DoS ni consumidor JavaScript ejecutado. Strings evitan coerción
   numérica por formato; no prueban interoperabilidad integral entre lenguajes.
6. Umbrales string no confiables muy grandes requieren límites a nivel servicio;
   el límite4096 del guard no es presupuesto universal de aritmética racional.
7. Las 388 fixtures son adversariales y reutilizadas: 29/388 no es prevalencia
   de mercado, significancia estadística ni riesgo financiero material.
8. No hay VaR/ES predictivo, backtesting Kupiec/Christoffersen/AS, ni afirmación
   IFRS9/SFC/FRTB. Comparar decisiones aritméticas no mejora pronósticos.
9. No se ocultan la falta de validación visual y las ramas no cubiertas.
10. Resultados previos se regeneraron por el comando completo; los informes
    fechados anteriores conservan su registro histórico, no tiempos universales.

## 8. Cierre

Checklist: src real, comando único, tests aprobados, baseline29vs0, CSV/JSON,
notebook ejecutado, README/MVP/informes/BibTeX y ubicación03-financial-risk:
completo. La publicación y CI remota se informan en el PR, no se presuponen aquí.

Rúbrica1–5: novedad3; rigor4; reproducibilidad5; código4; claridad4; impacto3;
honestidad5; MVP ejecutable5. Autoevaluación, no certificación externa.

Siguiente iteración recomendada: ampliar la seguridad del contrato fuera del proceso.
1. 03-financial-risk: esquema entrante, límites de payload/umbrales y pruebas de
   rechazo de paquetes manipulados, sin convertir null en False.
2. 04-quant-strategy-and-products/risk-engines: consumidor C++ con roundtrip de
   racionales y fixtures comunes, sanitizers y paridad por plataforma.
3. 03-financial-risk: política de error cerca de umbrales no nulos, separada de
   backtesting estadístico fuera de muestra.
