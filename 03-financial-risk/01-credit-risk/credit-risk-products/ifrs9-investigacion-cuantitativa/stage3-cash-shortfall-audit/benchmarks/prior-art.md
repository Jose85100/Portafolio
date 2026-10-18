# Prior art y acceso — 2026-10-18

Se revisó main f03f242222a0410f4558fb0522544afcd9ebb4f8: nuevo laboratorio IFRS9,
motor src/ifrs9_engine.py y tests, auditorías anterioresES y risk-enginesC++.
La contribución de hoy profundiza Stage3, no replica los aportes JSON/ES.

Verificado en fuente primaria IFRIC Update March2019, agenda decision13:
cash shortfalls descontados, gross carrying amount y allowance son valores
descontados. B5.5.33 consultado en resultados indexados de copias oficiales
UK/EUR-Lex2016; la página EUR-Lex confirma que el acto2016 fue reemplazado en2023.
La apertura de la edición completa IFRS Foundation redirigió a suscripción;
UK xhtml no pudo renderizarse, y el texto2023 devolvió desafío antirobot. No se
eludió ninguna restricción; no afirmamos revisión de texto consolidado2026.

Literatura consultada en arXiv q-fin.RM: Botha etal2603.11897 (survival de
write-off, NO nuevo default tras estado ya ocurrido) y Reitgruber1411.4265v3
(metodologíaIFRS9 y backtestingLGD). No se atribuyen resultados nuestros a esos
artículos. BIS2015 complementa la contabilidad, no sustituye la norma.
Consultas ECB sobre Stage3 devolvieron WP2841/2792 de efectos de provisiones,
no validación de este código; SemanticScholar devolvió trabajos de LGD y
PaperswithCode perfilBotha. SSRN/indexes especializados y revistas no se
revisaron exhaustivamente. Se distingue cobertura parcial de inexistencia.

La fórmula G-PV(recuperaciones), ponderación de escenarios y uso de expm1 son
conocidos. Novedad incremental local: baseline real + ablaciones PD/descuento,
oracleDecimal y pruebas de invariantes. No prioridad científica ni mejora
predictiva. No se usa tasa de descuento regulatoriaLGD como si fuera EIRIFRS9.
