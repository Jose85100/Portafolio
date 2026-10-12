# Laboratorio multilenguaje de ingeniería cuantitativa

Implementaciones comparables de pérdida esperada de crédito, con un contrato numérico común en Python, C, C++, R, MATLAB/Octave y Julia. El objetivo es demostrar **POO, diseño de interfaces, programación numérica, pruebas cruzadas y reproducibilidad**, no sostener que un lenguaje sea intrínsecamente superior.

## Contrato matemático compartido

Para exposiciones con PD, LGD y EAD deterministas y una única fecha de reconocimiento:

\[
EL=\sum_{i=1}^{N}PD_i\,LGD_i\,EAD_i.
\]

Los valores deben ser finitos; \(0\le PD,LGD\le1\), \(EAD\ge0\). Todos los programas calculan la misma función **ilustrativa**. No es por sí sola una medición IFRS 9 completa: faltan horizonte temporal, cash shortfalls, descuento, escenarios, staging y tratamientos de producto.

Vector de prueba común:
- Exposición A: PD=0.02, LGD=0.4, EAD=1000 -> EL=8
- Exposición B: PD=0.05, LGD=0.6, EAD=2000 -> EL=60
- Exposición C: PD=0.10, LGD=0.3, EAD=500 -> EL=15
- **EL total = 83** (unidades monetarias arbitrarias).

## Arquitectura

- \`python/model.py\`: dataclasses, interfaz abstracta, motor de cálculo y validaciones.
- \`c/main.c\`: structs, punteros, validación y acumulación numérica.
- \`cpp/main.cpp\`: clases, interfaz abstracta, RAII y polimorfismo.
- \`r/main.R\`: validación vectorial, análisis estadístico y prueba determinista.
- \`matlab/main.m\`: implementación matricial vectorizada compatible con MATLAB/Octave.
- \`julia/main.jl\`: tipos paramétricos, despacho múltiple y validación.

## Ejecución

\`\`\`bash
python3 python/model.py
python3 -m unittest discover -s python -p 'test_*.py' -v
cc -std=c11 -O2 -Wall -Wextra -pedantic c/main.c -lm -o /tmp/quant_el_c && /tmp/quant_el_c
c++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/main.cpp -o /tmp/quant_el_cpp && /tmp/quant_el_cpp
Rscript r/main.R
octave --quiet matlab/main.m
# o desde MATLAB: run('matlab/main.m')
julia julia/main.jl
\`\`\`

Se requieren intérpretes/compiladores instalados. No se garantiza disponibilidad de MATLAB comercial; Octave permite ejecutar el ejemplo matricial.

## Criterios de equivalencia y benchmark

Cada implementación debe arrojar EL=83, con tolerancia absoluta 1e-10. Para comparar rendimiento: usar los mismos arreglos de entrada, excluir carga de intérprete, ejecutar calentamiento y repeticiones, medir memoria y tiempo con herramientas apropiadas, e informar compilador, flags, BLAS, CPU y versión. No comparar una implementación vectorizada con otra que incluye lectura de archivos. El rendimiento no se ha medido en esta entrega.

## Evolución

1. Extender contrato con hazard discreta y PD marginales.
2. Añadir flujos descontados y escenarios macro.
3. Exponer núcleo C++ como librería con bindings a Python y R, solo si la medición de rendimiento justifica la complejidad.
4. Incorporar simulación Monte Carlo reproducible con pruebas estadísticas, no exigir igualdad exacta entre generadores aleatorios de lenguajes diferentes.
5. Ejecutar integración continua con matriz de compiladores e intérpretes.
