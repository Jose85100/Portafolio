# CICLO29oct2026 — pérdida con salidas competidoras

## 1. Título
Default, prepago y población activa en pérdida esperada descontada.

## 2. Hipótesis y novedad incremental
H: omitir prepago en el escenario suministrado supera la pérdida conjunta al menos20% respecto de esta. Umbral fijado antes de ejecutar. Aporte local: motor pequeño de flujo de probabilidad con contrato de EAD condicional y comparación racional independiente. No nueva teoría de riesgos competidores ni sistemaIFRS9 certificado.

## 3. Estado del arte
Cinco referencias verificadas: Deng/Quigley/VanOrder2000 sobre terminaciones hipotecarias; Putter/Fiocco/Geskus2007 sobre multiestado; Austin/Lee/Fine2016 y Andersen etal2012 sobre incidencia vs riesgo condicional; Fine/Gray1999 sobre subdistribución. ReferenciasBibTeX y detalle de accesos enprior-art. Algunos textos completos bloquearon acceso automático; se verificaron metadatos/DOI y abstract disponibles, no lectura exhaustiva. No se ajusta ninguno de sus modelos de regresión.

## 4. Brecha y alternativas
Se compararon fondeo de liquidez, correlación de cartera y salidas competidoras. Elegimos tercero para rotar fuera de liquidez y cerrar alcance mínimo. El engineIFRS existente declara aproximación anual sin prepago explícito; no se afirma que esté contablemente mal. Nuestro baseline es el caso contrafactual sin prepago, no un supuesto bug. Igual período en ambas proyecciones; ninguna conversión automática de unidades.

## 5. Diseño/config
12períodos uniformes, d=.02,p=.10, EAD100,LGD.45,r=.005 porperíodo. Cinco valoresp=[0,.02,.05,.10,.20]. Todos los demás parámetros fijos. Datos sintéticos,no clientes. El calendario se expresa en períodos genéricos; si se usa anual o mensual, toda probabilidad y tasa debe corresponder a esa unidad. No se infiere PD12m mensualizando por división. EAD es condicional en activo/default, no un saldo esperado ya reducido por prepago.

## 6. Método y contrato
S₀=1; Dₜ=Sₜ₋₁dₜ; Pₜ=Sₜ₋₁pₜ; Sₜ=Sₜ₋₁(1−dₜ−pₜ). Son probabilidades discretas de eventos mutuamente excluyentes dados los activos al inicio, no dos intensidades independientes continuas. Exigimos d,p≥0 y d+p≤1. Incidencia de default=ΣDₜ,incidencia prepago=ΣPₜ. InvarianteΣD+ΣP+S=1. EL=ΣDₜ×EADₜ×LGD/(1+r)^t. EAD puede variar porperíodo; LGD y tasa son escalares en esteMVP. Tasa∈[0,1],LGD∈[0,1], EAD finita≥0,1..360períodos. No se añade ordendefault-antes-prepago: los resultados del mismo período ya vienen como probabilidades exclusivas. La recurrencia financiera es O(H); el diagnóstico de masa usa sumas compensadas de todos los prefijos y cuesta O(H²) en esta implementación pequeña. Memoria O(H) para guardar cronograma.

## 7. Tests y benchmark
Cinco tests: oráculo independiente Fraction a12períodos; fórmula cerrada sinprepago y ablación1período; masa/absorción/EAD0; monotonicidad manteniendo probabilidades condicionales fijas,descuento y escala; entradas inválidas. Cobertura realmente medida solo núcleo, no todo experimento. Ruffsrc/tests/benchmarks y mypyestricto núcleo. Comparación determinista de5escenarios y cronogramas24filas, sinMC. Oráculo usa aritmética racional completa, no valores copiados del método flotante. Tiempo/memoria/CPU/versiones enmetrics. No C++ modificado,sanitizers no aplican.

## 8. Resultados
|Modelo|Default acumulado|EL descontada|
|---|---:|---:|
|Sin prepago|0,2152832763|9,3913606004|
|Salidas conjuntas|0,1307214740|5,7373789444|
El baseline supera al conjunto63,6872985%,H cumple20%. Oráculo racional EL5,737378944381397,error observado≈2,66e−15. Diferencia no estima ajuste contable real. El contraste matemático separa dos universos activos manteniendo igual PDcondicional,LGD/EAD/descuento. Sensibilidad guardada completa enCSV.

## 9. Análisis crítico y ablaciones negativas
Con p0 coincide supervivencia1−PD y ambos modelos; con H1,prepago y default del mismo período no compiten por una población previamente reducida: masa de default sigue d₁. No se muestra una falsa mejora en esos casos. Prepago total en primerperíodo elimina defaults posteriores. La disminución deEL al aumentar prepago se refiere a PD y EAD condicionales fijos; en datos reales la selección puede elevar el riesgo del grupo remanente. El baseline es válido para un mundo sin esa salida, pero no estima incidencia conjunta en nuestroDGP conp>.0.

## 10. Limitaciones y riesgos
No hay ajuste a datos, censura o identificabilidad de hazards. Probabilidades suministradas pueden estar mal calibradas o usar otra unidad. EAD ya ponderada por salidas produciría dobleconteo; el contrato lo prohíbe. No modela revolving,drawdowns,recobros,cures,modificaciones,escenariosmacro o correlación. No implementa staging/SICR/POCI o reglas deIFRS9/SFC. No se utiliza para gastos/reintegros/provisiones reales. Literatura estadística de otros dominios justifica identidades, no desempeño bancario.

## 11. Reproducir
`bash run.sh` instala versionesdirectas y ejecuta todo. OpcionalSKIP_INSTALL1 con entorno listo. Venv por defecto; transitivas sinlocktotal. Notebook realmente ejecutado enIPython secuencial conoutputs capturados; figura inspeccionada separada, sin renderHTML completo afirmado. No hay credenciales,datos de clientes o serviciosLLM externos.

## 12. Referencias
Cinco entradas reales conDOI/URL enreferencias.bib. Prior-art registra fuentesoriginales,indexación y bloqueos. No se inventan citas ni se atribuyen nuestras cifras a artículos; revisiónfocal,no exhaustiva.

## 13. Rúbrica
Autoevaluación: novedad2/5,rigor4,reproducibilidad4,código4,claridad4,impacto3,honestidad5,MVP4. Componente sintético, no madurez de programa. Revisión independiente/publicación solo se afirman posteriormente con evidencia.

## 14. Siguiente iteración
Siguiente iteración recomendada: ajustar conjuntamente default y prepago con cohortes temporales y validar que EAD sea condicional. Tareas: competing-exit-loss-audit añadir EAD amortizable y prueba de calendario; ifrs9-investigacion-cuantitativa definir contrato explícito de prepago antes de integrar; credit-portfolio-strategy investigar selección de sobrevivientes sin afirmar causalidad.

## Checklist
Código/comando/tests/baseline numérico/CSVJSONfigura/notebookejecutado/README/informe/cinco referencias/MVP/config/entorno presentes. No se simulan ejecución, revisión o publicación.
