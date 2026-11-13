# Agenda de motores y evidencia

## Entregado

**Catorce dominios** documentados y seis funciones numéricas de referencia con pruebas: RWA ponderado ilustrativo, ECL con hazard condicional, ES empírico, trayectoria de caja, pérdida operacional anual simulada y clasificación de KRI. No son motores regulatorios completos.

## Siguiente etapa por dominio

Cada una de las catorce carpetas de dominio contiene tres líneas: **42 ideas de investigación**. Convertir cada línea en un experimento con baseline, hipótesis refutable, datos, fórmula, notebook y criterio de cierre; no contar ideas como implementaciones.

## Orden de implementación

1. Resolver perímetro, fuentes normativas y contratos; completar mapa de equivalencias SFC.
2. Integrar bibliotecas existentes de crédito/IFRS 9 y mercado antes de construir adaptadores nuevos.
3. Extender liquidez, capital y estrés con escenarios comunes y conciliación de balance.
4. Construir registro de eventos SARO, evaluación SARAS y gestión de casos SARLAFT.
5. Añadir tableros KRIs, evidencia de BCP, conducta, calidad y reporte.
6. Validación independiente, evaluación con datos reales y controles operacionales.

## Criterio de promoción

S1: especificación y fuentes. S2 acotado: código reproducible, pruebas con casos manuales y notebook ejecutado. Validación empírica requiere muestra representativa, diseño temporal y revisión independiente. Operación requiere monitoreo, permisos, auditoría y recuperación. Las funciones entregadas no promocionan por sí solas los catorce dominios a S2.

## Extensiones propuestas

- Python/SQL como referencia; comparar C++ con tolerancias y benchmarks de convergencia antes de migrar.
- R para validación estadística independiente cuando aporte contraste.
- Notebooks: superficies de sensibilidad ECL, frontera capital-liquidez, curvas de supervivencia de caja, cola operacional y redes de contagio.
- Modelos novedosos: estrés inverso conjunto, umbrales KRI adaptativos y transmisión climática a PD/LGD; novedad pendiente de literatura y evidencia.
