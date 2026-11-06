# Inventario transversal de datos reales, proxies y simulaciones

**Alcance:** todo el repositorio Jose85100/Portafolio. Fecha de levantamiento 2026-11-05. La clasificación de proyectos adjunta está basada en READMEs confirmados y especificaciones del repositorio, no es una auditoría manual exhaustiva de cada celda. **No declarar sustitución completada salvo que exista pipeline ejecutado y evidencia del propio proyecto.**

## Artefactos

- [Matriz de migración priorizada](migration_matrix.csv): más de 30 rutas/áreas concretas con variable, fuente, política y bloqueo.
- [Escáner de archivos y notebooks](../../tools/data_provenance_audit.py): recorre `git ls-files`; detecta señales de generación sintética, referencias externas y semillas en código Python, notebooks, C/C++, R, Julia, Matlab y SQL. Ignora markdown de notebooks; registra errores.
- [GitHub Actions](../../.github/workflows/data-provenance-audit.yml): genera `file_inventory.csv` y `summary.json` y los conserva como artefactos temporales.
- [Tests](../../tests/test_data_provenance_audit.py): cobertura de detección sintética, real y mixta.

## Taxonomía obligatoria

| Estado | Significado |
|---|---|
| SYNTHETIC_CANDIDATE | El archivo contiene generación de simulaciones; puede ser intencional o accesorio |
| EXTERNAL_SOURCE_CANDIDATE | El código refiere fuentes o lecturas externas; **no demuestra descarga exitosa** |
| MIXED_REVIEW | Ambas señales; identificar dataset para entrenamiento, control, test y stress |
| NO_SIGNAL | Sin señal textual; no significa que el archivo no use datos externos |

El campo `verified_observed_integration` vale por defecto `NOT_VERIFIED`, incluso si el archivo contiene una URL. Los estados `EXECUTED_BRANCH_NOT_MERGED` de la matriz son independientes y se soportan en ejecución de la PR #152.

## Reglas de migración

1. El *owner* del problema determina unidad de observación, fecha de ocurrencia, fecha de disponibilidad y target. No se acepta un proxy por parecido del nombre de variable.
2. Fuente real > proxy observado > estimación por supuestos > simulación, pero las simulaciones con verdad conocida, Monte Carlo, equilibria o pruebas adversariales **no se borran**.
3. Nunca usar mora agregada para fabricar PD individual. Ni transiciones de mora, SICR, lifetime PD, LGD, EAD o recuperaciones sin datos adecuados.
4. Una fuente nueva entra con licencia, URL, versión de esquema, cobertura, grano, periodo, `published_at`, `retrieved_at`, hash, idempotencia, sensibilidad, sesgos conocidos, controles negativos y data quality gate.
5. Para series macro, backtesting exige datos conocidos en cada corte; el valor revisado hoy puede inducir *look-ahead*.
6. Para finanzas de mercado, usar precios ajustados, dividendos, delistings, calendarios y costo de transacción cuando corresponda.
7. Para RAG jurídico, el corpus necesita autoridad, vigencia, versión, jurisdicción, textos oficiales y evaluación humana.
8. La promoción `NOT_INTEGRATED -> INGESTED -> VERIFIED -> MODEL_CONNECTED -> EMPIRICALLY_VALIDATED` requiere evidencia y tests de la ruta específica.
9. Mantener `main` sin cambios hasta revisión de los nuevos commits y CI.

## Prioridad de ejecución

**P0:** conectar scorecard existente con microdatos UCI (horizonte 1 mes), migrar señales observadas ICETEX a feature mart agregado, macro nowcasting con series versionadas, VaR/GARCH con retornos observados y asset management con precios ajustados.

**P1:** DANE/BanRep para modelos económicos, ECL con supuestos explícitos y escenario macro, auditoría de data platform, RAG de fuentes oficiales y estados financieros para motores ejecutivos.

**P2:** problemas donde se debe conservar simulación estructural o no existen datos públicos apropiados (juegos, eventos extremos raros, ciertos seguros, capital privado, datos conductuales).

## Interpretación y limitaciones

El escáner cuantifica **referencias de código**, no archivos que ya poseen observaciones válidas. Si CI termina exitosamente, el total de candidatos será auditable. Los README pueden contradecir ejecuciones posteriores: hay que contrastar resultados contra commits y artefactos. La matriz es una primera capa de mapeo con 34 rutas/áreas, no prueba de cobertura completa por subcarpeta. El estado real de datos debe trazarse en la segunda fase con verificación de datasets y resultados por proyecto.

## Inventario de datos existentes en Drive — Master_DATOS

Se revisó [Master_DATOS](https://drive.google.com/drive/folders/1mcy86SL7qLssZFwbVvpjyFP15ckeuzFt), con áreas ATLAS_ECONOMICO_COLOMBIA, ATLAS_EMPRESAS, SHADOW_RISK, INVESTMENT_OS y gobierno de datos. Consultar [registro de fuentes Drive](drive_master_data_sources.csv): contiene IDs de origen, ruta, variable, consumidor, estado de inspección y validación pendiente. Los estados `CONTENT_READ` prueban acceso al contenido y `LISTED` únicamente existencia/metadata, no aprobación estadística.

**Política:** Master_DATOS mantiene los raws canónicos; Portafolio versiona código, contratos y referencias. No copiar tablas extensas o archivos potencialmente restringidos a Git. Respetar publicación-vintage, permisos, hashes y gobierno de datos documentado en Drive. El origen oficial de cada fuente debe verificarse independientemente del nombre del archivo.

**Dos archivos comprobados por contenido:** series de tasas mensuales BanRep (columnas `mes, dtf_promedio, ibr_promedio, tib_promedio, observaciones_*`) y agregado nacional SFC (fecha, depósitos, CDT, cartera, vivienda, oficinas). Ninguno equivale a una PD individual o una ECL por contrato.

**Pendiente para convertir el inventario en integración:** validar esquemas y unidades por dataset, leer manifiestos, definir credenciales de solo lectura de Drive fuera del repo, registrar source_id y hashes para cada carga, construir mart por grano, correr pruebas y luego ejecutar notebooks existentes con origen observado. El mapeo no prueba modificación de modelos.
