# Brecha de datos: reservas por calidad y garantías

**Corte de revisión:** 2026-11-11. **Estado:** companion público reproducible de sanciones administrativas disponible; aún no hay base de reclamaciones de garantía, pagos y pérdidas por proyecto.

## Señal oficial disponible

La [SIC informó](https://sedeelectronica.sic.gov.co/comunicado/comunicado-de-interes-sobre-la-proteccion-de-los-derechos-de-las-y-los-consumidores-en-proyectos-de-vivienda-nueva) 2.818 denuncias y 3.255 demandas relacionadas con presuntas vulneraciones a consumidores de vivienda nueva, recibidas entre enero de 2024 y octubre de 2025. Entre los motivos mencionó fallas de garantía, como humedades, fisuras y problemas estructurales, además de retrasos de entrega y otros incumplimientos.

El comunicado no separa el número correspondiente a garantía, no describe si denuncia y demanda corresponden a casos distintos, ni ofrece llave de proyecto, unidades expuestas, edad del inmueble, severidad, costo de reparación o indemnización pagada. Por ello, las cifras sirven únicamente como señal de actividad agregada de protección al consumidor. No son reclamaciones actuariales ni se usan para calibrar o validar reservas.

El dataset [Sanciones impuestas en firme por la SIC](https://www.datos.gov.co/Comercio-Industria-y-Turismo/Sanciones-impuestas-en-firme-por-la-SIC/73dx-n59j) sí permite un corte reproducible del sector `Inmuebles`. El [companion](observed-sic-real-estate-sanctions/README.md) resume filas y resoluciones únicas, y marca conductas con la palabra “Calidad” mediante una regla explícita. La clasificación sectorial/conductual no identifica defectos cubiertos por garantía, proyectos ni daños, y no tiene denominador de viviendas entregadas. No se agregan montos de sanción ni se interpretan como indemnizaciones o reservas.

## Datos mínimos para una aplicación reproducible

1. Reclamación/defecto con identificador de caso y proyecto seudonimizado; tipo, fecha de entrega, fecha de reporte, etapa de resolución y derechohabiente deduplicado.
2. Unidades entregadas y años-unidad expuestos por proyecto, tipología y cohorte de entrega.
3. Costos incurridos y pagados de inspección, reparación, indemnización, litigio y recuperación, con fecha y moneda.
4. Estado de desarrollo del reclamo, cierres, reaperturas, reservas y pagos tardíos para estimar IBNR sin sesgo de censura.
5. Permiso de uso, definiciones, conciliación con contabilidad y validación independiente sobre cohortes fuera de tiempo.

Una futura validación tendría que contrastar triángulos de desarrollo, frecuencia y severidad contra reservas y pagos observados, realizar pruebas de sensibilidad de inflación y maduración, y fijar criterios de aceptación antes de uso. El agregado público de la SIC no cumple esos requisitos.
