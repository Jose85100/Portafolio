# Data Engineering — Ingeniería de Datos

Línea independiente dentro de AI Architecture & Automation, con foco en plataformas analíticas y de riesgo financiero.

## Áreas

- Arquitecturas batch, microbatch y streaming; lakehouse, warehouse y data marts.
- Modelado dimensional, Data Vault, contratos de datos y evolución de esquemas.
- ELT/ETL, CDC, ingesta de APIs, bases SQL, almacenamiento de objetos.
- Orquestación con n8n, Airflow y Dagster; idempotencia, reintentos y backfills.
- Calidad de datos, observabilidad, reconciliación, linaje y manifiestos de evidencia.
- Infraestructura como código, CI/CD, seguridad, control de acceso y costos.
- Data products para econometría, IFRS 9, riesgos, nowcasting y motores quant.

## Productos propuestos

1. **Risk Data Platform**: ingesta D+1, normalización, calidad, versionamiento y publicación de datasets de riesgo.
2. **Macro Data Lakehouse**: ingesta reproducible de series públicas, calendarios de publicación, vintage data y nowcasting.
3. **Data Quality & Lineage Engine**: reglas declarativas, auditoría, alertas, linaje y reconciliación de métricas.
4. **Quant Research Data Factory**: pipelines para experimentos, datasets point-in-time, feature store y reproducibilidad.
5. **Workflow Orchestrator**: automatizaciones SQL/Python/n8n con control de fallos, reejecución segura y alertas.

## Estándar de entrega

Cada producto debe documentar arquitectura física y lógica, esquemas, contratos, SLA/SLO, pruebas, seguridad, reproducibilidad, costos, observabilidad y límites operativos.

**Estado:** catálogo y línea de trabajo creados; los cinco productos descritos son propuestas, no implementaciones terminadas.

## Relación con otros dominios

- Economía: series temporales, datos públicos y revisiones de datos.
- Riesgos: cartera, provisiones, liquidez y mercado.
- Quant: precios, factores, señales y backtesting point-in-time.
- IA: pipelines RAG, agentes y evaluación de modelos.

## Implementación disponible

- [Risk Data Platform — MVP ejecutable](risk-data-platform/): ingesta incremental CSV, contratos de datos, validación, deduplicación, reconciliación y manifiesto SHA256, con pruebas unitarias y CI.

Los otros cuatro productos del catálogo siguen en fase de propuesta. La plataforma implementada es un MVP local, no un servicio cloud productivo.
