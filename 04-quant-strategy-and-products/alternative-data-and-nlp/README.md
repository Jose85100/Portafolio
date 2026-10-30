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

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Keywords/sentiment genérico de documentos.** Base: Extracción temporal de cambios en guía, riesgo y demanda con trazabilidad textual. **Innovación a probar:** Evaluación humana etiquetada y señal incremental sobre sorpresa numérica convencional. **Prueba decisiva:** undefined
- **2. Indicadores oficiales rezagados sin texto.** Base: Texto de alta frecuencia integrado en modelo mixto con disponibilidad archivada. **Innovación a probar:** Validar nowcast pseudo-real-time contra modelo oficial-only; controlar revisiones y cobertura. **Prueba decisiva:** undefined
- **3. Fundamentales cuantitativos sin señales de revisión textual.** Base: Cambios semánticos de expectativas junto a sorpresas fundamentales. **Innovación a probar:** Ablation debe probar incrementalidad neta de costos frente a consenso/resultados base. **Prueba decisiva:** undefined
- **4. Mapa de proveedores estructurado y estático.** Base: Grafo de exposición extraído de texto con confianza y validación manual. **Innovación a probar:** Medir precisión/recall y utilidad ante shocks frente a mapa estructurado incompleto. **Prueba decisiva:** undefined
- **5. Monitoreo de métricas promedio de modelo.** Base: Auditoría de deriva por fuente, periodo, sector, lenguaje y subgroup pertinente. **Innovación a probar:** Medir detección temprana y falsos positivos; comprobar qué intervención corrige deriva. **Prueba decisiva:** undefined
