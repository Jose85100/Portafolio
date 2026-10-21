# Quadratic Root Certificate

MVP reproducible para encerrar con racionales exactos las raíces de las ecuaciones cuadráticas que aparecen por régimen en los MVP de ventas forzadas y clearing acoplado.

## Reproducción en un comando

Desde la raíz del repositorio, con Python 3.12, Linux y acceso a PyPI:

```bash
bash 01-economics-and-econometrics/computational-economics/numerical-validation/quadratic-root-certificate/reproduce.sh
```

El comando crea un entorno aislado, fija dependencias, ejecuta Ruff, mypy estricto, tests con cobertura, la suite común, benchmarks y el notebook. Produce CSV, JSON, logs y `results/comparison.png`.

## Pregunta e hipótesis

¿Una envolvente racional especializada recupera raíces simples y dobles que una fórmula flotante o una malla de cambios de signo no certifica? Hipótesis falsable: 100/100 casos racionales deben quedar encerrados, ancho máximo ≤1e-24 a 24 dígitos, y la raíz doble de 0,5 debe recuperarse aunque una malla 0,01 tenga cero cambios de signo.

## Madurez

- Componente de certificación cuadrática: **S2** (código, tests, baseline y resultados reproducibles).
- Infraestructura `computational-economics`: **S2 parcial**; la arquitectura completa no asciende a S3.
- Programas de macrofinanzas consumidores: permanecen **S2 parcial**. El certificado polinómico no prueba por sí solo la admisibilidad económica ni la completitud del equilibrio.

Véanse [MVP.md](MVP.md), [informe.md](informe.md) y [referencias.bib](referencias.bib).
