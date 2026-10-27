# CICLO27oct2026 — riesgo de secuencia y primera ruptura

## 1. Título
Oráculo de primera ruptura de caja con persistencia Markov y reserva mínima.

## 2. Hipótesis y novedad incremental
Para reserva6 y horizonte20, H1: modelo persistente supera la probabilidad IID de primera ruptura al menos10pp. H2: primera ruptura persistente supera su caja final negativa al menos2pp. Umbrales fijados enconfig antes de ejecutar. Novedad local: oráculo finito y comparación controlada de secuencias con marginales idénticos; no nueva teoría Markov ni afirmación de desempeño bancario.

## 3. Estado del arte
Cinco fuentes primarias verificadas27oct: Grinstead/Snell sobre cadenas y random walks; Asmussen sobre probabilidad aplicada; Ivanovs sobre procesos aditivos y primeras pasadas; Brunnermeier/Pedersen sobre funding vs market liquidity; BCBS2008 como contexto de liquidez. ReferenciasBibTeX y registro de alcance enprior-art. Asmussen se verificó por metadatos/contenido, no lectura integral; NBER403 se resolvió mediante página del autor. No se afirma revisión exhaustiva ni aplicabilidad regulatoria actual.

## 4. Brecha y alternativas
Se compararon referencia adaptativa del factor26 (PR87 aún abierto), cuantización de crédito25 y primera ruptura Markov. Se elige tercero para rotar a liquidez y cerrar un experimento acotado. El motor C++ ya detecta primera ruptura por trayectoria: no se atribuye un bug. El nuevo componente da probabilidades exactas del modelo finito y reserva mínima, separando terminalidad y supervivencia.

## 5. Diseño/config
C₀=6, horizonte20, flujos g=[+1,−2], régimen inicialπ=[.8,.2]. IID P=[[.8,.2],[.8,.2]]; persistente P=[[.95,.05],[.2,.8]]. Se verifica πP=π en ambos, así que cada día tiene probabilidad20% de estrés y flujo esperado+.4. Solo cambia dependencia temporal. Reserva en enteros0..40 con objetivo5%; no es parámetro regulatorio. MonteCarlo30semillas0–29 por modelo,20.000trayectorias/semilla. Datos generados, sin clientes.

## 6. Derivación e implementación
Cₜ=Cₜ₋₁+g(Sₜ), luego Sₜ₊₁∼P(Sₜ,·). τ=min{t≥1:Cₜ<0}; τ>H es censura derecha, no evento falso. DP vivo fₜ(c,s) guarda probabilidad sin ruptura previa. Para cada estado se añade g(s); masa con nueva caja<0 se absorbe en P(τ=t), el resto transiciona por P. Se mantiene un segundoDP sin absorción para P(C_H<0), permitiendo recuperación contrafactual. Invariante Σₖ≤ₜP(τ=k)+Σfₜ=1. El segundoDP conserva masa1. Reserva mínima se busca en rejilla explícita, sin extrapolar más allá delmáximo; retornaNone si no alcanza. Caja0 no rompe. La absorción mide historia, no supone cierre/liquidación económica. Tipos/entradas finitas y matrices estocásticas validados; límites H≤200,estados≤8 y rango computacional explícito.

## 7. Tests y benchmark
Seis tests: enumeración exhaustiva de2^H,H1..6; recuperación determinista −2,+3; frontera0 yH0; monotonicidad de reserva/masa/búsqueda; estacionariedad y ablaciónH1; entradasinválidas. Error de oráculoH6 observado0. Cobertura realmente medida solo de src/breach.py, no del experimento ni laboratorio vecino. Ruffsrc/tests/benchmarks y mypyestricto núcleo. Suite de liquidez existente ejecutada sin modificarla. RendimientoH20/50/100 guarda tiempo/estados/masa; no se extrapola escalabilidad distribuida. Tiempo/memoriaPython global incluyenMC y búsqueda de reserva. NoC++ modificado: sanitizers no aplican.

## 8. Resultados ejecutados
|Modelo|Primera ruptura|Terminal<0|Recuperación tras ruptura|Reserva mínima objetivo5%|
|---|---:|---:|---:|---:|
|IID|2,9270387%|0,9981786%|1,9288601pp|5|
|Persistente|25,7225097%|15,7928526%|9,9296570pp|22|
H1 diferencia22,7954710pp≥10pp; H2 diferencia9,9296570pp≥2pp. Riesgo de caja final no identifica todas las rupturas. Salidasraw60ensayosMC y curvas82reservas; notebook calculaRMSE contraoráculo. Masa flota dentro≈1e−15. Estos números pertenecen al modelo diseñado, no a frecuencia real de iliquidez.

## 9. Análisis crítico y ablaciones negativas
Horizonte1 con mismo régimen inicial produce exactamente el mismo riesgo en ambos modelos. Además, con reserva0 y horizonte20, persistente da44,3145% frente a48,8796% IID: la curva de riesgo cruza y no existe orden universal entre modelos. Persistencia no aumenta riesgo para toda reserva/horizonte. La secuencia determinista −2,+3 desde1 termina con caja2 pero rompe en día1; falsifica usar saldo final como supervivencia. El DPterminal permite evolución después de déficit solo como comparador contrafactual: no presume que una entidad real pueda financiarlo. El incremento observado depende de parámetros/objetivo, no debe generalizarse a toda matrizMarkov. Marginales iguales no implican igual probabilidad de eventos de trayectoria.

## 10. Limitaciones y riesgos
Dos regímenes sintéticos, flujos fijos por régimen y transición conocida. No hay estimación, incertidumbre deP, contagio de depósitos, moneda, descuentos, activosliquidables, márgenes o políticas de fondeo. No se distingue entidad con línea comprometida de una sin acceso: el saldo puede resultar insuficiente como estado operativo. La rejilla no valida redondeo de flujos reales. Exacto significa recursión finita a precisiónflotante bajo supuestos. Objetivo5% arbitrario de experimento; no conformidadLCR/NSFR/SFC ni consejo de reserva real.

## 11. Reproducción y entorno
`bash run.sh`: creaentorno, instala versionesdirectas, tests propios/integración, cobertura, lint, tipos, benchmark y notebook. OpcionalSKIP_INSTALL1 con entorno listo. Notebook realmente ejecutado conIPythoninprocess secuencial; outputs capturados, no fabricados. Figura inspeccionada separada; no renderHTML completo. Transitivas sinlocktotal; versiones/plataforma/CPU/tiempo/memoria enmetrics.json.

## 12. Referencias
Cinco entradas verificadas enreferencias.bib. Registro de búsquedas y límites enbenchmarks/prior-art.md. Ivanovs trabaja un marco másamplio, no se implementan sus factores; Brunnermeier/Pedersen incluye interacción endógena, ausente aquí. BCBS se cita como contexto2008, no vigencia local.

## 13. Rúbrica
Autoevaluación: novedad2/5,rigor4,reproducibilidad4,código4,claridad4,impacto3,honestidad5,MVP4. Prototipo sintético de componente; revisión independiente y publicación solo se afirman posteriormente con evidencia. No se eleva todo el dominio.

## 14. Siguiente iteración
Siguiente iteración recomendada: incorporar intervalos de incertidumbre de la matriz antes de usar reservas del modelo. Tareas: markov-first-breach-audit evaluar matrices extremas compatibles con muestra; laboratorio de liquidez añadir líneas de fondeo explícitas; risk-engines contrastar oráculo discreto con simulación de trayectorias enC++ sin alterar convención caja<0.

## Checklist
Código/comando/tests/baseline con números/CSVJSONfigura/notebookejecutado/README/informe/cinco referencias/MVP/config/entorno presentes. Revisión yPR reportados aparte; no se simula ejecución.
