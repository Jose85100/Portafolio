# Consulta dirigida de prior art — 2026-10-20

No se declara revisión sistemática de arXiv, SSRN, Semantic Scholar, Papers with Code, NIST, JMLR, Annals y SIAM en su totalidad. Se eligieron fuentes primarias pertinentes a geometría categórica y validez de permutaciones; no se afirma novedad algorítmica.

| Referencia | Fuente primaria consultada | Alcance |
|---|---|---|
| Miyamoto et al., v3 2024 | https://arxiv.org/abs/2304.14885v3 y https://arxiv.org/html/2304.14885v3 sección 3.5 | Autores, versiones, fórmula categórica, esfera de radio 2 y relación con el modelo multinomial. DOI de publicación relacionado 10.1007/s41884-024-00143-2; se cita explícitamente la versión arXiv consultada. |
| Lafferty–Lebanon, 2005 | https://jmlr.org/papers/v6/lafferty05a.html | Autores, título, volumen 6, páginas 129–163 y abstract sobre geometría multinomial; no se declara reproducir sus kernels ni resultados de clasificación. Exportación BibTeX falló; los datos se tomaron de la página editorial. |
| Phipson–Smyth, 2010 | https://arxiv.org/abs/1603.05766 y https://arxiv.org/html/1603.05766v1 | Texto de autores, artículo 39, DOI 10.2202/1544-6115.1585. Se distingue publicación 2010, corrección 2011 y subida arXiv 2016. Ajuste de p-valores para sorteos de permutaciones. |
| Hemerik–Goeman, v3 2018 | https://arxiv.org/abs/1411.7565v3 y https://arxiv.org/html/1411.7565v3 | Marco de transformaciones aleatorias e hipótesis de intercambio; DOI relacionado y publicación online 2017. No se confunde remuestreo IID de datos originales con permutación de etiquetas. |
| SciPy 1.17.0 | https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.stats.chi2_contingency.html | Baseline Pearson, grados de libertad y opción de remuestreo. Los tests contrastan la estadística/asintótico con SciPy. |

También se localizó Nielsen, An Elementary Introduction to Information Geometry, pero la apertura de PMC pidió recaptcha; no se usa como una de las cinco entradas verificadas ni se presume lectura integral.

La identidad FR/H y su consecuencia para el orden de permutaciones se derivan explícitamente en informe.md. La prueba elemental y la auditoría del repositorio no se presentan como un descubrimiento teórico.

## Ampliación de alineación — 2026-10-21

Se leyó Miyamoto et al., sección 4.4.1 de https://arxiv.org/html/2304.14885v3: métrica gaussiana diag(1/sigma²,2/sigma²) y distancia cerrada. El programa usa una identidad equivalente estable, contrastada con acosh a 80 dígitos. No se atribuye Fisher–Rao de las leyes originales a sus proyecciones normales.

Se verificó Shafer–Vovk, JMLR 9, 371–421 (2008), https://jmlr.org/papers/v9/shafer08a.html y su PDF: contexto de rangos e intercambio. El control de tolerancia implementado no se presenta como idéntico a todo su framework conformal.

NIST, https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/tolelimi.htm: distingue contenido y confianza de límites de tolerancia y su relación con percentiles unilaterales. La cota binomial y unión de tres métodos se derivan explícitamente en informe.md.

Documentación oficial de SciPy 1.17.0 para ks_2samp y wasserstein_distance: se usan sus estadísticas; la calibración es independiente y compartida entre métodos. Los nuevos cuatro registros se añaden a referencias.bib; no se presume novedad de estos algoritmos ni revisión exhaustiva.
