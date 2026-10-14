# Prior art focalizado — 2026-10-14

Consultas ejecutadas: ES ponderado/escenarios finitos en arXiv; Acerbi–Tasche; Rockafellar–Uryasev; cuantiles Hyndman–Fan; Higham; NIST floating point/numerical reproducibility; BIS ES market risk; LLVM ASan/UBSan/Clang-Tidy; SSRN weighted ES; Semantic Scholar fast detection ES; ECB expected shortfall WP; Papers with Code expected shortfall.

Fuentes primarias seleccionadas y metadatos: ocho entradas en referencias.bib. La apertura editorial de Rockafellar–Uryasev y una apertura arXiv de Bouchard devolvieron errores; títulos, autores y DOI/URLs fueron verificables en resultados editoriales/arXiv y página de autor. No se afirma acceso a esos textos completos.

La definición y los métodos numéricos son conocidos. Bouchard–Reghai–Virrion abordan clasificación eficiente de escenarios en simulación anidada: **no** se usó como baseline de velocidad frente al cálculo directo de escenarios conocidos, porque el problema computacional es diferente. SSRN y ECB devolvieron trabajos de combinación de pronósticos y dinámica de colas, no necesarios para probar el contrato finito. Semantic Scholar/Papers with Code no aportaron un resultado primario decisivo en el output recibido; es cobertura parcial, no evidencia de ausencia.

Revisión del repo: commit c213a687d501faae8b2637546f89b980425adfad; PR #32 ya integrado. API C++ `quant::tail` uniforme existente, README/CMake/tests del motor y aporte Python revisados. Búsqueda de PRs weighted/tail no encontró otro aporte C++ equivalente. No se afirma haber agotado literatura ni todo el código mundial.

Novedad defendible: extensión C++ integrada a pesos + fixtures binarios/racionales compartidos + benchmark contra el baseline real mediante expansión exacta + detección de un caso de underflow del aporte Python. No fórmula nueva ni prioridad científica.
