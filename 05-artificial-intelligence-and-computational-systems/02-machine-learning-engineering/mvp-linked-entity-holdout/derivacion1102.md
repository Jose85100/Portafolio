# De cotas condicionales a elegibilidad temporal y semántica

## Original y limitación

El1nov, partial_audit calcula extremos $[L,H]$ de filas expuestas sobre completaciones consistentes con equivalencia completa entre adjudicados. Para clases mixtas conocidas M, clases puras train ordenadas por tamaño $a_i$, puras test $b_j$ y desconocidos $u_{train},u_{test}$:

$$L=\sum_{m\in M}|m|,\qquad H=L+u+\sum_{i=1}^{\min(p,u_{test})}a_i+\sum_{j=1}^{\min(q,u_{train})}b_j.$$

La derivación y alcanzabilidad se conservan en derivacion1101.md y sus5508 configuraciones exhaustivas. No se modifica esa fórmula. La limitación es operacional/epistémica: la API no podía saber si el llamador suministraba enlaces positivos incompletos como equivalencia, ni cuándo estaban disponibles. Evaluar correctamente una fórmula con entradas semánticamente inválidas no valida el resultado.

## Notación, dominio y regla propuesta

Snapshot S declara filas adjudicadas K⊆V, fuente s, versión v, semántica q, fecha efectiva e y fecha de disponibilidad a. El corte congelado es c. Las fechas son instantes ISO8601 con zona; se normalizan UTC antes de comparar, no cadenas de offsets distintos. q debe declarar equivalencia completa **entre el subconjunto adjudicado**, incluidas diferencias entre clases. Enlaces positivos no acreditan esas diferencias.

$$G(S,c)=1\{v=1\}\,1\{s\ne\varnothing\}\,1\{q=\mathrm{equiv\_complete}\}\,1\{e\le c\}\,1\{a\le c\}.$$

Fuente vacía/solo espacios no es admisible. Fechas sin zona o inválidas, IDs fuera de universo, duplicados y asignación incompleta producen ValueError. Otras incompatibilidades devuelven blocked con motivos y **sin cotas**. Si G=1 se llama el auditor1nov y devuelve metadata-eligible: la interpretación depende aún de corrección de adjudicación. No convertirlo en validado/operacional.

## Derivación y propiedades

1. A partir del supuesto de información prospectiva, solo evidencia ya disponible a c puede usarse para construir/justificar la partición: a≤c. Saber hoy que una identidad era válida en e≤c no implica que se conociera entonces. Por eso e≤c solo es insuficiente.
2. La igualdad q=equivalencia completa es requisito para impedir fusiones entre clases adjudicadas diferentes en la derivación1nov; sin ese dato, su conjunto de completaciones puede ser demasiado pequeño. El gate no infiere semántica a partir de etiquetas singleton ni de cobertura.
3. Intersecar esas condiciones con esquema conocido/fuente declarada define G. Si G=1, se preservan EXACTAMENTE L/H del auditor1nov; si G=0, se abstiene en lugar de inventar un intervalo. Esta es disciplina conocida de contratos/point-in-time, no nueva teoría ML.
4. Con declaraciones honestas, la regla implica a≤c y e≤c por construcción. No prueba ausencia de fuga en features, etiquetas, selección de muestra, tuning o links observados usados antes del gate. El snapshot de identidades se supone estático y aplicable al caso histórico; no modela identidades que cambian de validez ni expiraciones.
5. El predicado event-time-only omite a≤c: con e=c y a=c+1µs admite información futura. Contrajemplo determinista; no resultado estadístico ni prevalencia empírica. Si fechas/fuente mienten, puede pasar: límite de confianza conservado explícitamente.

## Manifest e integridad

Sea P el payload que incluye snapshot, observed, asignación congelada y corte. Se ordenan IDs/identidades, se normalizan offsets y se serializa JSON con claves ordenadas/separadores fijos y ASCII. $h=\operatorname{SHA256}(P)$ vincula esos bytes canónicos. Orden distinto y mismo instante con otro offset producen mismo h; cambiar fuente, corte o asignación normalmente cambia h (tests concretos, no demostración de ausencia de colisiones). verify_manifest vuelve a calcular y compara el digest. No firma, no autenticidad, no historial inmutable: quien altera payload y recalcula hash conserva verificación. No afirmar cumplimiento completo W3C PROV; se usa como inspiración para procedencia explícita.

Unidades: e/a/c en instantes UTC, latencias ilustrativas en horas, L/H en filas, coste en ns/bytes; digest sin unidad. Tiempo de serialización/hash y auditoría O(n log n+L_id+B) por ordenación/clausuras y B bytes de payload, memoria O(n+L_id+B); no constante ni gratis. Registro CPU/hardware real en environment.json. Instalación e I/O excluidos de benchmarks. Con v1, fuente y semántica correctas y fechas elegibles se recupera exactamente1nov; no se alteran ecuaciones anteriores ni contratos compartidos.
