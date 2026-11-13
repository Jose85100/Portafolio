# MVP: verificador de integridad y completitud de evidencia

## Pregunta e hipótesis

¿Un verificador local del paquete puede evitar aceptar artefactos faltantes o alterados después de la escritura del manifiesto, así como relaciones incompletas/cíclicas, sin rechazar bundles correctos? Hipótesis preregistrada en `config.json`: en 40 réplicas por modo, aceptación 40/40 de controles limpios, rechazo 40/40 de alteración/pérdida de payload y de corrupción de dependencias. Un ataque que modifica tanto el payload como la referencia de hash se registra como prueba negativa; no forma parte de la hipótesis de integridad ex post.

## Unidad, alcance y contrato

La unidad es un bundle local con `manifest.json` y paths relativos confinados a su raíz. Cada entrada declara identificador único, tipo, path, SHA-256 y dependencias. Se exigen tipos de evidencia declarados por política; dependencias deben existir y formar un DAG. El componente devuelve hallazgos deterministas; no interpreta el contenido, licencia, validez estadística ni semántica de cada artefacto.

## Método

El verificador calcula SHA-256 de bytes recuperados, revisa completitud estructural y valida aciclicidad por DFS en O(V+E) temporal y O(V+E) espacio. El almacenamiento y lectura de payloads añade O(B), donde B es el total de bytes. Serialización canónica auxiliar ordena claves JSON y elimina espacios; no se usa como firma. Rutas absolutas, segmentos `..` y symlinks se rechazan; permanece una ventana TOCTOU entre inspección y uso posterior.

## Protocolo

Cada réplica construye el mismo paquete sintético mínimo y aplica una sola mutación declarada: ninguna, edición posterior del payload, borrado, referencia huérfana, ciclo, o edición más recálculo del hash en manifiesto. Se comparan tres políticas: (i) baseline de manifiesto y tipos, (ii) ablación con hashes solamente, (iii) verificador completo. Cada escenario se repite 40 veces para chequear determinismo, no para inferir una tasa poblacional. CSV y JSON guardan observaciones en bruto y agregados.

## Umbrales de aceptación

Se exige 100% de controles limpios aceptados y 100% de rechazo de las cuatro clases de corrupción que ocurren después de fijar el manifiesto. Umbral es criterio de aceptación del fixture, no SLO ni intervalo poblacional. Las 40 pruebas por modo son reproducciones deterministas del mismo escenario, no n=40 casos independientes.

## Resultados y falsación

Se satisfacen los umbrales sobre los casos cubiertos: 40/40 limpios aceptados; en cada ataque ex post (payload, ausencia, dependencia y ciclo), 40/40 rechazados. Baseline acepta las corrupciones porque no lee o contrasta evidencia; hash-only detecta payload pero deja pasar dependencias y ciclos. En la condición auto-rehash, las tres políticas aceptan las 40 réplicas. Por tanto, la hipótesis operacional se limita explícitamente al atacante incapaz de reemplazar el manifiesto o sus expectativas de confianza.

## Límites

Los datos son fixtures sintéticos y no representan incidencias reales ni distribución de amenazas. El verificador no implementa autenticación, firmas, rotación de claves, revocación, anti-rollback, procedencia del builder, custodia de logs, compatibilidad con SLSA/in-toto, semántica de aprobación, ni protección frente a atacante que controla el manifiesto. No debe autorizar despliegues sin esas capas.
