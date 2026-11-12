# IDEAM: catálogo de estaciones candidatas

## Resultado

Se incorporó un snapshot del [Catálogo Nacional de Estaciones IDEAM](https://www.datos.gov.co/d/hp9r-jxuu), descargado el 11 de noviembre de 2026 desde el recurso público `hp9r-jxuu`. El archivo contiene 10.000 filas; se removieron 132 filas exactamente duplicadas y no quedaron códigos duplicados en el ranking. La página institucional describe 9.685 estaciones, por lo que la diferencia entre el conteo publicado y la descarga requiere aclaración antes de tratar el snapshot como inventario completo. SHA-256 del CSV: `e377d9b8644ff2f1c720296d55a4534544f02a50eba88e45422c97d39de13095`.

El catálogo permite ubicar estaciones pluviométricas, pluviográficas y climatológicas candidatas. Entre las diez ciudades de referencia, el catálogo marca activas las candidatas más cercanas a Barranquilla, Bogotá, Bucaramanga, Cartagena, Medellín y Villavicencio; las más cercanas a Barrancabermeja, Cali, Neiva y Pasto aparecen suspendidas. Son distancias a centroides urbanos aproximados, no a predios ni zonas agrícolas. No se obtuvieron observaciones históricas de lluvia.

## Uso y controles

Requisitos: Python 3, `pandas` y `numpy`.

```bash
python3 03-financial-risk/01-credit-risk/credit-portfolio-strategy/climate-parametric-pricing/observed-ideam-station-catalog/analyze_station_catalog.py
```

El script remueve duplicados exactos, verifica campos y coordenadas, identifica categorías relacionadas con precipitación y ordena las cinco estaciones más cercanas por ciudad. La fecha de instalación/suspensión y estado provienen del catálogo; no prueban que la variable, frecuencia, aprobación o cobertura diaria requerida esté disponible.

## Alcance y límites

Este es un inventario espacial oficial, **no una serie meteorológica ni una validación del índice paramétrico**. Distancia no equivale a representatividad: relieve, microclima, ubicación del asegurado, cambios instrumentales, datos faltantes y consistencia temporal deben evaluarse con las observaciones y metadatos de cada estación. El snapshot fue limitado a 10.000 filas por la consulta; la cifra no se presenta como censo completo.

La vía oficial para series y descargas por estación es [DHIME](https://www.ideam.gov.co/dhime). IDEAM también ha publicado un ZIP nacional diario, pero ese enlace agotó tiempo de espera en esta sesión; no se registró archivo, hash ni resultados. La lista de candidatos sirve para preparar una solicitud DHIME concreta por estación/periodo, no para reemplazarla.

Para validar aplicación actuarial siguen faltando coordenadas de exposición, series IDEAM fechadas con banderas de calidad e historial instrumental, daños/pagos y criterios acordados de evaluación de riesgo de base. Por eso no se estima frecuencia de trigger, prima ni eficacia crediticia.

## Artefactos

- `data/ideam_station_catalog_2026-11-11.csv`: snapshot de catálogo, sin datos de clientes.
- `results/nearest_candidate_stations.csv`: cinco candidatas más próximas a cada centro urbano aproximado.
- `results/catalog_quality_manifest.json`: origen, hash, reglas, conteos y límites.
- `analyze_station_catalog.py`: análisis reproducible del snapshot.
