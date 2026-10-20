# Búsqueda focalizada y procedencia — 2026-10-20

Repo base dd5dc42984ca98ecf3ccda47a21dfd4008afe0bb. PR57 ya integrado. Revisión de
README, CMake y librería risk-engines: crédito gaussiano de defaults futuros y
weighted-tail-audit; no se encontró API de flujos Stage3 en esa biblioteca.
03-financial-risk sí tiene el cálculo estable y su migración: se reutiliza como
baseline correcto de paridad, sin presentarlo como hallazgo nuevo.

Fuentes primarias abiertas: IFRIC marzo2019, BIS d350, arXiv1411.4265,
NumPy2.1expm1, Python3.12Decimal, GCCinstrumentation y NISTreproducibility.
IFRIC sustenta cash shortfalls; BIS y Reitgruber son contexto de model risk/LGD,
no validación de esta API. NumPy explica estabilidad; GCC explica instrumentación.

Consultas: IFRS9 LGD/cash shortfalls/numerical en arXiv, SSRN, Semantic Scholar,
Papers with Code y ECB WP. Resultados pertinentes visibles: SSRN4750458 y
ECB WP2792/2841, sólo metadatos de búsqueda; no se afirma lectura de esos textos.
No se recuperó benchmark implementable equivalente en SemanticScholar/PWC en
esta búsqueda; no significa que no exista. No se hizo revisión exhaustiva de
Journal of Risk/Journal of Financial Econometrics ni acceso de suscripción.
Una búsqueda alternativa produjo resultados irrelevantes y se descartaron.
El borrador C++17 N4659 no pudo recuperarse, no se cita como leído.

No se reclama prioridad de la fórmula, originalidad científica del port ni
certificación regulatoria. Aporte incremental: API acotada C++ y contrato de
paridad automatizado con Python real, Decimal, sanitizers y coste observable.

Guía visualize-data aplicada al benchmark estático. Sus referencias compartidas
no pudieron recuperarse; se continúa con la guía principal y QA de figura.
No se crea notebook: el entregable principal es src C++ ejecutable con CMake.
