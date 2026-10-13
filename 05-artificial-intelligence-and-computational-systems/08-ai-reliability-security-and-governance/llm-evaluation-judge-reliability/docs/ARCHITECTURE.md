# Arquitectura

```mermaid
flowchart TD
  I[Ítems con dificultad] --> M[Modelos A y B<br/>acierto verdadero]
  M --> J[Juez automático<br/>TPR, TNR, sesgos]
  H[Etiquetas humanas<br/>subconjunto aleatorio] --> PPI[PPI / Rogan-Gladen]
  J --> PPI
  PPI --> CI[IC y prueba de diferencia]
  M --> PP[Comparación pareada<br/>McNemar exacto]
  PP --> SL[Rebanadas<br/>Holm / BH]
  PP --> G[Compuerta de regresión<br/>SPRT vs tamaño fijo]
  J --> AC[Acuerdo<br/>kappa, Fleiss, alpha]
```

## Decisiones de diseño

- Todo método se contrasta con una verdad conocida (cobertura exacta, simulación Monte Carlo, fórmulas cerradas).
- Las etiquetas humanas son una muestra **aleatoria**; PPI mide y resta el sesgo del juez en lugar de suponerlo constante.
- Las pruebas pareadas operan sobre los ítems discordantes; el plan de muestra se hace con la tasa de discordancia.
- Las compuertas secuenciales exigen un tope máximo de muestra.

## Límites

- Modelos logísticos de un parámetro; los reales tienen perfiles multidimensionales.
- Jueces con error constante o dependiente de la verbosidad; los reales varían con la tarea y la versión.
- PPI supone etiquetas humanas correctas y representativas; el SPRT, discordancias independientes.
