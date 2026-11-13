# Cobertura explícita de marcos y motores

Actualizado: 2026-11-10. Una carpeta o especificación no acredita implementación completa.

| Marco | Carpeta propietaria | Fundamentos / motor objetivo | Evidencia actual |
|---|---|---|---|
| Basilea III y reformas finales, llamadas Basilea IV | [Capital](08-capital-rwa-icaap-ilaap/) | Pilares, capital elegible, buffers, transición y métodos por riesgo | Diseño; transposición local pendiente |
| RWA | [Capital](08-capital-rwa-icaap-ilaap/) | Exposición, ponderadores, mitigantes y conciliación | Función ilustrativa de suma ponderada probada |
| ICAAP | [Capital](08-capital-rwa-icaap-ilaap/) | Materialidad, suficiencia y proyección bajo estrés | Diseño |
| ILAAP | [Capital](08-capital-rwa-icaap-ilaap/) y [SARL](04-sarl-liquidity/) | Suficiencia de liquidez, contingencia y escenarios | Diseño; trayectoria de caja ilustrativa probada |
| SREP | [Revisión supervisora](14-srep-supervisory-review/) | Evidencia, hallazgos y consistencia ICAAP/ILAAP | Diseño comparativo europeo |
| ISO 31000 | [ERM](11-erm-kri-model-governance/) | Contexto, evaluación, tratamiento, seguimiento y comunicación | Diseño; sin certificación |
| COSO ERM | [ERM](11-erm-kri-model-governance/) | Estrategia, objetivos, desempeño, revisión e información | Diseño |
| BCP | [Continuidad](10-bcp-cyber-third-party/) | BIA, servicios críticos, RTO/RPO y ejercicios | Diseño |
| KRIs | [ERM](11-erm-kri-model-governance/) | Diccionario, dirección, umbrales y escalamiento | Clasificador de umbrales probado |
| SARLAFT | [SARLAFT](09-sarlaft-financial-crime/) | Debida diligencia, segmentación, señales y casos | Diseño; fuente SFC |
| SAGRILAFT | [SAGRILAFT](13-sagrilaft/) | Aplicabilidad, contrapartes y beneficiarios finales | Diseño; fuente Supersociedades |

## Patrón de implementación por marco

Cada motor futuro debe tener spec, contrato de entradas/salidas, norma y fecha, casos manuales, código, pruebas, notebook con fórmulas y sensibilidad, manifiesto de ejecución y límites. Separar reglas normativas de modelos estadísticos y de decisiones humanas. No crear copias de bibliotecas existentes.

## Extensiones de motores por marco

- Basilea/RWA: adaptadores por método y clase de exposición, trazabilidad de mitigantes y puente de variación de RWA.
- ICAAP/ILAAP: proyección conjunta de balance, escenarios comunes y estrés inverso con acciones factibles.
- ISO/COSO: registro objetivo-riesgo-control, efectividad evidenciada y cobertura de responsabilidades.
- BCP: simulador de interrupciones con dependencias y comparación de tiempo de recuperación frente a objetivos.
- KRIs: persistencia, histéresis, escalamiento y validación temporal de alertas.
- SARLAFT/SAGRILAFT: componentes analíticos compartidos con reglas y reportes separados.

Estas extensiones son propuestas; solo las seis funciones del directorio engines tienen ejecución local documentada.
