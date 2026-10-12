# Fundamento I — Matemático y teórico: Seguros, clima y conducta

**Tipo:** fundamento; no proyecto. Complementa el [índice de bases](README.md).

## Objeto y construcción formal

R=Σ_t v^t E[C_t|F0]; Cov(L_i,L_j)=σ_iσ_j C(d_ij;θ).

Para cada variable aleatoria especificar espacio de probabilidad (Ω,F,P), filtración (F_t), horizonte, unidad y mecanismo de observación. Para problemas de pricing separar medida histórica P y neutral al riesgo Q. Identificar las variables de decisión, restricciones y función objetivo.

## Resultados que deben demostrarse

1. Condiciones de integrabilidad, existencia y unicidad cuando correspondan.
2. Monotonicidad, convexidad o contraejemplos cuando fallen.
3. Dependencia entre riesgos y efectos de diversificación sin doble conteo.
4. Sensibilidad a supuestos, identificación estructural y cambio de régimen.
5. Diferencia entre identidades exactas, aproximaciones y hipótesis empíricas.

## Caso de prueba

Derivar un caso analítico sencillo, construir un contraejemplo al relajar un supuesto y registrar unidades y tolerancias de comparación con la implementación. No atribuir una prueba a una fórmula meramente enunciada.

## Conexión

Esta base alimenta los [siete proyectos](../README.md), el fundamento estadístico y el computacional. **Estado:** documentación metodológica; pruebas matemáticas especializadas por proyecto pendientes.
