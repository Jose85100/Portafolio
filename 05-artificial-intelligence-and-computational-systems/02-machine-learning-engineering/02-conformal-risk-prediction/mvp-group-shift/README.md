# Conformal Prediction Under Shift — M2

Prototipo ejecutable de cobertura predictiva por grupo. **No operacional.**

Comando único desde esta carpeta: `bash reproduce.sh`.

El script instala numpy y pytest, ejecuta los tests y escribe `results/raw.csv`. El experimento usa 30 seeds, cuatro regímenes y dos métodos: split conformal global (baseline) y Mondrian por grupo. Produce 240 registros pareados. Train/cal/test = 400/400/800. Alpha=0.1. OLS se ajusta solo en train. Grupo 0 tiene sigma=.5, grupo 1 sigma=2.5. El shift condicional multiplica el ruido del grupo 1 por 1.7 en test. En grupo escaso se usa fallback global si hay menos de 25 ejemplos de calibración.

Esta rama contiene una versión compacta del motor. El paquete ZIP local incluye una evaluación ampliada de cuatro métodos, notebook y figura; no confundir las 240 corridas de esta rama con las 480 del paquete ampliado.
