# MVP recuperado26oct, ejecutado27oct

- **Qué:** método de momentos para error clásico de medida conocido, con abstención por positividad/condición.
- **Cómo:** Python3.12, `bash run.sh`; dependencias fijadas y entorno aislado.
- **Salida:**1200datasets/4800evaluaciones, CSV/JSON, figura, notebook ejecutado, tests/cobertura e informe.
- **No cubre:** varianza desconocida, errores correlacionados, no linealidad, CI ajustados, causal discovery general o datos reales.
- **Madurez:** componenteS2, no se certifica todo el programaS3/S4/M2 ni operación.
- **Notebook:** IPython en proceso con namespace nuevo; celdas realmente ejecutadas, aborta errores. No se afirma kernel Jupyter separado.
- **Trazabilidad:** diseño26 reconstruido desde historial después de pérdida del worktree. Resultados regenerados27; no byteidentidad con archivos antiguos. PR84 corresponde a otra entrega, investigación25.

El incremento28está documentado en MVP_joint.md y se reproduce con bash run_joint.sh;no sustituye el experimento26.
