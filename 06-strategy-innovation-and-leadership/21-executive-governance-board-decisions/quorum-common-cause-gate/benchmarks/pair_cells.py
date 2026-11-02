"""Teaching increment: a requirement for future evidence is not evidence obtained."""
import nbformat as nbf


def pair_cells():
    md = nbf.v4.new_markdown_cell
    code = nbf.v4.new_code_cell
    return [
        md(r"""## 2 de noviembre: ¿qué evidencia conjunta haría falta para mantener B?
El1 de noviembre, admitir incertidumbre de parámetros llevó de B(costo3) a C(costo4) para certificar la misma meta0,85. Hoy **no inventamos una muestra**. Construimos una herramienta para preguntar qué restricción conjunta, si pudiera justificarse, permitiría mantener la opción más barata.

La restricción propuesta es $P(B_1=B_2=1\mid shock)\ge\phi$. $\phi$ es un dato de entrada supuesto y condicionado al shock; no es una frecuencia observada ni un límite de confianza estimado. Usamos el escenario hipotético$\phi_B=0,65$, sin restricciones adicionales para A/C. Conservamos caja, costos, reglas y meta. El baseline sin esta información sigue siendo válido para su conjunto mayor; la comparación no demuestra eficacia de recolección de datos ni ahorro realizado."""),
        md(r"""### Derivación: reducir la clase de leyes admisibles
Original01nov:
$$L_{box}=(1-s_+)r_-+s_+(r_-+q_{1-}+q_{2-}-2)_+.$$
Sea $C=B_1\cap B_2$ y $t=P(C\mid shock)$. Por Fréchet y la restricción suministrada:
$$t\ge t_*:=\max(0,\phi,q_{1-}+q_{2-}-1).$$
Para las dos variables indicadoras R y C, $P(R\cap C)\ge(r_-+t_*-1)_+$. Por probabilidad total:
$$L_\phi=(1-s_+)r_-+s_+(r_-+t_*-1)_+.$$
Es una especialización de cotas clásicas y optimización de probabilidades con restricciones de momentos, no una nueva teoría. La restricción es factible si $0\le\phi\le\min(q_{1+},q_{2+})$. El conjunto es cerrado y acotado; los extremos existen. Se recupera exactamente01nov con$\phi=0$, y aumentar una restricción factible no puede empeorar el certificado.

**Alcanzabilidad:** elegir$t=t_*$ y$q'_i=\max(q_{i-},t_*)$ respeta los intervalos si la restricción es factible. Las cuatro masas del par son$t_*,q'_1-t_*,q'_2-t_*,1-q'_1-q'_2+t_*$, no negativas. Distribuir la masa de R primero fuera de C alcanza$(r_-+t_*-1)_+$. Así la cota es sharp para este evento y esta clase supuesta. No se impone independencia de R ni una cópula inferior global."""),
        code("from benchmarks.pair_run import load_pair_config, lp_pair\nfrom src.pair_assurance import pair_lower, required_pair_floor, choose_pair\npcfg,pplans,prisk,pshock=load_pair_config()\npdf=pd.DataFrame([{'plan':p.name,'cost':p.cost,'box_lower':interval_bounds(p,prisk,pshock)['lower'],'pair_lower':pair_lower(p,prisk,pshock,pcfg['floors'][p.name])} for p in pplans])\ndisplay(pcfg['evidence_status'])\ndisplay(pdf.round(6))\nassert abs(pdf.loc[1,'pair_lower']-.8665)<1e-12\nassert choose_pair(pplans,prisk,pshock,pcfg['floors'],pcfg['target']).name=='B'"),
        md(r"""### Testigo independiente con LP, misma información
Se mantienen ocho masas$p_{abc}$, suma1, no negatividad y marginales dentro de sus intervalos. Añadimos una sola desigualdad$\sum bc\,p_{abc}\ge\phi$. El objetivo incorpora$(1-s_+)\sum a p+s_+p_{111}$, incluyendo normal y shock. No usamos la expresión cerrada para construir la solución LP; recibe la misma caja y el mismo piso que el método analítico.

Revisamos factibilidad, objetivo y restricción conjunta. Las masas son un contraejemplo o extremo construido, no datos observados."""),
        code("pB=pplans[1]\npvalue,pmass,pstates=lp_pair(pB,prisk,pshock,pcfg['floors'][pB.name])\npw=pd.DataFrame(pstates,columns=['R','B1','B2']);pw['mass']=pmass\ndisplay(pw)\nassert abs(pmass.sum()-1)<1e-10\nassert ((pstates[:,1]*pstates[:,2])@pmass)>=pcfg['floors'][pB.name]-1e-10\nassert abs(pvalue-pair_lower(pB,prisk,pshock,pcfg['floors'][pB.name]))<1e-10\nporacle=pd.read_csv('results/pair_oracle.csv')\nassert poracle.error.max()<1e-10\nprint('Escenarios de oráculo:',len(poracle),'error máximo:',poracle.error.max())"),
        md(r"""### Umbral mínimo requerido y regiones sin aporte
Si la caja ya cumple la meta$\tau$, no hace falta piso adicional: se devuelve0. Si no cumple y$s_+>0$, resolver$L_\phi\ge\tau$ da
$$\phi_{req}=1-r_-+\frac{\tau-(1-s_+)r_-}{s_+}.$$
Solo se considera alcanzable si$\phi_{req}\le\min(q_{1+},q_{2+})$. Con$s_+=0$, el par no puede reparar un rol insuficiente. Para B y meta0,85, el requisito calculado es$4/7\approx0,5714286$; no afirmamos que datos disponibles lo respalden.

Si$\phi\le q_{1-}+q_{2-}-1$, la información es redundante y no mejora la cota: para B, piso0,55 no agrega nada a su base0,56. Una entrada0,99 es incompatible con sus marginales superiores0,82 y se rechaza; jamás se interpreta un conjunto vacío como garantía perfecta. El gráfico muestra el umbral, meseta y costo de decisión, con escenarios sintéticos."""),
        code("pthreshold=required_pair_floor(pB,prisk,pshock,pcfg['target'])\nprint('Piso conjunto requerido para B:',pthreshold)\nassert abs(pthreshold-4/7)<1e-12\nassert abs(pair_lower(pB,prisk,pshock,pthreshold)-pcfg['target'])<1e-12\nassert pair_lower(pB,prisk,pshock,pthreshold-1e-5)<pcfg['target']\nassert abs(pair_lower(pB,prisk,pshock,.55)-interval_bounds(pB,prisk,pshock)['lower'])<1e-12\ndisplay(Image(filename='results/pair_assurance.png'))\npsummary=json.loads(Path('results/pair_summary.json').read_text())\ndisplay(psummary['timing_n100_median_seconds'])\ndisplay(pd.read_csv('results/pair_decisions.csv'))"),
        md(r"""### Decisión y límites de interpretación
**Continuar** con C bajo la caja sin evidencia conjunta adicional. **Ajustar** a B solo si el responsable acepta una restricción válida al menos igual al umbral calculado, para el mismo régimen, población y horizonte; el escenario0,65 no es esa aceptación. **Cerrar** el menú cuando ninguna opción certifique la meta, o rechazar entradas incompatibles, sin bajar quórum.

Comparación condicional: si la restricción fuera válida, B cuesta una unidad abstracta menos por sesión que C. La ablation que suministra el mismo piso0,65 a todas las opciones elige A(costo2): el motor no favorece B y no se demuestra que investigar B sea óptimo. No calculamos rentabilidad de un estudio sin datos de costo, cobertura y vigencia; no hay ahorro observado. Restricciones más fuertes pueden reducir conservadurismo, pero excluir leyes válidas sin evidencia fabrica confianza falsa.

Negativos preservados: piso redundante no aporta, piso0 recupera01nov, meta0,97 es inviable y ausencia de shock no se repara con coasistencia. Fórmula y LP son igualmente precisos en la malla; tiempos excluyen instalación/carga y memoria Python no incluye nativaHiGHS/RSS. Herramienta S2 sintética, adaptación de ingeniería y auditoría de cotas conocidas; no validación empresarial, legalidad ni calidad decisional. Próximo hito: contrato de evidencia conjunta con validación temporal y cobertura simultánea antes de convertir supuestos en estimaciones."""),
    ]
