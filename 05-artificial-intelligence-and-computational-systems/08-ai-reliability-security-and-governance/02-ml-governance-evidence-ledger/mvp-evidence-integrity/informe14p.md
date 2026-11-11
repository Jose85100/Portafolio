# Informe de investigación — Integridad de evidencia de modelos

**Ciclo:** 2026-11-10 · **Área:** AI Reliability, Security & Governance · **Clasificación:** integración de ingeniería y auditoría adversarial, sin reivindicar novedad científica. **Madurez:** prototipo M2 bajo simulación sintética; no validado ni operacional.

## Página 1 — Resumen ejecutivo

El ledger de evidencia ML del programa describía manifiestos SHA-256, grafos de procedencia y versionado como elementos de diseño, pero carecía de verificador ejecutable. Este ciclo abordó una brecha acotada: verificar un paquete local exportado antes de consumirlo. La implementación valida la estructura del manifiesto, existencia y hash de cada archivo, IDs únicos, tipos requeridos, rutas confinadas y dependencias existentes sin ciclos.

La hipótesis fijada antes de interpretar resultados: 40/40 bundles limpios deben aceptarse y 40/40 mutaciones posteriores a fijar el manifiesto deben rechazarse en cuatro modos (edición de bytes, archivo ausente, referencia huérfana y ciclo). Se compararon tres alternativas: un baseline que valida sólo manifiesto/tipos, una ablación que valida hashes, y el verificador completo.

El método completo aceptó 40/40 controles limpios y rechazó 160/160 corrupciones ex post. El baseline aceptó todas las corrupciones; hash-only detectó cambios o faltantes de payload, pero no dependencias huérfanas o ciclos. El negativo decisivo fue un atacante que modifica el payload y recalcula el hash del manifiesto: las tres políticas aceptaron los 40 casos. Esto ocurre porque el verificador carece de raíz de confianza independiente. El resultado demuestra consistencia local, no autenticidad ni verdad del linaje.

## Página 2 — Brecha y problema

Los flujos de ML intercambian conjuntos de datos, parámetros, métricas, código, pesos y aprobaciones entre almacenamiento y herramientas. Una referencia rota o un archivo alterado tras el registro puede llevar a que un auditor examine evidencia distinta a la que produjo el modelo. La pregunta práctica es si un consumidor offline puede detectar inconsistencias internas antes de seguir una cadena de análisis.

La brecha identificada es concreta: el programa tiene una especificación de ledger, pero no una implementación mínima de inspección estructural ni pruebas que muestren qué errores detecta. Se evita reproducir un servidor de tracking, una cadena de suministro completa o un protocolo de firma. El componente recibe una carpeta con manifiesto, recorre el grafo declarado y devuelve hallazgos deterministas.

No evalúa legalidad, representatividad o corrección del dataset; calidad estadística del modelo; si una aprobación fue otorgada por la persona indicada; o si el builder ejecutó el código declarado. Este alcance reducido permite probar controles básicos, pero exige una interpretación estrecha: coherencia del paquete respecto a su propio manifiesto.

## Página 3 — Comparación de candidatas

Se compararon tres líneas por brecha no cubierta, importancia, originalidad incremental, viabilidad verificable y coste de sobreafirmación (matriz detallada en `prior_art.md`). A, verificación de integridad/completitud de evidencia ML, fue elegida: el diseño interno menciona hashes y DAG sin implementación, y la prueba puede aislarse sin datos privados.

B, provenance firmada de builder con raíz de confianza, cubre amenazas más fuertes, pero SLSA, in-toto y TUF ya ofrecen marcos maduros. Construir una versión improvisada sin PKI ni gobernanza de claves sería incompleto. Se difiere para integrar estándares existentes. C, ledger append-only o árbol Merkle distribuido, podría detectar ciertas reescrituras, pero exige servicio, retención y pruebas de consistencia; tampoco resuelve quién declara la fuente verdadera. Se difiere hasta demostrar necesidad de auditoría multiusuario.

A es una elección del ciclo y una brecha implementable, no una afirmación de superioridad universal. Las alternativas pueden ser mejores con threat model organizacional, emisores de attestations y ciclo de vida de claves definidos.

## Página 4 — Hipótesis y criterios fijados

La unidad experimental es un paquete local con tres artefactos: dataset, modelo y aprobación. Cada elemento declara `id`, `path` relativo, digest SHA-256, tipo y `depends_on`. El manifiesto declara esquema y clases requeridas. La decisión es binaria: ningún hallazgo significa aceptar; uno o más significa rechazar.

La hipótesis se limita a corrupción posterior al manifiesto, no al atacante que domina el manifiesto. Los umbrales guardados en `config.json` son 100% de aceptación de bundles limpios, detección completa de cambios post-escritura y detección completa de errores de dependencia o ciclos. Las 40 réplicas por escenario comprueban estabilidad determinista del fixture; no estiman una tasa poblacional de seguridad.

También se fijó el negativo fuera de la hipótesis principal: editar el archivo y recalcular su hash en el manifiesto. Si se acepta, los hashes no autentican la declaración. Es un control interpretativo que previene comunicar integridad interna como prueba de linaje auténtico.

## Página 5 — Diseño del algoritmo

El método carga `manifest.json`, valida el esquema mínimo, verifica IDs únicos, revisa paths relativos sin segmentos `..`, lee los payloads y compara sus SHA-256 con el digest esperado. El conjunto de tipos presentes debe cubrir los requeridos. En el DAG se comprueba que cada dependencia exista y una búsqueda DFS detecta ciclos usando estados activos y visitados.

El recorrido cuesta O(V+E) tiempo y memoria para V artefactos y E relaciones. Lectura y hashing suman O(B), total de bytes. El programa retorna hallazgos tipados en lugar de detenerse ante el primer problema. La serialización auxiliar `canonical_json` ordena claves, compacta JSON y excluye NaN; no implementa RFC 8785 ni se utiliza para firmar/verificar identidad.

El código modular está en `src/evidence_integrity/core.py`. La operación es offline y no depende de claves. El hash implementado es SHA-256 sobre los bytes del archivo recuperado. El verificador no interpreta semánticamente el contenido ni valida que el digest declarado se origine en un actor autorizado.

## Página 6 — Datos y procedencia

No se usaron datos de producción, incidentes observados ni ejemplos empíricos. El generador crea CSV sintético, bytes de pesos simulados y un JSON de aprobación ficticio. Los datos existen sólo para ejecutar el contrato sin red, credenciales o licencias de corpus.

`results/raw_cases.csv` conserva réplica, modo mutado, resultado esperado y decisiones de baseline, hash-only y verificador completo. `results/summary.json` agrega aceptaciones; `results/acceptance.png` muestra conteos sobre 40 por condición. Los números describen ejecución determinista, no prevalencia, frecuencia de ataques ni eficacia esperada en una organización.

El tipo `approval` se comprueba por presencia y hash; su contenido no se autentica ni valida como decisión válida. El verificador no prueba que el dataset sea real, que el actor aprobador exista ni que el código entrenado coincida con el manifiesto. El fixture no sirve como benchmark externo y no refleja artefactos de escala real.

## Página 7 — Baselines y ablaciones

El baseline comprueba que exista un manifiesto parseable, el esquema y cobertura nominal de tipos requeridos. No contrasta archivos ni aristas. Hash-only recalcula SHA-256 de cada payload, sin validar dependencias o ciclos. El método completo añade estructura, rutas, IDs y grafo.

Los tres aceptan 40/40 limpios. Para payload alterado y archivo ausente, baseline acepta 40/40; hash-only y método completo aceptan 0/40. Para dependencia inexistente y ciclo, baseline y hash-only aceptan 40/40, mientras el método completo acepta 0/40. En el negativo auto-rehash, las tres alternativas aceptan 40/40.

La ablación indica que el DAG aporta detección distinta de los hashes. El negativo confirma que un grafo y digest autoconsistentes no validan legitimidad. Estos comparadores son políticas de ingeniería con contrato conocido, no métodos competidores seleccionados por rendimiento sobre una prueba de ML.

## Página 8 — Resultados cuantitativos

Se ejecutaron 240 filas: seis condiciones por 40 réplicas. Los controles limpios tuvieron 40 aceptaciones de 40 en las tres políticas. Para las cuatro condiciones cubiertas por la hipótesis de mutación ex post, el método completo tuvo cero aceptaciones en 160 filas; detección observada 100% dentro del fixture.

Baseline tuvo cero detecciones entre esas 160 filas porque no observa payload ni relaciones suficientemente. Hash-only rechazó 80 filas de payload editado o faltante y aceptó las 80 de error de grafo. El método completo rechazó las cuatro clases. En el escenario rehash, el método completo aceptó 40/40, refutando cualquier garantía general frente a un atacante con control del manifiesto.

No se calculan intervalos binomiales: las réplicas son clones generados por la misma función, no muestras aleatorias independientes. Tampoco se reportan p-values o inferencia causal. La diferencia proviene de los controles implementados y de la prueba de contrato, no de estimar un efecto externo. El CSV y JSON son la fuente de resultados.

## Página 9 — Sensibilidad y prueba negativa

La sensibilidad se presenta mediante ablaciones: se cambia la política de chequeo y se observa qué ataques evita y cuáles deja pasar. Las pruebas unitarias incluyen ID duplicado, manifiesto malformado, traversal de paths, archivo ausente, determinismo de canonicalización del subconjunto y sensibilidad del hash a un byte distinto.

El hallazgo negativo tiene una implicación de producto: si el mismo actor puede reemplazar contenido y manifiesto, la comprobación no autentica nada. No necesita romper SHA-256; basta recalcular el digest legítimo del payload elegido. El control atraviesa todas las políticas y evita concluir que “la provenance está asegurada” por resultados positivos de mutaciones unilaterales.

Faltan colisiones diseñadas, symlinks fuera de raíz, TOCTOU, archivos remotos, carreras, bundles grandes, grafos profundos, Unicode visualmente ambiguo y parsing entre lenguajes. La siguiente etapa debe añadirlos junto con amenaza y política de confianza explícitas.

## Página 10 — Pruebas y reproducibilidad

Las pruebas automatizadas cubren paquete correcto, cambio de payload, dependencia faltante, ciclo, payload ausente, path inseguro, manifiesto malformado, orden equivalente de claves JSON y sensibilidad de SHA-256 a cambios de bytes. Las propiedades se exploran en ciclos finitos deterministas; no se afirma cobertura matemática universal.

`run_experiment.py` genera fixtures temporales, ejecuta las tres políticas y guarda CSV/JSON/figura. `notebook.ipynb` explica y reproduce tablas/figura. `run.sh` es el comando único, ejecuta simulación, pruebas y notebook. Las repeticiones no emplean aleatoriedad; la etiqueta `seed_case` sólo identifica la réplica.

El núcleo y tests usan biblioteca estándar. Para gráfica y notebook se requiere Python, pandas, matplotlib, nbformat y nbclient; se listan en `requirements.txt`. Los resultados guardados corresponden a esta ejecución local. No se afirma que todos los sistemas tengan versiones idénticas; CI limpia y versiones bloqueadas son trabajo posterior.

## Página 11 — Literatura y estándares

W3C PROV define un modelo conceptual de entidades, actividades, agentes y derivaciones. Es un vocabulario interoperable, no una autenticación por sí solo. RFC 8785 define JSON Canonicalization Scheme y evita ambigüedad de serialización en firmas; el helper local no pretende implementarlo.

SLSA describe provenance de build y recomienda verificar builder confiable, firmas y parámetros esperados. in-toto presenta un marco de pasos de supply chain y verificación contra layout firmado. TUF trata distribución segura mediante roles, claves, umbrales, versiones y expiración. MLflow Tracking registra parámetros, código, métricas y artefactos; su Model Registry documenta lineage y versionado.

El MVP no reemplaza estas herramientas: prueba consistencia de un bundle hipotético exportado. Los estándares relevantes priorizan controles autenticados, mientras este prototipo implementa consistencia autocontenida. Hay siete referencias verificables con vínculos en `referencias.bib` y comparativa en `prior_art.md`.

## Página 12 — Interpretación y madurez

La clasificación es **diseño del ledger con prototipo M2**: código modular, configuración, pruebas, datos sintéticos reproducibles, notebook, raw CSV/JSON, baseline, ablation y límites. M2 califica el componente, no el dominio entero.

No es **validado**: falta corpus independiente, pipeline real, evaluación fuera de muestra, escala, revisión independiente y política de confianza. No es **operacional**: no hay servicio, manejo de claves, permisos, auditoría de producción, monitorización, rollback, SLO o responsable de incidentes.

Puede usarse como inspector local de calidad estructural durante investigación. Usarlo para aprobar un modelo excedería la evidencia. Un bundle que pasa puede contener valores inventados, fuente falsa o aprobación inválida. Si una decisión exige garantizar origen y el sistema no dispone de verificador de confianza externo, se debe abstener de dar esa garantía.

## Página 13 — Riesgos y límites

El principal riesgo es la interpretación: digest correcto demuestra igualdad de bytes frente a la expectativa codificada, no que el artefacto venga de proceso autorizado. Un grafo sin ciclos no demuestra que sea verdadero o completo. Los tipos requeridos son contrato declarativo, no fuente de verdad.

El manifiesto completo se carga en memoria y no tiene límites de recursos. DFS recursivo puede fallar con profundidad elevada. La comprobación bloquea rutas absolutas, `..` y symlinks detectados. Sigue abierta una carrera TOCTOU entre validación y uso; el consumidor seguro debería fijar descriptores y evitar resolver de nuevo la ruta.

La función de serialización no sigue toda RFC 8785. El siguiente endurecimiento debe definir esquema versionado, límites, política de symlinks, parsing estricto y manejo seguro de errores. Aun así, ninguna mejora local de parsers sustituye a firmas verificadas contra identidad y expectativas confiables.

## Página 14 — Decisiones y pasos siguientes

Se conserva el resultado negativo sin ajustar hipótesis a posteriori. El siguiente paso útil es fijar expectativa de confianza fuera del bundle: integrar formatos de attestation y bibliotecas mantenidas para firma/identidad, y adaptar después el DAG al ciclo de ML. El roadmap prioriza export/import de un tracker, escenarios de atacante con permisos diferenciados, evaluación independiente y pruebas de escala, paths, symlinks y TOCTOU.

Antes de cualquier despliegue deben existir emisores permitidos, expiración, revocación, anti-rollback y política de claves. Sin raíz de confianza no se debe usar este componente para una decisión de alta consecuencia.

**Conclusión:** se satisface la hipótesis limitada sobre los fixtures: rechazo total de las corrupciones ex post seleccionadas y aceptación de controles limpios. La hipótesis universal de autenticidad queda refutada por 40/40 rehash coordinados. El resultado demuestra un inspector local de consistencia estructural y un límite de seguridad accionable; no demuestra efectividad empírica, originalidad científica, validación operacional ni confianza en la provenance declarada.
