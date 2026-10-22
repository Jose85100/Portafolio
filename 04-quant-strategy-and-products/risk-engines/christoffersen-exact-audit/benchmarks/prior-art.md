# Prior art y alcance

Christoffersen (1998) define cobertura condicional y el LR de independencia. Dufour (2006) estudia tests Monte
Carlo con parámetros molestos. Phipson y Smyth explican por qué un p-valor basado en permutaciones muestreadas no
debe reportarse como cero. Santos y Alves (2009) proponen otro test exacto de independencia con alternativa de
clustering ordenada. Pajhede (2015) documenta distorsiones finitas para Markov-1 y emplea calibración Monte Carlo.

Este MVP no reproduce el test de Santos–Alves ni reclama prioridad. Enumera la distribución condicional del mismo
`LR_ind` implementado ayer en Python, para crear un oracle C++ pequeño y medir sensibilidad a semillas.
