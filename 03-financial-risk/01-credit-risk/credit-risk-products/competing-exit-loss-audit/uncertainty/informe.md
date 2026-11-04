# Informe — incertidumbre Beta de LGD en tiempo de default competidor

1. **Título/programa.** Extensión de `competing-exit-loss-audit`; añade dispersión de severidad a la cadena 29→30→31→1-nov→2-nov→3-nov.
2. **Hipótesis falsable/aporte.** En escenarios finitos con varianza Beta positiva, el plug-in por la media subestima varianza total de pérdida; error analítico en media frente a Simpson4096 <1e-10. Aporte técnico de incertidumbre, no nuevo estimador.
3. **Estado del arte.** Competing risks y cumulative incidence; Beta como distribución en [0,1]; EAD/LGD contextual IRB. Se citan cinco fuentes BibTeX reales. El modelo no contradice estándar ni formula cumplimiento.
4. **Brecha/candidatas.** Plug-in beta ignora variabilidad condicional; candidatas y motivos en README. Sin base autorizada, se evita ajustar parámetros.
5. **Diseño/config.** Hazards constantes y EAD afín, horizonte 1y, λd=.18, λp=.12, EAD 100→160, Beta(3,2), seed no aplica; benchmark sintético determinista. Config registra entorno.
6. **Fórmula/derivación.** `L=1_D EAD(τ)G`; densidad conjunta marginal default `λd exp[-(λd+λp)t]`. Expandir `EAD=a+bt` da integrales de t^0,t^1,t^2; `E[L²]` usa el segundo momento Beta. La expresión original de LGD puntual queda como baseline al fijar G=E[G]. Propiedades: masa de default ≤1, pérdida no negativa, dispersión tiende a cero conforme α+β→∞ manteniendo media. Independencia es supuesto, no resultado.
7. **Implementación/tests.** Cinco pruebas unitarias incluyen límites, EAD constante, sin default, concentración alta y rechazo de entradas; ejecución `bash run.sh` exit 0. Benchmark valida media con Simpson4096; no se afirma cobertura.
8. **Resultados.** Escenario fijo: E[L]=11.989958599649365; SD Beta incierta=30.032915911546965; SD plug-in=28.23831658603103; error Simpson esperanza=2.4868995751603507e-14. La figura cambia concentración manteniendo media LGD 0.6.
9. **Crítica/ablación negativa.** E[L] no cambia por distribuir LGD independiente con la misma media; sólo aumenta segundo momento. Si α+β→∞ el efecto desaparece, negativo de control. La curva Beta no es calibrada y la independencia puede fallar.
10. **Sesgos/límites.** Un solo escenario sintético, hazards constantes, pérdida sin descuento, EAD lineal, Beta independiente. No estima parámetros, recuperaciones, dependencia, sesgo de selección/censura o ECL regulatorio.
11. **Comando.** `cd 03-financial-risk/01-credit-risk/credit-risk-products/competing-exit-loss-audit/uncertainty && bash run.sh`.
12. **BibTeX.** `referencias.bib`: cinco referencias de competing risk/Beta/estándar contextual; vínculos en README. CRE35 es archivo histórico y no asesoría normativa.
13. **Rúbrica 1–5 (autoevaluación).** Original: novedad 1, rigor 3, reproducibilidad 3, código 3, claridad 3, impacto 2, honestidad 5, MVP 3. Ampliada: profundidad 3, aporte defendible 2, calidad experimental 3, utilidad 3, reproducibilidad 3, honestidad 5.
14. **Siguiente iteración.** Validar independencia y distribución LGD en cohortes autorizadas con censura explícita; detener claims de varianza de cartera si existe dependencia temporal/covariada no modelada.

**Revisión adversarial antes del cierre.** El revisor detectó cancelación en la forma cerrada de \(\int t^2e^{-ht}dt\) cerca de la frontera Taylor/formula cerrada. Se amplió la serie estable a \(hT<0.5\) y se añadieron casos Decimal de 60 dígitos en \(x=0.001,0.0011,0.002,0.499,0.5\), potencias 0–2; error relativo medido <2e-12 en los casos probados. No es una garantía formal para todo float. Suite después de corrección: 6 tests pasan.
