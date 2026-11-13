# Corrección de momentos de un proxy ruidoso

**Recuperación de investigación26oct2026; reconstrucción y ejecución27oct2026.** El worktree original26 no sobrevivió al cambio de sesión. Se reconstruyó el método desde el historial visible y se regeneraron resultados; no se afirma restauración byteporbyte ni se cuenta como investigación nueva27.

```bash
bash run.sh
```

Desde esta carpeta, Python3.12. El comando crea entorno aislado con pins, ejecuta lint/tipos/tests/cobertura,4800evaluaciones y notebook con outputs reales. `MATH_ENV` elige otro entorno. No requiere datos remotos.

El MVP25 mostró que un proxy ruidoso no elimina confusión. Aquí se resta una **varianza de error conocida externamente** de la covarianza del proxy y se resuelve un sistema2x2. Se abstiene si la matriz corregida es incompatible o está mal condicionada. El gate usa correlación y es invariante a unidades; no valida el supuesto externo.

Resultados regenerados: n2000,β0,RMSE≈.10082 frente a≈.55987 de OLSproxy sobre las mismas200réplicas aceptadas. Con n100 empeora:RMSE≈.95119 frente a≈.56957 y15abstenciones. La varianza maldeclarada produce sesgo persistente o abstención.

- [Notebook ejecutado](notebook.ipynb), [informe14puntos](informe.md), [fuentes](fuentes.md), [BibTeX](referencias.bib).
- `src/`, `tests/`, `config.json`, `results/` con CSV/JSON/figura y logs.

Comparaciones condicionales a aceptación; se usa el mismo subconjunto para baselines. Abstenciones se informan aparte, sin convertirlo en riesgo operativo incondicional. No se emiten CI/p-valores ajustados. El oráculo Z observado utiliza información privilegiada. ComponenteS2 sintético, sin validación externa; EL83 no aplica.

## Incremento nuevo28oct2026:PSD conjunto

`bash run_joint.sh` comprueba la covarianza latente completa,además del bloque de regresores. En18casos poblacionales,el gate anterior acepta cuatro matrices imposibles y el conjunto ninguna. Una varianza falsa compatible sigue pasando: no se interpreta aceptación como causalidad. [Notebook nuevo](notebook_joint.ipynb),[informe14puntos](informe_joint.md),[alcance](MVP_joint.md),[fuentes reabiertas](fuentes_joint.md). El intervalo27sin entregaGit no se reconstruye ni cuenta como entregado.
