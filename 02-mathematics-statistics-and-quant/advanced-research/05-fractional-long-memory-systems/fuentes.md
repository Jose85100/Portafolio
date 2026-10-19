# Verificación dirigida de antecedentes — 2026-10-19

No se afirma revisión sistemática de todas las plataformas sugeridas ni originalidad de los métodos. La prueba de cota específica del MVP está desarrollada en informe.md; no se atribuye una implementación nueva a referencias que no la presentan.

| Entrada | Fuente primaria consultada | Alcance y barreras |
|---|---|---|
| Granger–Joyeux 1980 | https://onlinelibrary.wiley.com/doi/10.1111/j.1467-9892.1980.tb00297.x | Registro editorial indexado con autores/DOI; apertura directa 403. Datos bibliográficos contrastados con registro de autora en https://researchers.mq.edu.au/en/publications/an-introduction-to-longmemory-time-series-models-and-fractional-d/ . No se declara lectura integral. |
| Hosking 1981 | https://academic.oup.com/biomet/article-abstract/68/1/165/237536 | Registro primario indexado con título, DOI, volumen y páginas. Apertura redirige a CDN no accesible; tampoco fue accesible la copia docente intentada. No se afirma lectura integral. |
| Lubich 1986 | https://epubs.siam.org/doi/10.1137/0517050 | Página accesible con abstract, autor, DOI y número impreso mayo 1986; fecha de publicación online 2006 no se confunde con el año del artículo. Contexto de convoluciones fraccionales; no se implementan todos sus métodos multistep. |
| Jensen–Nielsen 2014 | https://onlinelibrary.wiley.com/doi/10.1111/jtsa.12074 | Registro/abstract accesibles: diferenciación fraccional rápida O(N log N) ya es prior art. Autores, DOI, volumen y páginas verificados. También se localizó versión SSRN https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2269814 (2013), sin confundir versión con publicación 2014. |
| NIST DLMF 5.5 | https://dlmf.nist.gov/5.5 | Relaciones funcionales Gamma accesibles. La identidad de prefijos se deriva por recurrencia en informe.md y se comprueba con mpmath. |
| SciPy 1.17.0 | https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.signal.fftconvolve.html | Documentación de la versión fijada; convolución FFT lineal y modos de salida. No se usa el modo circular sin relleno como implementación válida. |

La selección por masa de cola usa una desigualdad elemental y métodos de memoria corta conocidos; la novedad incremental es su auditoría integrada en el programa 05. No se afirma que toda biblioteca de finanzas use el cutoff auditado. No se declara búsqueda exhaustiva en Semantic Scholar, Papers with Code, JMLR, Annals u otras plataformas no recorridas.
