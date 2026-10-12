# Diseño técnico y lectura ejecutiva

## Modelo de decisión

```text
Margen=P−CV; beneficio=N·Margen−CF; LTV≈Margen/churn, si churn>0.
```

## Diagrama

```mermaid
flowchart LR
 A["Hipótesis de negocio"] --> B["Parámetros y límites"]
 B --> C["Validación de datos"]
 C --> D["Motor cuantitativo"]
 D --> E["Indicadores de decisión"]
 E --> F["Revisión de comité"]
```

El último paso es una revisión humana, no una aprobación automática.

## Supuestos

Churn geométrico constante, sin descuento temporal ni expansión de ingresos. CAC es un coste de adquisición por cliente, no gasto mensual.

## Controles y pruebas

Sensibilidad a precios, costos, churn y CAC; distinguir LTV bruto de contribución neta de adquisición.

## Aplicación ejecutiva

CEO/Head: localizar segmentos rentables y verificar sostenibilidad antes de escalar.

## Riesgos de interpretación

Los datos son sintéticos y no están calibrados a una empresa. No existe conexión con ERP, core bancario, CRM ni sistemas de gobierno. La utilidad de una política requiere estimación, validación y responsabilidad institucional. La optimización matemática no sustituye la discusión de restricciones legales, regulatorias y reputacionales.

## Reproducir

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/09-business-unit-economics-pricing/tests -v
```
