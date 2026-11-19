# Evaluación de políticas con covariable observada y resultados simulados

Este ejercicio combina `LIMIT_BAL` observado del conjunto [Default of Credit Card Clients](https://doi.org/10.24432/C55S3H) de I-Cheng Yeh (2009), UCI Machine Learning Repository, **CC BY 4.0**, con asignación, propensión y utilidad **simuladas**. Los datos son 30.000 titulares de tarjeta de Taiwán, no solicitantes nuevos. La covariable describe crédito concedido, en nuevos dólares taiwaneses (NTD), no una variable demostrada disponible antes de originar. No se usa la etiqueta real de impago ni se estiman decisiones o efectos causales reales.

El archivo XLS se reutiliza sin modificación desde `01-credit-risk/credit-risk-products/scorecard-logistico-woe/observed-uci350/data/`, donde su manifiesto identifica la descarga oficial UCI del 12 de noviembre de 2026. Se verifica SHA-256 `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933`, estructura y 30.000 filas. La [ficha UCI](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients) define `LIMIT_BAL` como cupo concedido, que puede incluir crédito complementario familiar; datos de 2005. La muestra no es representativa de solicitantes rechazados ni del mercado colombiano.

## Diccionario y simulación

- `x = min(LIMIT_BAL / 1.000.000 NTD, 1)`: covariable adimensional observada transformada con truncamiento fijo, no una PD.
- `A ~ Bernoulli(0,2 + 0,6x)`: acción enteramente simulada; su probabilidad es conocida por construcción y está entre 0,2 y 0,8.
- `Y(0) = 0` y `Y(1) = 0,8x − 0,1 + ε`, `ε ~ N(0,1)`: utilidades simuladas en unidades arbitrarias. No son dinero ni outcome UCI.
- Políticas fijas antes del experimento: nunca, siempre y tratar si `x ≥ 0,125`. El umbral se deriva de la función de utilidad sintética y no representa una regla de aprobación válida.
- La verdad condicional es el promedio de las medias potenciales **simuladas** para los `x` del archivo. Las columnas DM, IPS y AIPW usan la propensión y media verdaderas del generador; no entrenan modelos. El error estándar de AIPW es una aproximación bajo independencia, no incluye incertidumbre de modelos ni selección de política.

Desde la raíz del repositorio, con `xlrd` instalado (`requirements-research.txt`):

```bash
python3 03-financial-risk/04-advanced-research/01-causal-origination-policy/semisynthetic_uci/run.py
python3 -m unittest discover -s 03-financial-risk/04-advanced-research/01-causal-origination-policy/semisynthetic_uci -p 'test_*.py' -v
```

Con semilla 42, la utilidad media verdadera condicional de la política de umbral es 0,05839 y AIPW da 0,05816 (error estándar aproximado 0,00726); la escala es arbitraria. La coincidencia es una comprobación del algoritmo frente a un mecanismo conocido, **no evidencia de precisión causal en originación**. El fichero no documenta política de aprobación, propensiones, rechazados ni desenlaces contrafactuales. Harían falta datos longitudinales, fecha de decisión, políticas históricas, desenlaces y un diseño de identificación creíble para pasar de este ejemplo a evaluación real.

## Comparación pareada de políticas

El archivo [results.json](results.json) incluye la diferencia AIPW entre la
política de umbral y tratar siempre, calculada como el promedio de la diferencia
de las contribuciones por el mismo individuo. Su error estándar usa la
desviación estándar muestral de esas diferencias dividida por √n; así conserva
la covarianza entre políticas. Con la semilla 42, la diferencia verdadera
condicional en esta muestra es 0,02440 y la estimación es 0,02139 (EE 0,00801;
intervalo normal aproximado al 95 % [0,00569; 0,03709]). Son unidades de
utilidad sintética, no una mejora económica real.

El intervalo es una aproximación IID, sin corrección por modelos de propensión
o resultados estimados, dependencia, selección de política o cambio de
población. Aquí se condiciona la verdad al vector de cupos observado, mientras
que la fórmula IID también refleja heterogeneidad entre cupos; no se interpreta
como un intervalo exacto condicionado. Las dos políticas se fijaron antes de la
evaluación y los modelos de asignación y resultado son conocidos por diseño.
