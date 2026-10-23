# Firmas de nivel 2: auditoría de orden y aliasing

**Estado S2 acotado**: el programa 13 pasa de diseño a un prototipo para caminos poligonales finitos. No es un sistema de detección de dinámicas ocultas validado.

Desde esta carpeta, Python 3.12:

```bash
bash run.sh
```

El comando instala dependencias fijadas, ejecuta lint, tipos, tests con cobertura, benchmark y notebook. El notebook se ejecuta realmente con IPython en proceso: el entorno restringe sockets del kernel Jupyter. No se simulan outputs; el ejecutor aborta ante cualquier error de celda. En un entorno con sockets el cuaderno también puede ejecutarse con Jupyter convencional.

## Qué aporta

El README previo planteaba comparar trayectorias con iguales marginales y distinto orden. Ahora hay recurrencia tensorial de nivel 2, composición de Chen, oráculo shoelace independiente y auditoría de aliasing. La contribución es evidencia reproducible local; la fórmula y propiedades son conocidas.

800 trayectorias (400 pares reversos), semilla 422: sin ruido, firma 100% frente a 50% endpoint/momentos. Con ruido 1.0 baja a 70%. El error máximo contra shoelace fue 1.07e-14; el error geométrico al aproximar un círculo converge con orden 1.99987. Dos vueltas observadas en cuatro segmentos tienen área 0 frente a 6.28066 con 256 segmentos.

- [Notebook ejecutado](notebook.ipynb): explicación, ecuaciones y salidas.
- [Informe de 14 puntos](informe.md): diseño, resultados negativos, rúbrica y límites.
- `src/signatures.py`: API tipada; `tests/`: identidades y edge cases.
- `results/`: réplicas CSV, convergencia, recursos, cobertura y figura.
- [Referencias](referencias.bib) y [verificación de fuentes](fuentes.md).

El área shoelace iguala numéricamente a la firma y es más eficiente para área planar. No hay ventaja alegada sobre bibliotecas C++ optimizadas, ni aprendizaje supervisado, reconstrucción, datos operativos o validación externa. EL=83 no aplica a este componente; no se modifica quant-libraries.
