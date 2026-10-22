# Oracle exacto para la independencia de excepciones VaR

MVP C++17 que enumera todas las secuencias binarias con `n` y número de excepciones fijos, calcula la distribución
condicional exacta del `LR_ind` de Christoffersen y audita un baseline Monte Carlo. Complementa, sin reemplazar,
el laboratorio Python `03-financial-risk/.../christoffersen-permutation-audit`.

## Un comando

Requiere Linux, Python 3.12, GCC, CMake, clang-format, clang-tidy y gcov:

```bash
./run.sh
```

El comando instala dependencias, ejecuta lint/tipos, compila, corre CTest, ASan/UBSan, cobertura, benchmark y
genera `results/run.json` y `results/audit.png`.

## Hipótesis

Para una secuencia situada cerca del umbral exacto de 5%, 999 permutaciones Monte Carlo pueden cambiar la decisión
entre semillas. La enumeración elimina error Monte Carlo en dominios combinatoriamente pequeños a cambio de mayor
tiempo de ejecución. Éxito: demostrar al menos un desacuerdo entre 200 semillas y cuantificar coste/error.

## Alcance y contrato

- Dominio benchmark: `n=30`, cuatro excepciones, `C(30,4)=27.405` estados.
- Oracle: p-valor conservador, masa `LR >= LR_observado`.
- Ablation: mid-p, que divide los empates y no conserva la misma garantía de nivel.
- Baseline: 999 permutaciones con corrección `(b+1)/(B+1)` y `std::mt19937_64`.
- Límite defensivo: máximo cinco millones de estados exactos.

No se afirma novedad matemática ni validez regulatoria. El objetivo es una referencia pequeña para validar motores
aproximados y detectar decisiones sensibles a la semilla.
