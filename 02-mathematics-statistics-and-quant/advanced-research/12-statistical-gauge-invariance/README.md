# Statistical Gauge Invariance — certificado S2 para factorización rango uno

**Estado: S2 (prototipo ejecutable y sintético).**

Pregunta: ¿puede un certificado espectral de la información de Fisher reconocer automáticamente la no identificabilidad por escala en `M = u vᵀ`, distinguirla de degeneraciones adicionales y eliminar la inestabilidad paramétrica sin cambiar la predicción?

El MVP implementa el Jacobiano analítico, la Fisher gaussiana, el vector tangente gauge `(u,-v)`, un certificado de nulidad, una sección canónica balanceada obtenida por SVD y un baseline de diferencias finitas. El benchmark usa matrices sintéticas completamente observadas; no afirma resolver simetrías desconocidas ni modelos de rango mayor.

## Reproducción completa

Desde esta carpeta:

```bash
make run
```

El comando crea `.venv`, instala dependencias fijadas, ejecuta tests/cobertura/lint/tipos, benchmark, figura, notebook y auditoría de artefactos. Las salidas verificables quedan en `benchmarks/` y el análisis crítico en `informe.md`.

También puede reproducirse con contenedor:

```bash
docker build -t gauge-certificate . && docker run --rm gauge-certificate
```

## Alcance matemático

Con ruido gaussiano iid de varianza conocida, `J(u,v)(u,-v)=0`. Si `u` y `v` son no nulos, `rank(J)=m+n-1`: hay exactamente una dirección infinitesimal no identificable. El certificado numérico comprueba esa proposición; el caso degenerado `u=0` se rechaza porque su nulidad excede uno.

## Estructura

- `src/gauge.py`: núcleo tipado y certificado.
- `src/benchmark.py`: simulación, baseline y resultados crudos.
- `tests/`: propiedades, casos límite y regresiones.
- `config.json`: diseño preespecificado, semillas y umbrales.
- `benchmarks/`: CSV/JSON, figura, logs, cobertura y entorno.
- `notebook.ipynb`: análisis ejecutado de punta a punta.
- `informe.md`, `MVP.md`, `referencias.bib`, `fuentes.md`: evidencia y límites.

No se reclama novedad algorítmica: la contribución es una formalización verificable y repo-específica que conecta simetría, nulidad de Fisher y gauge fixing.
