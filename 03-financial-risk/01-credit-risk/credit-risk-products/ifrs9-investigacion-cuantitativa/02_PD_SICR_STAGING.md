# 02. PD temporal, incremento significativo del riesgo y clasificación por etapas

## 1. Separar tres objetos

**PD de originación:** estimación del riesgo de incumplimiento cuando se reconoció inicialmente el instrumento. **PD a la fecha de reporte:** estimación actual, condicionada a información disponible. **SICR:** evaluación del cambio en riesgo de incumplimiento durante la vida esperada desde el reconocimiento inicial, no una regla mecánica basada en cambio de ECL. La definición operacional de default y la evidencia de mora deben conciliarse con políticas contables y prácticas de gestión.

IFRS 9 incorpora una presunción refutable de incremento significativo cuando los pagos contractuales superan 30 días de vencimiento; es un indicador de respaldo, no la única prueba ni una regla que obligue a esperar 30 días. La presunción refutable de default a más tardar a 90 días de vencimiento exige análisis y evidencia si se usa una definición más tardía. Existen criterios cualitativos y otras condiciones que deben incorporarse. La clasificación no puede depender únicamente de un score contemporáneo.

## 2. Modelo de hazard en panel

Para contrato \(i\), mes \(k\) y covariables conocidas en el corte \(t\),

\[
h_{i,k,t}=\Pr(T_i=k\mid T_i\ge k,X_{i,t},M_{t:k}).
\]

Especificación logística:

\[
\operatorname{logit}(h_{i,k,t})=
\alpha_k+\beta^\top X_{i,t}+\gamma^\top M_{t+k,s}
+u_{\mathrm{producto}(i)}.
\]

El efecto \(\alpha_k\) captura duración; \(M_{t+k,s}\) representa escenario macro prospectivo; el modelo puede incluir efectos jerárquicos con regularización. Las PD marginales son \(S_{k-1}h_k\); la PD acumulada a \(H\) es \(1-S_H\).

La verosimilitud discreta para observaciones contrato-periodo expuestas al riesgo es

\[
\ell(\theta)=\sum_{i,k\in\mathcal R_i}
\left[y_{ik}\log h_{ik}+(1-y_{ik})\log(1-h_{ik})\right].
\]

Los contratos censurados contribuyen con periodos observados sin default, sin etiquetarse como no-default de por vida. La censura informativa por prepago o refinanciación requiere modelo de riesgos competitivos o análisis de sensibilidad.

## 3. Riesgos competitivos y prepagos

Con hazards causa-específicas de default \(h_k^D\) y prepago \(h_k^P\), coherentes con eventos mutuamente excluyentes dentro del intervalo,

\[
S_k=S_{k-1}(1-h_k^D-h_k^P),\qquad
\Pr(T_D=k)=S_{k-1}h_k^D.
\]

Es esencial que \(h_k^D+h_k^P\le1\). Tratar el prepago como censura independiente cuando depende del score o de la macroeconomía puede distorsionar tanto la PD como el horizonte de exposición. La definición de vida esperada contable debe armonizarse con este modelo, no derivarse automáticamente de una tasa de prepago estimada.

## 4. Diseño SICR

Una metodología defendible compara medidas de riesgo de default a la fecha de originación y a la fecha de reporte sobre horizontes comparables, teniendo en cuenta el efecto mecánico del envejecimiento del crédito. Una razón ilustrativa es

\[
R_{i,t}=
\frac{PD^{\mathrm{vida\ remanente}}_{i,t}}
{PD^{\mathrm{vida\ remanente\ comparable}}_{i,0}},
\]

acompañada de cambio absoluto, rating, señales cualitativas y evidencia de mora. El denominador debe ser la expectativa al origen para la **misma vida remanente**, no necesariamente la PD original de vida completa. Un umbral universal sobre \(R\) puede ser inadecuado: por ejemplo, pasar de 0.1% a 0.3% y de 15% a 45% tiene la misma razón pero consecuencias de riesgo distintas.

La selección de umbrales debe evaluar error tipo I/II, estabilidad por cohortes, capacidad de anticipar deterioro, sensibilidad macro y posibilidad de transferencias excesivamente procíclicas. Documentar políticas de curación (cure), reversión a Stage 1 y excepciones por indicadores cualitativos. La opción de bajo riesgo crediticio, cuando aplicable, exige justificación y no es equivalente a ausencia de mora.

## 5. Pruebas cuantitativas

**Discriminación:** AUC/Gini por fecha de corte y vintage; no basta AUC agregado. **Calibración:** comparar eventos observados con probabilidades por horizonte y grupos, con intervalos binomiales o bootstrap agrupado por contrato. **Estabilidad:** PSI puede señalar cambio de distribución, pero no demuestra por sí solo deterioro predictivo. **Validación temporal:** entrenar en cortes anteriores y probar en cohortes posteriores; imponer embargo cuando las ventanas de resultado se superponen. **Sensibilidad:** estresar empleo, tasas y actividad económica preservando relaciones plausibles.

## 6. Fuga de información y sesgo mecánico

El saldo observado **en el momento de default** no es una variable admisible para pronosticar desde un corte anterior si no era observable entonces. Es información posterior y puede introducir look-ahead bias. Sin embargo, ese saldo sí es un dato legítimo para **medir la EAD realizada y validar** predicciones de EAD ex ante. La exclusión de información futura debe distinguir construcción de variables predictoras de construcción de etiquetas y resultados observados.

Asimismo, usar la media de saldos de los 12 meses previos como EAD de todos los productos puede crear sesgo de producto y horizonte: es una hipótesis empírica, no un requisito IFRS 9. Deben compararse estimadores mediante pérdidas predictivas y reconciliación de flujos.

## 7. Diseño de evidencia

Registrar para cada contrato: fecha de originación, fecha de reporte, rating al origen, score actual, historial DPD, default, curación, cambios contractuales, variables macro vintage y fecha de disponibilidad. Congelar snapshots y reconstruir qué se conocía realmente en cada fecha. Sin trazabilidad temporal, el backtest de SICR no es defendible.
