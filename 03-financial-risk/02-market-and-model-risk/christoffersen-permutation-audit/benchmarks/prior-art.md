# Estado del arte y alcance de novedad

- Kupiec (1995) introduce cobertura incondicional basada en proporción de fallos.
- Christoffersen (1998) separa cobertura incondicional e independencia y las combina en cobertura condicional.
- Christoffersen y Pelletier (2004) muestran baja potencia en muestras realistas y proponen tests de duración.
- Dufour (2006) formaliza tests Monte Carlo con parámetros molestos.
- Campbell (2007) revisa backtesting y sus limitaciones.
- Santos y Alves (2009) señalan que la distribución exacta de tests de independencia no está disponible en el
  esquema usual y construyen un test exacto con una alternativa ordenada específica.
- Pajhede (2015) documenta que Markov-1 queda subdimensionado para p=1% y usa técnica Monte Carlo para corregir
  tamaño en comparaciones de potencia.
- BCBS (1996) vincula backtesting con precisión de modelos internos, pero el semáforo por conteo no diagnostica
  dependencia temporal.

No se afirma prioridad académica. La novedad defendible es incremental y específica del repositorio: implementar
y contrastar, con el mismo estadístico ya usado allí, qué ocurre al condicionar en el conteo y tratar o no los
empates discretos. La ablation aleatorizada hace explícito el precio operativo de obtener tamaño nominal.
