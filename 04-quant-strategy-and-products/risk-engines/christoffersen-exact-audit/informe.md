# Informe crítico — oracle exacto de independencia

## Pregunta e hipótesis

¿Puede un baseline de 999 permutaciones cambiar una decisión al 5% únicamente por la semilla cuando el p-valor
condicional verdadero está cerca del umbral? La hipótesis exigía al menos un desacuerdo en 200 semillas frente a
un oracle que enumera todas las ubicaciones posibles de cuatro excepciones en 30 días.

## Diseño y supuestos

El estadístico es el `LR_ind` de primer orden de Christoffersen. Bajo la nula condicional, las `k` posiciones son
equiprobables dado el total de excepciones. El programa enumera `C(30,4)=27.405` configuraciones, selecciona el
escalón discreto más próximo a 5% y calcula la masa `LR >= LR_observado`. El baseline muestrea 999 permutaciones,
usa `(extremos+1)/(B+1)` y repite semillas 1–200.

## Resultados ejecutados

| Medida | Resultado |
|---|---:|
| Estados exactos | 27.405 |
| LR observado | 1,369532 |
| p-valor exacto conservador | 4,2146% |
| mid-p, ablation | 4,0777% |
| Desacuerdos Monte Carlo | **32/200 (16%)** |
| Error absoluto MC máximo | 1,8854 puntos porcentuales |
| Tiempo exacto | 2.421 µs |
| Tiempo MC por semilla | 201 µs |
| Pico RSS del proceso auditado | 58.468 KiB |

La enumeración fue aproximadamente 12,0 veces más lenta que una corrida Monte Carlo de 999 muestras, pero elimina
el error de muestreo en este dominio. La memoria es el pico del proceso completo, no una atribución causal separada
por método; el oracle conserva las 27.405 secuencias durante la selección de frontera.

## Fallos y ablations negativas

La primera prueba asumía que tres hits consecutivos siempre producían mayor LR que tres hits regularmente
separados en solo diez días. Falló: la separación excesivamente regular también es dependencia. Se amplió el caso
a 30 días y cuatro hits; el fallo original no se oculta.

El mid-p reduce el p-valor de 4,2146% a 4,0777%. Puede aliviar conservadurismo, pero ya no es el p-valor conservador
que cuenta toda la masa empatada. No se recomienda intercambiarlos silenciosamente.

## Calidad y verificación

CTest, 12 assertions C++ y ASan/UBSan pasaron. GCC 13.3 compiló con `-Wall -Wextra -Wpedantic -Wconversion
-Werror`. Cobertura del header: 91,16% de líneas; 92,41% de ramas ejecutadas y 68,35% tomadas al menos una vez.
Ruff, formato y mypy pasaron para el benchmark Python. `clang-tidy` no estaba instalado en el host; se declara como
limitación y el comando conserva la comprobación cuando la herramienta está disponible.

## Límites y riesgos de modelo

- `n=30, k=4` es un oracle de ingeniería, no una ventana regulatoria típica.
- El coste combinatorio impide enumerar directamente `C(250,k)`; se impone un máximo de cinco millones de estados.
- Solo prueba independencia de primer orden y condiciona en el conteo; no prueba cobertura incondicional.
- No incorpora estimación del VaR, datos reales, horizontes solapados ni severidad de pérdidas.
- Los desacuerdos se buscan deliberadamente cerca de 5%; no estiman su frecuencia en un portafolio real.
- `std::mt19937_64` asegura repetibilidad local del baseline, no identidad garantizada entre todas las bibliotecas.
- El pico RSS incluye C++ y carga del entorno; falta una medición aislada de memoria por algoritmo.

## Conclusión

La hipótesis se sostuvo: 32 de 200 semillas invirtieron la decisión exacta. El resultado no invalida Monte Carlo;
demuestra que una sola semilla y 999 réplicas son insuficientes para decisiones próximas al umbral. El oracle exacto
es útil como fixture pequeño para probar aproximaciones, no como motor general para ventanas grandes.
