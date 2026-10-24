# Inteligencia de fraude y contexto de amenaza

**Capa defensiva adicional · S1, diseño y estudios propuestos.** Se añade al ciclo de crédito sin sustituir KYC, riesgo, workflow, core o pagos. No es necesariamente un servicio separado.

**Objetivo:** Interpretar patrones de abuso y dependencias con procedencia, confianza, vigencia y alternativa benigna.

**Etapas:** Canales, Orquestación, Investigación, Monitoreo.

**Responsable propuesto:** Equipo de fraude con privacidad/seguridad para alcance de fuentes; no un servicio de vigilancia de personas.

## Controles y alcance

| Control | Diseño a evaluar |
|---|---|
| Indicadores con procedencia | Registrar origen, fecha, confianza, cobertura y motivo de uso; un indicador de terceros no es condena ni label. |
| Hipótesis alternativas | Confrontar coordinación ilícita aparente con hogar compartido, nuevo dispositivo, viaje, asistencia y error operacional. |
| Dependencia de fuente | Varias respuestas que dependen del mismo hecho no se convierten en evidencias independientes. |

## Estudios adicionales de la capa

### INTEL-PROVENANCE · Indicador dudoso propagado por varias fuentes

**Diseño propuesto:** Dataset ficticio incluye un indicador equivocado compartido por tres fuentes y luego corregido. Comparar agregación ingenua y linaje con confianza/estado.

**Medición:** Falsos vínculos, duplicación de evidencia y propagación de corrección.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

### INTEL-EXPIRY · Patrón obsoleto bajo nueva población

**Diseño propuesto:** Cambiar antigüedad y base de exposición de indicadores sintéticos; evaluar cohortes sin asumir que el patrón observado sigue activo.

**Medición:** Alerta útil, carga de revisión, caducidad y daño en controles legítimos.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

## Conexión con proyectos

- [01-geo-device-context](../../projects/01-geo-device-context/README.md)
- [02-provider-orchestration](../../projects/02-provider-orchestration/README.md)
- [08-risk-data-observability](../../projects/08-risk-data-observability/README.md)
- [09-purpose-bound-signal-governance](../../projects/09-purpose-bound-signal-governance/README.md)

## Riesgo residual

- El permiso técnico de una fuente no habilita cualquier finalidad; solo fuentes y datos institucionalmente admisibles.
- La ausencia de un indicador no demuestra legitimidad y la presencia no confirma autoría.

## Criterio para avanzar

Definir primero la capacidad del actor y la frontera de confianza. Preparar casos sintéticos y una ruta legítima comparable; medir fallos críticos, cobertura, fricción y costo. Un control solo se incorpora si puede observarse cuándo se ejecutó y qué verificó. El pase de una prueba local no acredita seguridad de extremo a extremo.

[Mapa de las ocho capas](../README.md) · [Estudios adversariales de los diez proyectos](../../projects/THREAT_MODEL.md) · [Cuatro vistas draw.io defensivas adicionales](../diagrams/README.md).
