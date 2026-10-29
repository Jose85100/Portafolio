# Tres ideas y revisión focal — 29 de octubre de 2026

| Idea | Aporte | Decisión |
|---|---|---|
| Fondeo contingente de liquidez | Añadir capacidad/coste a ciclos27/28 | Necesita política y más supuestos |
| Stress de factor de crédito | Continuar dependencia25/26 | Repite dominio reciente de cartera |
| Default y prepago como salidas competidoras | Separar incidencia y PD condicional en pérdida de vida | Seleccionada:12períodos, oráculo racional y código mínimo |

Main022f6bd y PR abiertos0 antes de la publicación accidental del duplicado99 (cerrado, no cuenta como29). Se inspeccionaron README de productos y pd_lifetime/ecl_componentes del engineIFRS existente. Ese engine declara buckets anuales y una aproximación sin prepago explícito: NO se afirma bug o implementación contable incorrecta. El baseline de esteMVP es el caso sin prepago y mismo calendario; una hipótesis contrafactual válida, pero no la incidencia conjunta cuando sí hay salida competidora.

Cinco referencias reales verificadas por títulos/autores/DOI en fuentes primarias o registros bibliográficos oficiales: Deng2000Wiley/Wharton (default y prepago conjuntos); Putter2007Wiley (multiestado); Austin2016PubMed con abstract recuperado; Andersen2012OUP/PubMed indexados; Fine/Gray1999editorial indexada. PMC/eScholarship presentaron controles automáticos y algunos enlacesOUP/Wiley no abrieron: no se afirma lectura íntegra. Putter fue online2006 y aparece en volumen2007. Novedad local, no revisión exhaustiva ni teoría nueva.

Literatura de supervivencia aporta identidades generales, no recomendaciones médicas ni evidencia de crédito. No ajustamos Fine-Gray, Cox, opciones de hipoteca o datos censurados. Se usan probabilidades discretas suministradas, no intensidades continuas ni coeficientes de subdistribución. Deng demuestra pertinencia del problema, no valida nuestros parámetros sintéticos.
