# Guard de contaminación de calibración KYC

Una referencia de supuestos inliers puede contener scores bajos manipulados: el rango ordinario diluye la cola y aumenta falsas alertas. Este MVP añade una envolvente conservadora con una **cota externa válida** del número de contaminantes. No estima esa cota ni detecta fraude.

## Reproducir — Python 3.12
```bash
bash run.sh
```
Instala dependencias directas fijadas y ejecuta tests, cobertura, Ruff, mypy estricto del núcleo, benchmark y notebook. Alternativa con entorno listo: `SKIP_INSTALL=1 bash run.sh`. El comando crea .venv con acceso a paquetes existentes y selecciona el intérprete aislado (PYTHON permite elegir otro); dependencias transitivas no totalmente bloqueadas. Notebook ejecutado realmente, secuencialmente con IPython en proceso y outputs capturados; no depende de kernel ZeroMQ. Figura separada inspeccionada; no se afirma render de HTML completo.

## Resultados sintéticos
80 semillas, referencia n499, 199 scores contaminados bajos (39,88%). FPR rango ordinario **8,346%**, guard **5,007%**. Detección **89,578%→84,740%**: robustez cuesta potencia. Si la cota subestima (99 frente a199), FPR guard **6,763%**; el supuesto importa. Contaminación de scores100 reduce ambas detecciones a cero. En limpio, usar cota199 conservadora reduce FPR5,018%→3,091% y detección84,877%→79,543%.

Consulta `informe.md` para los14 puntos, prueba de dominación, errores estándar entre semillas, limitaciones y rúbrica; `results/` contiene1.280 filas crudas, métricas/figura y rendimiento n100/1000/10000; `referencias.bib` contiene5 fuentes primarias verificadas.

Madurez: prototipo sintético verificable de componente, con revisión independiente del ciclo separada; no se certifica todo el especialista ni operación real. No sustituye validación temporal o adjudicación humana.
