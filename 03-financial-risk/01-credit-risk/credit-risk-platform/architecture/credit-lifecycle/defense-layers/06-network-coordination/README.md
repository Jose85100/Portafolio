# Análisis de coordinación y vínculos entre casos

**Capa defensiva adicional · S1, diseño y estudios propuestos.** Se añade al ciclo de crédito sin sustituir KYC, riesgo, workflow, core o pagos. No es necesariamente un servicio separado.

**Objetivo:** Investigar redes de solicitudes, teléfonos, dispositivos y destinos sin propagar culpabilidad entre vecinos legítimos.

**Etapas:** Originación, Fraude, Destino de fondos, Investigación.

**Responsable propuesto:** Fraude/investigación con fuentes habilitadas y modelo de vinculación validado.

## Controles y alcance

| Control | Diseño a evaluar |
|---|---|
| Relaciones tipadas | Compartir IP, teléfono, documento o beneficiario son relaciones distintas con confianza y caducidad. |
| Tiempo y disponibilidad | Grafo al corte; ninguna relación futura entra en la decisión histórica. |
| Corroboración y deduplicación | Un componente genera hipótesis de caso; no una decisión adversa para cada vecino por asociación. |

## Estudios adicionales de la capa

### NETWORK-BENIGN · Hogar/oficina compartidos frente a coordinación

**Diseño propuesto:** Generar grafos con grupos legítimos y patrones coordinados controlados; comparar conteos tipados y un challenger sin usar vecinos futuros.

**Medición:** Vínculos falsos, captura del patrón, falsas alertas por entorno compartido y carga deduplicada.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

### NETWORK-DESTINATION · Cuenta receptora común con distintas explicaciones

**Diseño propuesto:** Escenarios ficticios distinguen destino comercial autorizado, intermediario legítimo y destino inconsistente; comprobar titularidad/contexto y evitar clasificación por grado solamente.

**Medición:** Precisión de hipótesis, evidencia faltante y falsas asociaciones.

**Estado:** no ejecutado; requiere baseline, fixtures versionados, controles legítimos y evidencia para evaluar el control.

## Conexión con proyectos

- [01-geo-device-context](../../projects/01-geo-device-context/README.md)
- [02-provider-orchestration](../../projects/02-provider-orchestration/README.md)
- [05-disbursement-reconciliation](../../projects/05-disbursement-reconciliation/README.md)
- [08-risk-data-observability](../../projects/08-risk-data-observability/README.md)

## Riesgo residual

- La titularidad de una cuenta no prueba que la transacción sea libre de engaño.
- Cambios de identificador y datos incompletos pueden romper vínculos o crear asociaciones falsas.

## Criterio para avanzar

Definir primero la capacidad del actor y la frontera de confianza. Preparar casos sintéticos y una ruta legítima comparable; medir fallos críticos, cobertura, fricción y costo. Un control solo se incorpora si puede observarse cuándo se ejecutó y qué verificó. El pase de una prueba local no acredita seguridad de extremo a extremo.

[Mapa de las ocho capas](../README.md) · [Estudios adversariales de los diez proyectos](../../projects/THREAT_MODEL.md) · [Cuatro vistas draw.io defensivas adicionales](../diagrams/README.md).
