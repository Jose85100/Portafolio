# MVP

- Qué es: broker read-only de prueba con grant de directorio anclado y esquema/cap de lectura externos al modelo.
- Corre: `bash run.sh` en Linux/Python 3.12 con pip, desde esta carpeta.
- Produce: 10 tests, 288 solicitudes en CSV, tres resúmenes, figura SVG y notebook de cuatro celdas ejecutado; cinco referencias técnicas verificadas.
- No cubre: LLM/prompt injection natural, red, writes, mounts hostiles, cambios de contenido, raíz no confiable, hardlink races, multi-tenant auth ni sandbox productivo.
- Coste de utilidad: rechaza symlinks internos legítimos; no se presenta como false-deny cero.
- Madurez: componente S1→S2; revisión local no equivale a plataforma operacional. El programa amplio sigue parcial.
