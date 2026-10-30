# Datos alternativos y NLP financiero

Uso de textos y fuentes alternativas para medir información económica y financiera. Esta carpeta estudia construcción de variables, validación y aporte incremental; no asume que más datos produzcan mejores decisiones.

## Cinco ideas

1. **Extracción de sorpresas en reportes corporativos**
   - Identificar cambios en guía, riesgos, demanda, márgenes y lenguaje frente al reporte anterior.
   - Combinar extracción estructurada con embeddings o clasificadores y evaluar señal en ventanas de evento sin usar texto publicado después.

2. **Nowcast de actividad a partir de textos y anuncios**
   - Construir indicadores de demanda, inversión, empleo o precios desde comunicados, vacantes y noticias económicas.
   - Contrastar con estadísticas oficiales usando vintages, cobertura geográfica y retrasos de publicación.

3. **Señal cuantamental de revisiones de expectativas**
   - Combinar métricas contables y de mercado con cambios textuales en expectativas de analistas o empresas.
   - Medir información incremental frente a señales financieras básicas y controlar sesgo de cobertura y supervivencia.

4. **Índice de riesgo de cadena de suministro**
   - Extraer menciones de escasez, proveedores, logística y concentración en reportes públicos para mapear exposición por sector.
   - Verificar contra eventos observados y construir intervalos de confianza por baja frecuencia o ambigüedad textual.

5. **Auditoría de sesgo y deriva en señales textuales**
   - Medir cómo cambian vocabulario, fuentes y desempeño del modelo en periodos de crisis, cambios de idioma o sector.
   - Comparar reglas transparentes y modelos NLP; registrar procedencia, derechos de uso y pruebas de fuga de información.

## Salvaguardas metodológicas

Guardar fecha de publicación y captura, deduplicar documentos, separar entrenamiento y evaluación temporalmente, probar contra un benchmark sin texto y revisar permisos de uso. No inferir identidad ni atributos sensibles.
