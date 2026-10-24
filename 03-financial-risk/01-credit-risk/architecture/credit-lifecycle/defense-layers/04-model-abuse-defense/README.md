# Protección frente a sondeo y contraingeniería

**Capa defensiva adicional · S1, diseño y estudios propuestos.** Se añade al ciclo de crédito sin sustituir KYC, riesgo, workflow, core o pagos. No es necesariamente un servicio separado.

**Objetivo:** Reducir abuso de interfaces, inferencias indebidas y extracción de información sin sacrificar explicación fiel y derechos.

**Etapas:** API, Motor de decisión, Explicación, Observabilidad.

**Responsable propuesto:** Seguridad de aplicación y model risk; cumplimiento/atención para requisitos de explicación.

## Controles y alcance

| Control | Diseño a evaluar |
|---|---|
| Superficie de respuesta | Exponer información necesaria y razones fieles, separando respuesta al cliente de datos internos/secretos del modelo. |
| Intentos correlacionados | Medir repetición por caso/actor/contexto con límites apropiados; contemplar reintentos legítimos y redes compartidas. |
| Robustez de política | Buscar discontinuidades/inestabilidad con casos sintéticos; proteger integridad de variables y versión de política. |

## Estudios adicionales de la capa

### MODEL-PROBING · Sondeo acotado de un modelo de laboratorio

**Diseño propuesto:** Modelo propio sintético con presupuesto de consultas fijo; comparar salida mínima suficiente y salida con datos internos innecesarios. Evaluar estabilidad y capacidad de detectar abuso, sin extraer modelos de terceros.

**Medición:** Información interna expuesta, alertas de abuso, costo y fricción de usuarios legítimos.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

### MODEL-EXPLANATION · Explicación fiel bajo restricciones de información

**Diseño propuesto:** Comparar razones generadas desde reglas/atribuciones verificadas con texto libre en un corpus ficticio; comprobar que la reducción de detalle no invente la causa ni oculte errores revisables.

**Medición:** Fidelidad de razón, discrepancias, campos secretos expuestos y capacidad de revisión.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

## Conexión con proyectos

- [01-geo-device-context](../../projects/01-geo-device-context/README.md)
- [03-credit-offer-policy](../../projects/03-credit-offer-policy/README.md)
- [08-risk-data-observability](../../projects/08-risk-data-observability/README.md)
- [09-purpose-bound-signal-governance](../../projects/09-purpose-bound-signal-governance/README.md)

## Riesgo residual

- Ocultar un umbral no corrige un mal modelo ni elimina derechos de explicación/reclamación.
- Rate limits pueden perjudicar oficinas o redes compartidas; deben evaluarse como política, no identidad.

## Criterio para avanzar

Definir primero la capacidad del actor y la frontera de confianza. Preparar casos sintéticos y una ruta legítima comparable; medir fallos críticos, cobertura, fricción y costo. Un control solo se incorpora si puede observarse cuándo se ejecutó y qué verificó. El pase de una prueba local no acredita seguridad de extremo a extremo.

[Mapa de las ocho capas](../README.md) · [Estudios adversariales de los diez proyectos](../../projects/THREAT_MODEL.md) · [Cuatro vistas draw.io defensivas adicionales](../diagrams/README.md).
