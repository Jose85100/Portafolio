# Enrutar entre modelos: costo, calidad y garantías

Enrutamiento entre modelos de distinto costo con garantías de calidad, todo simulado (sin LLM reales): cascada por confianza, enrutador aprendido, caché semántico, bandidos en línea, asignación bajo presupuesto con cota por programación lineal y **control conforme del riesgo** con garantía de muestra finita.

## Hallazgos (medidos en el notebook)

- El oráculo alcanza 88,3 % de calidad a ~26 % del costo del modelo grande: ese es el techo del enrutamiento.
- Para conservar el 95 % de la calidad del grande, la cascada ahorra ~19 % del costo (un modelo pequeño de 42 % de acierto escala mucho).
- La frontera de la cascada **casi no depende de la calibración** (solo usa el orden de las confianzas); sí importa al leer el umbral como probabilidad: con umbral 0,9 una confianza sobreconfiada declara 0,97 y entrega 0,84.
- Un enrutador aprendido iguala a la cascada con atributos informativos (AUC 0,79) y pierde con atributos pobres (AUC 0,62).
- Control conforme: el riesgo de prueba no supera ε en las 16 configuraciones validadas (calibrada y sobreconfiada); el umbral ingenuo viola el objetivo en 48 % de las repeticiones con 50 datos. Exige n ≥ 1/ε − 1 consultas de calibración.
- Caché semántico: el umbral óptimo depende del costo de una respuesta equivocada (τ* de 0,6 a 0,8 según K).
- Bandidos: UCB y Thompson tienen arrepentimiento sublineal; ε-greedy mantiene una tasa constante; sin exploración se atasca.
- La asignación bajo presupuesto queda a menos de 1 acierto esperado de la cota de la relajación lineal y supera a la cascada y al reparto aleatorio.

## Estructura

```text
src/        librería (`world`, `policies`, `conformal`, `cache`, `bandits`, `optimize`)
tests/      pruebas unitarias (unittest)
docs/       ARCHITECTURE.md (diagrama y decisiones de diseño)
notebook.ipynb   desarrollo completo con pruebas automáticas (assert) y lecturas calculadas desde los datos
main.py     demostración corta
```

## Cómo ejecutar

```bash
python3 main.py                              # demostración corta
python3 -m unittest discover -s tests        # pruebas unitarias
python3 -m unittest tests.test_notebooks     # (desde la raíz del repo) ejecuta los notebooks
```

## Datos

Simulación con semilla fija y verdad conocida; sin datos reales ni confidenciales.

## Límites

- Todo es simulado: habilidades, costos y confianzas son supuestos.
- El control conforme supone intercambiabilidad calibración–producción; con deriva se pierde la garantía.
- Los bandidos no usan contexto; el caché usa embeddings sintéticos.
