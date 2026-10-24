"""Idempotent scientific extensions; original generators call extend after rebuilding."""
from pathlib import Path
import argparse
import textwrap
import hashlib
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
AI=ROOT/'05-artificial-intelligence-and-computational-systems'
ARCH=AI/'03-deep-learning-and-foundation-models/structured-decision-architectures'
TARGETS=[
 ROOT/'01-economics-and-econometrics/04-econometrics/05-instrumental-variables/weak-iv-inference-audit/notebook.ipynb',
 ROOT/'02-mathematics-statistics-and-quant/advanced-research/13-path-signatures-hidden-dynamics/notebook.ipynb',
 ROOT/'03-financial-risk/01-credit-risk/fraud-and-anomaly-research/01-identity-kyc-consistency/channel-conformal-audit/notebook.ipynb',
 AI/'02-machine-learning-engineering/02-conformal-risk-prediction/notebook.ipynb',
 ROOT/'06-strategy-innovation-and-leadership/20-ai-innovation-productivity-leadership/innovation-evsi-gate/notebook.ipynb',
 ARCH/'01-typed-decision-cascade/notebook.ipynb', ARCH/'02-evidence-preserving-document-pipeline/notebook.ipynb']

def md(s): return nbf.v4.new_markdown_cell(textwrap.dedent(s).strip())
def code(s): return nbf.v4.new_code_cell(textwrap.dedent(s).strip())
def pair(cells,title,explanation,source):
    cells.extend([md('### '+title+'\n\n'+explanation),code(source)])

STYLE='''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
plt.rcParams.update({'figure.figsize':(8,4.6),'font.size':11,'axes.spines.top':False,
                     'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18})
BLUE='#245B83'; GOLD='#B57A21'; GRAY='#4D5358'
rng_depth=np.random.default_rng(20261023)
'''

def extensions(index):
 c=[md('## Laboratorio ampliado — derivación, usos y refutación\n\nExperimentos adicionales del 23 de octubre de 2026. Datos sintéticos; las cifras guardadas del estudio original se conservan y las nuevas se recalculan debajo.'),code(STYLE)]
 if index==0:
  c.append(md(r'''### Modelo, identificación y unidades

$$x_i=\pi z_i+v_i,\quad y_i=\beta x_i+u_i+\gamma z_i,\quad E[z_iu_i]=0.$$

$\beta$ mide unidades de $y$ por unidad de $x$; $\pi$ es relevancia; $\gamma=0$ expresa exclusión. La correlación entre $u$ y $v$ hace endógeno a $x$. Dividir por una primera etapa casi nula vuelve inestable a IV. Anderson–Rubin prueba $H_0:\beta=b$ mediante la regresión de $y-bx$ sobre $1,z$.

$$F_{AR}(b)=\frac{SSR_0(b)-SSR_1(b)}{SSR_1(b)/(n-2)}\sim F_{1,n-2}.$$

La distribución exacta requiere errores estructurales IID normales homocedásticos y exclusión válida. La robustez a relevancia débil no sustituye estos supuestos.'''))
  pair(c,'Reconstrucción independiente del estadístico','Contrastar sumas de cuadrados con la implementación evita confiar solo en el gráfico guardado.', '''
from src.inference import sample, ar_pvalue, wald_pvalue, first_stage_f
from scipy.stats import f
y_d,x_d,z_d=sample(42,150,1.)
b_null=1.
residual=y_d-b_null*x_d
Z=np.column_stack([np.ones(len(z_d)),z_d])
fit=Z@np.linalg.lstsq(Z,residual,rcond=None)[0]
sse=float(np.sum((residual-fit)**2)); sst=float(np.sum((residual-residual.mean())**2))
f_manual=max(0,sst-sse)/(sse/(len(y_d)-2))
p_manual=float(f.sf(f_manual,1,len(y_d)-2))
assert abs(p_manual-ar_pvalue(y_d,x_d,z_d,1.))<1e-10
print({'F_AR':f_manual,'p_value':p_manual,'F_primera_etapa':first_stage_f(x_d,z_d)})
''')
  pair(c,'Inversión del test y conjunto de confianza','El grid no certifica los límites exactos: un conjunto puede ser desconectado, ilimitado o vacío. No reducirlo automáticamente a una banda entre mínimo y máximo.', '''
grid_beta=np.linspace(-8,10,721)
fig,ax=plt.subplots()
for strength,style in [(0.,'--'),(8.,'-')]:
    yy,xx,zz=sample(51,150,strength)
    pvals=np.array([ar_pvalue(yy,xx,zz,b) for b in grid_beta])
    ax.plot(grid_beta,pvals,label=f'c={strength:g}',ls=style)
    accepted=grid_beta[pvals>.05]
    print('c=',strength,'fracción del grid aceptada=',len(accepted)/len(grid_beta),
          'toca frontera=', bool(len(accepted) and (accepted[0]==grid_beta[0] or accepted[-1]==grid_beta[-1])))
ax.axhline(.05,color=GRAY,ls=':'); ax.set(xlabel='Beta nula (y/x)',ylabel='p-valor AR',title='Inversión de AR sobre un grid finito');ax.legend();plt.show()
''')
  pair(c,'Relevancia y exclusión son preguntas distintas','Repeticiones nuevas con semillas separadas del estudio original. Las barras muestran tasas Monte Carlo, no cobertura de una cartera real.', '''
from scipy.stats import binomtest
records=[]
for strength,gamma in [(0,0),(1,0),(8,0),(1,.35)]:
    rejected_ar=[];rejected_w=[]
    for seed in range(120):
        yy,xx,zz=sample(50000+seed,150,strength,exclusion=gamma)
        rejected_ar.append(ar_pvalue(yy,xx,zz,1.)<=.05)
        rejected_w.append(wald_pvalue(yy,xx,zz,1.)<=.05)
    lohi=binomtest(sum(rejected_ar),120).proportion_ci(method='wilson')
    records.append({'c':strength,'gamma':gamma,'AR':np.mean(rejected_ar),'Wald':np.mean(rejected_w),'AR_lo':lohi.low,'AR_hi':lohi.high})
checks_iv=pd.DataFrame(records);display(checks_iv.round(4))
fig,ax=plt.subplots();pos=np.arange(len(records))
ax.bar(pos-.17,checks_iv.AR,.34,label='AR',color=BLUE)
ax.bar(pos+.17,checks_iv.Wald,.34,label='Wald',color=GOLD)
ax.set_xticks(pos,[f'c={r["c"]}, gamma={r["gamma"]}' for r in records]);ax.axhline(.05,color=GRAY,ls='--')
ax.set(ylabel='Fracción de rechazos, 120 réplicas',title='Identificación débil y violación de exclusión');ax.legend();plt.show()
''')
  pair(c,'Escala e invariancia','Cambiar unidades de x y la hipótesis de beta de forma consistente debe conservar AR.', '''
original=ar_pvalue(y_d,x_d,z_d,1.)
converted=ar_pvalue(y_d,100*x_d,z_d,.01)
assert abs(original-converted)<1e-12
assert abs(original-ar_pvalue(y_d,x_d,-3*z_d,1.))<1e-12
print('Invariancia de unidades e instrumento verificada.')
''')
  c.append(md('### Uso y próxima falsificación\n\nUsar AR para hipótesis estructurales con exclusión defendible, no para resolver instrumentos inválidos. Reportar el conjunto invertido completo y la primera etapa. Próximo experimento: heterocedasticidad con inferencia robusta y su comparación contra este F exacto; no atribuir a este notebook esa garantía pendiente.'))
 elif index==1:
  c.append(md(r'''### Firma truncada y orden temporal

Para incrementos $\Delta x_k$ de una trayectoria lineal a trozos:

$$S^1=\sum_k\Delta x_k,\quad S^2=\sum_{i<j}\Delta x_i\otimes\Delta x_j+\frac12\sum_k\Delta x_k\otimes\Delta x_k.$$

La composición de Chen es $(a,b)\star(c,d)=(a+c,b+d+a\otimes c)$. El área orientada es $(S^2_{12}-S^2_{21})/2$, en unidades de coordenada 1 por coordenada 2. Ni esta área ni una firma de nivel dos identifican una trayectoria completa.'''))
  pair(c,'Chen frente a cálculo de trayectoria completa','Una partición conserva el punto de unión, sin repetir un desplazamiento.', '''
from src.signatures import signature, compose, circle, signed_area, polygon_area
path_d=np.cumsum(rng_depth.normal(size=(100,2)),axis=0)
whole=signature(path_d)
split=compose(signature(path_d[:51]),signature(path_d[50:]))
assert all(np.allclose(a,b,atol=1e-10) for a,b in zip(whole,split))
print('Error de composición:',max(np.max(np.abs(a-b)) for a,b in zip(whole,split)))
''')
  pair(c,'Identidad shuffle y reversión','La parte simétrica queda determinada por el desplazamiento; el contenido nuevo de nivel dos está en la parte antisimétrica.', '''
a_d,b_d=whole
shuffle=b_d+b_d.T-np.outer(a_d,a_d)
assert np.max(np.abs(shuffle))<1e-9
assert np.allclose(signature(path_d[::-1])[1],np.outer(a_d,a_d)-b_d)
print('Residual shuffle máximo:',np.max(np.abs(shuffle)))
''')
  pair(c,'Convergencia del área y aliasing','La referencia analítica de un círculo de radio uno con q vueltas es q*pi. El error de discretización no es incertidumbre estadística.', '''
rows_d=[]
for turns in [1,2,3]:
    for n in [4,8,16,32,64,128,256]:
        path=circle(n,turns=turns)
        area=signed_area(path)
        assert abs(area-polygon_area(path))<1e-10
        rows_d.append({'vueltas':turns,'segmentos':n,'area':area,'error':abs(area-turns*np.pi)})
areas_d=pd.DataFrame(rows_d);display(areas_d.head(9).round(5))
fig,ax=plt.subplots()
for (turns,g),color,marker in zip(areas_d.groupby('vueltas'),[BLUE,GOLD,GRAY],['o','s','^']):
    ax.loglog(g.segmentos,g.error,marker=marker,color=color,label=f'{turns} vueltas')
ax.set(xlabel='Segmentos observados',ylabel='Error absoluto de área',title='Convergencia y pérdida por muestreo');ax.legend();plt.show()
''')
  pair(c,'Misma bolsa de puntos, orden diferente','Una representación que borra el orden no puede recuperar orientación. Aquí se compara la misma trayectoria con su reversa.', '''
path=circle(40)
forward=signed_area(path); backward=signed_area(path[::-1])
assert np.allclose(path.mean(0),path[::-1].mean(0))
assert np.isclose(forward,-backward)
fig,ax=plt.subplots();ax.plot(path[:,0],path[:,1],color=BLUE)
for i in [3,14,25]:
    ax.annotate('',xy=path[i+1],xytext=path[i],arrowprops={'arrowstyle':'->','color':GOLD})
ax.set(aspect='equal',xlabel='x1',ylabel='x2',title='Orden y área orientada; radio uno');plt.show()
print({'area_ida':forward,'area_reversa':backward})
''')
  pair(c,'Contraejemplo de identificabilidad','Una excursión recta y su retorno tienen firma truncada nula, como una trayectoria constante.', '''
excursion=np.array([[0.,0.],[2.,3.],[0.,0.]])
constant=np.zeros((3,2))
assert all(np.allclose(a,b) for a,b in zip(signature(excursion),signature(constant)))
print('Trayectorias distintas; misma firma de nivel 2.')
''')
  c.append(md('### Uso y extensiones\n\nÚtil como feature de orden y área en flujos o señales; no es detector de fraude ni reconstructora universal. Antes de ampliar nivel, estudiar muestreo irregular, normalización por escala y fuga temporal. Agregar tiempo como coordenada cambia la representación y requiere otro experimento.'))
 elif index==2:
  c.append(md(r'''### Rangos conformes por canal

$$p(s)=\frac{1+\sum_{i=1}^n1[S_i\ge s]}{n+1},\qquad alerta=1[p(s)\le\alpha].$$

Los empates se cuentan conservadoramente. El score debe estar congelado y la calibración usar casos legítimos aprobados; intercambiabilidad dentro de cada canal permite control marginal de falsas alertas para un nuevo legítimo. Esto no es probabilidad posterior de fraude, control FDR ni garantía bajo drift.'''))
  pair(c,'Resolución mínima y abstención','Con menos de 19 observaciones no puede alertarse al 5% aunque el score nuevo supere a todos.', '''
from src.conformal import TailCalibrator, ChannelCalibrator
resolution=pd.DataFrame({'n':[5,9,18,19,39,99,199]})
resolution['p_min']=1/(resolution.n+1)
resolution['puede_alertar_5pct']=resolution.p_min<=.05
display(resolution)
assert not TailCalibrator([0.]*18).alert(999,.05)
assert TailCalibrator([0.]*19).alert(999,.05)
''')
  pair(c,'Pooling frente a canales heterogéneos','El cambio de mezcla puede ocultar errores por canal. Se mantienen las mismas realizaciones para comparar políticas.', '''
cal_a=rng_depth.normal(0,1,399);cal_b=rng_depth.normal(2,1.4,399)
test_a=rng_depth.normal(0,1,3000);test_b=rng_depth.normal(2,1.4,3000)
pooled=TailCalibrator(np.r_[cal_a,cal_b]);grouped=ChannelCalibrator({'A':list(cal_a),'B':list(cal_b)})
channel_rows=[]
for name,values in [('A',test_a),('B',test_b)]:
    for policy,func in [('pooled',pooled.p_value),('por canal',lambda s:grouped.p_value(name,s))]:
        alerts=np.array([func(v)<=.05 for v in values])
        channel_rows.append({'canal':name,'politica':policy,'FPR':alerts.mean(),'n':len(values)})
channel_table=pd.DataFrame(channel_rows);display(channel_table)
fig,ax=plt.subplots();channel_table.pivot(index='canal',columns='politica',values='FPR').plot.bar(ax=ax,color=[BLUE,GOLD],rot=0)
ax.axhline(.05,color=GRAY,ls='--');ax.set(ylabel='Falsas alertas / legítimos',title='Calibración sobre poblaciones heterogéneas');plt.show()
''')
  pair(c,'Deriva temporal sin recalibración','La garantía depende de la distribución; una transformación monótona común conserva rangos, desplazar solo test no.', '''
shifts=np.linspace(0,2,9)
drift_rates=[np.mean([grouped.p_value('A',v+d)<=.05 for v in test_a]) for d in shifts]
fig,ax=plt.subplots();ax.plot(shifts,drift_rates,'o-',color=BLUE);ax.axhline(.05,color=GRAY,ls='--')
ax.set(xlabel='Desplazamiento test (unidades del score)',ylabel='FPR',title='Umbral congelado ante cambio temporal');plt.show()
assert drift_rates[-1]>drift_rates[0]
''')
  pair(c,'Carga y costo de revisión','Un umbral estadístico no administra capacidad. Este cálculo de cola es un escenario de planeación, no una eficacia observada.', '''
volume=10000;minutes=8;capacity_minutes=1600
loads=pd.DataFrame({'shift':shifts,'FPR':drift_rates})
loads['alertas_esperadas']=volume*loads.FPR
loads['minutos_solicitados']=minutes*loads.alertas_esperadas
loads['minutos_sobre_capacidad']=np.maximum(loads.minutos_solicitados-capacity_minutes,0)
display(loads.round(2))
print('Capacidad de revisiones:',capacity_minutes//minutes)
''')
  pair(c,'Canal desconocido y empates','No usar pooling silencioso ni convertir ausencia de soporte en normalidad.', '''
try:
    grouped.p_value('nuevo',1.)
except KeyError:
    print('Canal nuevo: requiere política explícita y revisión.')
else:
    raise AssertionError('Se esperaba rechazo del canal desconocido')
assert TailCalibrator([1.]*99).p_value(1.)==1.
assert np.isclose(TailCalibrator([1.]*99).p_value(2.),.01)
''')
  c.append(md('### Uso en originación\n\nLa alerta prioriza revisión de consistencia; no decide fraude ni rechazo crediticio por sí sola. La validación siguiente debe usar etiquetas maduras, canales predefinidos y fechas disponibles, medir demora/costo de revisión y distinguir fraude confirmado de falta de documentos.'))
 elif index==3:
  c.append(md(r'''### Conformal ponderado y masa del nuevo punto

Con scores de calibración $s_i$ y razones de densidad $w_i=dQ_X/dP_X(x_i)$:

$$q(x)=Q_{1-\alpha}\left(\sum_i\frac{w_i\delta_{s_i}}{\sum_jw_j+w(x)}+\frac{w(x)\delta_{+\infty}}{\sum_jw_j+w(x)}\right).$$

La masa de test no se elimina. Si $(1-\alpha)(\sum w_i+w(x))>\sum w_i$, el intervalo es infinito. Predictor independiente, razones correctas, solapamiento y distribución $Y|X$ invariante son supuestos esenciales. Cobertura marginal no es cobertura por segmento.'''))
  pair(c,'Cuantil como distribución discreta','Reconstrucción manual pequeña, incluyendo un nuevo punto de peso dominante.', '''
from src.conformal import thresholds, ratios
scores_d=np.array([1.,2.,3.,4.]);weights_d=np.array([1.,1.,2.,2.])
test_weights_d=np.array([.1,2.,20.])
q_d=thresholds(scores_d,weights_d,test_weights_d,alpha=.2)
manual=[]
for wt in test_weights_d:
    target=.8*(weights_d.sum()+wt)
    choices=scores_d[np.cumsum(weights_d)>=target]
    manual.append(choices[0] if len(choices) else np.inf)
assert np.array_equal(q_d,manual)
display(pd.DataFrame({'peso_test':test_weights_d,'q':q_d}))
''')
  pair(c,'Masa infinita y utilidad','El diagnóstico separa cobertura, fracción finita y ancho condicional a ser finito; no sustituir infinito por el mayor score.', '''
scores_d=np.sort(rng_depth.exponential(size=80))
weights_d=rng_depth.lognormal(0,1,size=80)
test_grid=np.geomspace(.01,1000,200)
quantiles_d=thresholds(scores_d,weights_d,test_grid)
fig,ax=plt.subplots();finite=np.isfinite(quantiles_d)
ax.plot(test_grid[finite],quantiles_d[finite],color=BLUE,label='Cuantil finito')
if (~finite).any(): ax.axvline(test_grid[~finite][0],color=GOLD,ls='--',label='Inicio de abstención infinita')
ax.set(xscale='log',xlabel='Peso de test',ylabel='Radio conforme (unidades y)',title='El peso de test puede impedir un intervalo finito');ax.legend();plt.show()
print('Frontera analítica de finitud:', .1/.9*weights_d.sum())
''')
  pair(c,'Invariancia por escala común y ESS','ESS es un diagnóstico de concentración, no un certificado de cobertura. Escalar solo pesos de calibración cambia la política.', '''
base=thresholds(scores_d,weights_d,test_grid)
scaled=thresholds(scores_d,weights_d*17,test_grid*17)
assert np.array_equal(base,scaled)
ess=weights_d.sum()**2/np.sum(weights_d**2)
print({'n_cal':len(weights_d),'ESS':ess,'fraccion_finita_grid':finite.mean()})
''')
  pair(c,'Ablación de pesos mal especificados','Datos nuevos con semilla fija; se perturba la razón oráculo sin ajustar etiquetas de test.', '''
g_cal=rng_depth.random(400)<.1;g_test=rng_depth.random(4000)<.8
s_cal=np.abs(rng_depth.normal(size=400))*np.where(g_cal,5.,1.)
s_test=np.abs(rng_depth.normal(size=4000))*np.where(g_test,5.,1.)
weight_rows=[]
for target_assumed in [.1,.3,.5,.8,.95]:
    wc=ratios(g_cal,.1,target_assumed);wt=ratios(g_test,.1,target_assumed)
    q=thresholds(s_cal,wc,wt)
    is_finite=np.isfinite(q)
    weight_rows.append({'target_asumido':target_assumed,'cobertura':np.mean(s_test<=q),'fraccion_finita':is_finite.mean(),'ancho_finito':2*np.mean(q[is_finite]) if is_finite.any() else np.nan})
weight_table=pd.DataFrame(weight_rows);display(weight_table.round(4))
fig,ax=plt.subplots();ax.plot(weight_table.target_asumido,weight_table.cobertura,'o-',color=BLUE,label='Cobertura')
ax.plot(weight_table.target_asumido,weight_table.fraccion_finita,'s--',color=GOLD,label='Fracción finita');ax.axhline(.9,color=GRAY,ls=':')
ax.set(ylim=(0,1.03),xlabel='Probabilidad de grupo asumida en destino',ylabel='Fracción',title='Sensibilidad a la especificación de pesos');ax.legend();plt.show()
''')
  pair(c,'Cambio condicional','Con los mismos pesos correctos, multiplicar los errores de destino rompe el supuesto de Y dado X invariante.', '''
q_correct=thresholds(s_cal,ratios(g_cal,.1,.8),ratios(g_test,.1,.8))
conditional=pd.DataFrame({'factor_error':[1,1.5,2,3]})
conditional['cobertura']=[np.mean(s_test*factor<=q_correct) for factor in conditional.factor_error]
display(conditional)
assert conditional.cobertura.iloc[-1]<=conditional.cobertura.iloc[0]
''')
  c.append(md('### Uso y arquitectura\n\nIncorporar al monitoreo de modelos cuando las razones sean defendibles y el predictor esté congelado. Registrar cobertura y fracción útil juntas. Antes de conectar una API de decisión, evaluar densidad estimada, error de etiquetas, subgrupos y política de abstención. No transferir la garantía oráculo a pesos aprendidos sin análisis adicional.'))
 elif index==4:
  c.append(md(r'''### Valor de información y decisión de escalar

$$\theta\sim Beta(a,b),\quad K|\theta\sim Binomial(n,\theta),\quad E[\theta|K=k]=(a+k)/(a+b+n).$$

El valor de escalar es $V(\theta)=N(B\theta-c)-F$. La alternativa de no escalar vale cero. El piloto es separado de la población futura y sus costos no incluyen beneficios operacionales propios.

$$EVSI(n)=\sum_{k=0}^nP(K=k)\max\{0,V(E[\theta|k])\}-\max\{0,V(E\theta)\}.$$

$$\Delta(n)=EVSI(n)-C_0-nC_1.$$

Todas las cantidades monetarias usan una misma unidad sintética. Más información puede aumentar EVSI, pero el valor neto puede disminuir.'''))
  pair(c,'Regla de decisión posterior','El umbral económico depende de beneficio, costo y gasto fijo, no de un 50% universal.', '''
from src.evsi import Case, predictive, evaluate, choose
from dataclasses import replace
case_d=Case()
n_d=50
posterior=(case_d.alpha+np.arange(n_d+1))/(case_d.alpha+case_d.beta+n_d)
payoff=np.array([case_d.payoff(p) for p in posterior])
critical=(case_d.unit_cost+case_d.fixed_rollout/case_d.population)/case_d.benefit
print('Umbral de éxito para escalar:',critical)
fig,ax=plt.subplots();ax.plot(np.arange(n_d+1),payoff,color=BLUE);ax.axhline(0,color=GRAY,ls='--')
ax.set(xlabel='Éxitos en piloto de 50',ylabel='Valor esperado al escalar (unidades)',title='Decisión posterior y alternativa de detener');plt.show()
''')
  pair(c,'Reconstrucción de EVSI','Comparación de enumeración manual de estados con la función pública.', '''
mass=np.array(predictive(case_d,n_d))
manual_future=float(mass@np.maximum(payoff,0))
immediate=max(0,case_d.payoff(case_d.alpha/(case_d.alpha+case_d.beta)))
manual_evsi=manual_future-immediate
computed=evaluate(case_d,n_d)
assert abs(manual_evsi-computed['evsi'])<1e-8
assert abs(mass.sum()-1)<1e-12
print({'EVSI_manual':manual_evsi,'costo_piloto':computed['experiment_cost'],'incremento_neto':computed['increment']})
''')
  pair(c,'Diseño discreto y costo marginal','El máximo se restringe al grid mostrado; no es óptimo continuo ni una decisión secuencial.', '''
sizes=list(range(0,301,10))
design_d=pd.DataFrame([evaluate(case_d,n) for n in sizes])
selected=choose(case_d,sizes);display(pd.DataFrame([selected]).round(3))
fig,ax=plt.subplots();ax.plot(design_d.n,design_d.evsi,label='EVSI bruto',color=BLUE)
ax.plot(design_d.n,design_d.increment,label='Incremento neto',color=GOLD,ls='--');ax.axhline(0,color=GRAY,ls=':')
ax.set(xlabel='Tamaño del piloto',ylabel='Valor (unidades sintéticas)',title='Información adicional y costo del experimento');ax.legend();plt.show()
''')
  pair(c,'Prior y escala de despliegue','Cambiar la población futura modifica el valor de aprender. El prior se explicita y no se elige con resultados futuros.', '''
sensitivity_d=[]
for a,b in [(2,8),(6,4),(8,2)]:
    for population in [1000,10000,50000]:
        cc=replace(case_d,alpha=a,beta=b,population=population)
        choice=choose(cc,sizes)
        sensitivity_d.append({'a':a,'b':b,'N':population,'n_elegido':choice['n'],'incremento':choice['increment']})
display(pd.DataFrame(sensitivity_d).round(2))
''')
  pair(c,'Cota de información perfecta','Integración independiente del prior beta. La cota es ex ante, no desempeño observado del producto.', '''
from scipy.integrate import quad
from scipy.stats import beta as beta_dist
evpi_d=quad(lambda theta:max(0,case_d.payoff(theta))*beta_dist.pdf(theta,case_d.alpha,case_d.beta),0,1,points=[critical])[0]-immediate
assert design_d.evsi.min()>-1e-7
assert design_d.evsi.max()<=evpi_d+1e-6
assert evaluate(case_d,0)['increment']==0
print({'EVPI_integracion':evpi_d,'max_EVSI_grid':design_d.evsi.max()})
''')
  c.append(md('### Uso para dirección e innovación\n\nEl criterio compara aprender, escalar y detener con costos explícitos. Separa calidad del experimento de tamaño de mercado y evita imponer un piloto por costumbre. Faltan abandono secuencial, demora, heterogeneidad, competencia y validación del prior; no interpretar el máximo sintético como presupuesto empresarial recomendado.'))
 c.append(md('### Preguntas para extender el estudio\n\n1. ¿Qué supuesto permite el resultado y qué contraejemplo lo destruye?\n2. ¿Qué cambia al separar entrenamiento, calibración y evaluación por fecha?\n3. ¿Qué pérdidas, costos o acciones no están representados?\n4. ¿Qué evidencia real haría abandonar este modelo?\n\nLas salidas anteriores son el resultado de esta ejecución; las pruebas locales no establecen validez empírica.'))
 from research_depth_experiments import experiments
 c.extend(experiments(index,md,code,pair))
 return c


def architecture(index):
 c=[md('# '+('Decisiones tipadas: calibración, abstención y costo' if index==5 else 'Extracción con evidencia: fuente, contradicción y conciliación')),
 md('## Resumen y alcance\n\nLaboratorio de arquitectura con datos sintéticos y sin API comercial. Se ejecutan contratos neutrales y escenarios de error. Las métricas resultantes describen exclusivamente este generador; no son benchmarks de Jev ni ScaleDown.'),
 md('## Contexto y métodos\n\nSe comparan políticas sobre las mismas realizaciones. Semilla 20261023; calibración y test independientes. El objetivo es entender qué capa detecta cada fallo y dónde la abstención preserva incertidumbre.'),code(STYLE),
 code('''
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd().parent))
from src.contracts import Decision, Evidence, choose_action, select_threshold, extract_literal
''')]
 if index==5:
  c.append(md(r'''### Del score a la probabilidad

$$p=\sigma(z),\quad p_T=\sigma(z/T),\quad T>0.$$

En el generador $P(Y=1|z)=\sigma(z)$, pero el proveedor sintético reporta $\sigma(2.4z)$. La temperatura se estima minimizando NLL en calibración. No se modela el entrenamiento de Jev. El score no representa fraude: la tarea es una clasificación binaria abstracta.'''))
  pair(c,'Datos separados por función','Los errores y la confianza salen de un generador conocido; no se elige una semilla para favorecer una política.', '''
from scipy.special import expit
from scipy.optimize import minimize_scalar
n_cal,n_test=5000,8000
z_cal=rng_depth.normal(0,2,n_cal); z_test=rng_depth.normal(0,2,n_test)
y_cal=rng_depth.binomial(1,expit(z_cal));y_test=rng_depth.binomial(1,expit(z_test))
logit_cal=2.4*z_cal;logit_test=2.4*z_test

def nll_logits(logits,y):
    return float(np.mean(np.logaddexp(0,logits)-y*logits))

opt=minimize_scalar(lambda log_t:nll_logits(logit_cal/np.exp(log_t),y_cal),bounds=(-3,3),method='bounded')
assert opt.success
temperature=float(np.exp(opt.x))
p_raw=expit(logit_test);p_calibrated=expit(logit_test/temperature)
print({'n_cal':n_cal,'n_test':n_test,'temperatura_ajustada':temperature,'verdad_generador':2.4})
''')
  pair(c,'Brier, NLL y ranking','Calibrar puede cambiar calidad probabilística sin mejorar clasificación ni ranking. No se asume que siempre mejore test.', '''
from sklearn.metrics import average_precision_score, roc_auc_score
metrics_d=[]
for name,p in [('sin calibrar',p_raw),('temperatura',p_calibrated)]:
    metrics_d.append({'modelo':name,'Brier':np.mean((p-y_test)**2),'NLL':nll_logits(logit_test/(temperature if name=='temperatura' else 1),y_test),'AP':average_precision_score(y_test,p),'AUC':roc_auc_score(y_test,p)})
metrics_d=pd.DataFrame(metrics_d);display(metrics_d.round(5))
assert np.isclose(metrics_d.AUC.iloc[0],metrics_d.AUC.iloc[1])
''')
  pair(c,'Curva de confiabilidad','Cada punto compara media probabilística con frecuencia observada. Grupos vacíos no se dibujan como cero.', '''
fig,ax=plt.subplots()
for name,p,color in [('sin calibrar',p_raw,GOLD),('temperatura',p_calibrated,BLUE)]:
    bins=np.minimum((p*10).astype(int),9)
    means=[];frequencies=[]
    for j in range(10):
        keep=bins==j
        if keep.any():means.append(p[keep].mean());frequencies.append(y_test[keep].mean())
    ax.plot(means,frequencies,'o-',label=name,color=color)
ax.plot([0,1],[0,1],ls='--',color=GRAY,label='Ideal');ax.set(xlabel='Probabilidad media',ylabel='Frecuencia de clase 1',title='Calibración sobre test sintético independiente');ax.legend();plt.show()
''')
  c.append(md(r'''### Selectividad con una cota simultánea

Para cada umbral $t$ se calcula el error entre aceptados. Sobre un grid fijo de $K=50$:

$$U_t=\widehat r_t+\sqrt{\frac{\log(K/\delta)}{2n_t}}.$$

La política elige la mayor cobertura con $U_t\le r_{max}$. La muestra usada para ajustar temperatura se divide nuevamente: el ajuste usa una mitad y la selección del umbral otra. La cota requiere ejemplos IID y reglas fijas antes de observar las etiquetas de selección.'''))
  pair(c,'Ajuste separado de selección','La temperatura anterior era diagnóstico. Se vuelve a ajustar solo con la primera mitad para seleccionar el umbral en la segunda.', '''
half=n_cal//2
opt_sel=minimize_scalar(lambda lt:nll_logits(logit_cal[:half]/np.exp(lt),y_cal[:half]),bounds=(-3,3),method='bounded')
temp_sel=np.exp(opt_sel.x)
p_select=expit(logit_cal[half:]/temp_sel)
conf_select=np.maximum(p_select,1-p_select)
correct_select=((p_select>=.5)==y_cal[half:])
count,threshold,upper=select_threshold(conf_select,correct_select,max_error=.15)
p_test_sel=expit(logit_test/temp_sel)
conf_test=np.maximum(p_test_sel,1-p_test_sel)
correct_test=((p_test_sel>=.5)==y_test)
keep=conf_test>=threshold
print({'umbral':threshold,'cal_aceptados':count,'cota_cal':upper,'cobertura_test':keep.mean(),'error_test_aceptados':float((~correct_test[keep]).mean()) if keep.any() else None})
''')
  pair(c,'Frontera riesgo y cobertura','El test evalúa un umbral congelado; no se usa para seleccionarlo. Error condicional entre aceptados no equivale a error sobre toda la población.', '''
risk_rows=[]
for t in np.linspace(.5,.99,50):
    selected=conf_test>=t
    if selected.any():risk_rows.append((selected.mean(),(~correct_test[selected]).mean()))
risk_rows=np.array(risk_rows)
fig,ax=plt.subplots();ax.plot(risk_rows[:,0],risk_rows[:,1],color=BLUE)
ax.set(xlabel='Fracción aceptada',ylabel='Error entre aceptados',title='Frontera riesgo-cobertura sobre test');plt.show()
''')
  pair(c,'Fallback imperfecto y errores correlacionados','Derivar no garantiza acierto. Comparamos escenarios con 3% de error independiente o errores compartidos.', '''
error_specialist=~correct_test
fallback_independent=rng_depth.random(n_test)<.03
fallback_correlated=(error_specialist & (rng_depth.random(n_test)<.6)) | (rng_depth.random(n_test)<.01)
fallback_rows=[]
for name,error in [('independiente',fallback_independent),('correlacionado',fallback_correlated)]:
    final_error=np.where(keep,error_specialist,error)
    fallback_rows.append({'fallback':name,'error_global':final_error.mean(),'derivacion':(~keep).mean()})
display(pd.DataFrame(fallback_rows))
''')
  c.append(md(r'''### Costo esperado por acción

$$C(a|p)=pL(1-q_a)+c_a+(1-p)f_a.$$

Severidad $L=100$, eficacia asumida $q$, costo directo $c$ y fricción legítima $f$ comparten unidades. El ejemplo no estima eficacia causal ni usa importes reales. La acción es una recomendación simulada; no hay rechazo o bloqueo externo.'''))
  pair(c,'Política económica y umbral fijo','Se contrasta el costo real simulado bajo la misma etiqueta y eficacia esperada por clase, no solo número de alertas.', '''
loss=np.full(3,100.);efficacy=np.array([0,.6,.9]);cost=np.array([0,2,8]);friction=np.array([0,1,10])
actions=np.array([choose_action(float(p),loss,efficacy,cost,friction)[0] for p in p_calibrated])
fixed=np.where(p_calibrated>.5,2,0)
policy_rows=[]
for name,a in [('continuar',np.zeros(n_test,dtype=int)),('umbral .5',fixed),('costo esperado',actions)]:
    realized=y_test*loss[a]*(1-efficacy[a])+cost[a]+(1-y_test)*friction[a]
    policy_rows.append({'politica':name,'costo_medio':realized.mean(),'fraccion_intervenida':np.mean(a!=0)})
policy_table=pd.DataFrame(policy_rows);display(policy_table.round(4))
fig,ax=plt.subplots();ax.barh(policy_table.politica,policy_table.costo_medio,color=BLUE);ax.set(xlabel='Costo medio (unidades sintéticas)',title='Políticas sobre las mismas etiquetas');plt.show()
''')
  pair(c,'Cambio condicional después de calibrar','Una inversión parcial de etiquetas conserva el contrato de salida pero deteriora la validez probabilística.', '''
y_shift=y_test.copy();flip=rng_depth.random(n_test)<.2;y_shift[flip]=1-y_shift[flip]
print({'Brier_base':float(np.mean((p_calibrated-y_test)**2)),'Brier_shift':float(np.mean((p_calibrated-y_shift)**2)),
       'riesgo_selectivo_shift':float(np.mean((p_test_sel[keep]>=.5)!=y_shift[keep])) if keep.any() else None})
valid_but_wrong=Decision(('clase0','clase1'),(.01,.99),'fixture-v1')
assert valid_but_wrong.probabilities[1]==.99
print('Contrato válido; ninguna garantía de verdad individual.')
''')
  pair(c,'Sensibilidad de eficacia','Una política óptima bajo eficacia supuesta puede deteriorarse si la intervención funciona menos de lo esperado.', '''
stress=[]
for multiplier in [0,.25,.5,.75,1.]:
    realized=y_test*loss[actions]*(1-efficacy[actions]*multiplier)+cost[actions]+(1-y_test)*friction[actions]
    stress.append({'factor_eficacia':multiplier,'costo_politica_congelada':realized.mean()})
display(pd.DataFrame(stress).round(3))
''')
  c.append(md('## Hallazgos y uso\n\nLas tablas y curvas anteriores muestran por separado calibración, cobertura, errores y costo. La temperatura no cambia AUC; el fallback correlacionado y el cambio condicional exponen fallos que un esquema válido no detecta. Adoptar una API comercial exigiría repetir estas comparaciones con respuestas reales, etiquetas maduras, costos medidos e intervalos de incertidumbre.'))
 else:
  c.append(md(r'''### Evidencia literal y semántica

$$v=s[a:b],\quad h=SHA256(UTF8(s)).$$

La igualdad del span prueba procedencia literal sobre este snapshot; no acredita que sea ingreso ni que el documento sea auténtico. Los offsets se expresan en puntos de código Unicode, no bytes.'''))
  pair(c,'Corpus de documentos y verdad de referencia','Cada caso incluye ingreso declarado, transferencia y corrección. El dataset es completamente sintético y explícito.', '''
import hashlib
from dataclasses import replace
records=[]
for i in range(200):
    salary=int(rng_depth.integers(1,9))*1000000
    transfer=int(rng_depth.integers(1,5))*1000000
    text=f'Expediente {i}. Salario mensual: {salary} COP. Transferencia interna: {transfer} COP. No sumar la transferencia al ingreso. Café.'
    records.append({'id':i,'source':text,'salary':salary,'transfer':transfer})
display(pd.DataFrame(records)[['id','salary','transfer']].head())
''')
  pair(c,'Extracción con spans y ambigüedad','El doble de prueba encuentra solo valores únicos. Una repetición requiere desambiguar por contexto en lugar de escoger la primera coincidencia.', '''
receipts=[]
for record in records:
    literal=str(record['salary'])
    evidence=extract_literal(record['source'],literal)
    receipts.append({'id':record['id'],'evidence':evidence,'verified':bool(evidence and evidence.verify(record['source']))})
print({'casos':len(records),'evidencias_verificadas':sum(r['verified'] for r in receipts),'abstenciones':sum(r['evidence'] is None for r in receipts)})
assert extract_literal('100 y 100','100') is None
''')
  pair(c,'Cambios de fuente, offsets y Unicode','El hash exige texto inmutable. Normalizar acentos o espacios crea una nueva versión y requiere recalcular offsets.', '''
source='Café: salario 3000000 COP.'
evidence=extract_literal(source,'3000000')
assert evidence.verify(source)
assert not evidence.verify(source+' ')
assert not replace(evidence,start=evidence.start+1).verify(source)
assert evidence.start!=len(source[:evidence.start].encode('utf-8'))
print({'offset_unicode':evidence.start,'offset_bytes':len(source[:evidence.start].encode('utf-8')),'hash':evidence.document_hash[:16]})
''')
  pair(c,'Matriz de fallos de contrato','No se reporta tasa de seguridad: son cinco mutaciones dirigidas y reproducibles, no ataques muestreados de población.', '''
mutations=[('original',evidence,source),('fuente alterada',evidence,source+' '),
           ('valor inventado',replace(evidence,value='999'),source),('offset incorrecto',replace(evidence,end=evidence.end-1),source),
           ('hash incorrecto',replace(evidence,document_hash='0'*64),source)]
mutation_table=pd.DataFrame([{'caso':name,'aceptado':e.verify(s)} for name,e,s in mutations]);display(mutation_table)
assert mutation_table.aceptado.sum()==1
''')
  c.append(md(r'''### Conciliación del ingreso

$$I_m=\sum_e monto_e\,f_e\,1[e\text{ es ingreso externo único}].$$

Se conserva período y concepto. En este corpus el salario es mensual y las transferencias son internas; la suma indiscriminada sobreestima el ingreso. No se infiere capacidad de pago o solvencia solo por el documento.'''))
  pair(c,'Suma de movimientos frente a ingreso','La misma cifra puede tener fuente verificable y pertenecer al concepto equivocado.', '''
salary=np.array([x['salary'] for x in records]);transfer=np.array([x['transfer'] for x in records])
naive=salary+transfer
semantic_error=transfer # flujo real, concepto incorrecto
assert np.all(naive>=salary)
print({'sobreestimacion_media_COP':float(np.mean(naive-salary)), 'ratio_mediano':float(np.median(naive/salary))})
fig,ax=plt.subplots();ax.scatter(salary/1e6,naive/1e6,alpha=.35,color=BLUE);ax.plot([0,14],[0,14],ls='--',color=GRAY)
ax.set(xlabel='Salario verdadero (millones COP)',ylabel='Suma indiscriminada (millones COP)',title='Procedencia correcta con concepto incorrecto');plt.show()
''')
  pair(c,'Normalización de periodicidad','Las conversiones son convenciones explícitas. Quincenal (24 pagos/año) difiere de cada 14 días (365.25/14 pagos/año).', '''
factors={'mensual':1.,'anual':1/12,'semanal':365.25/7/12,'quincenal':2.,'cada_14_dias':365.25/14/12}
periods=pd.DataFrame({'periodo':list(factors),'factor_mensual':list(factors.values())})
periods['monto_literal_COP']=1500000
periods['equivalente_mensual_COP']=periods.factor_mensual*periods.monto_literal_COP
display(periods.round(2))
assert factors['quincenal']!=factors['cada_14_dias']
''')
  pair(c,'Compresión antes de extraer','Se evalúa una ablación deliberadamente simple: conservar el prefijo elimina correcciones al final. No es una implementación de ScaleDown Compress.', '''
docs=[]
for i in range(100):
    original=2000000+i*1000
    correction=original+500000
    text=f'Ingreso reportado {original} COP. '+'Contexto administrativo. '*10+f'Corrección final: ingreso válido {correction} COP.'
    docs.append((text,str(correction)))
retention=[]
for chars in [40,100,200,400,800]:
    retained=np.mean([truth in text[:chars] for text,truth in docs])
    retention.append({'limite_caracteres':chars,'retencion_evidencia':retained,'longitud_media':np.mean([len(t[:chars]) for t,_ in docs])})
retention=pd.DataFrame(retention);display(retention)
fig,ax=plt.subplots();ax.plot(retention.longitud_media,retention.retencion_evidencia,'o-',color=BLUE)
ax.set(ylim=(-.03,1.03),xlabel='Caracteres retenidos, media',ylabel='Fracción con corrección preservada',title='La reducción de longitud puede eliminar evidencia');plt.show()
''')
  pair(c,'Span válido con etiqueta errónea','Se construye un campo salario que apunta a una transferencia real. El contrato literal pasa; la regla semántica debe detectarlo.', '''
text='Salario: 3000000 COP. Transferencia: 9000000 COP.'
wrong=extract_literal(text,'9000000')
assert wrong.verify(text)
semantic_label='salario'
correct_label='transferencia'
assert semantic_label!=correct_label
print('Procedencia literal: válida; etiqueta de concepto: incorrecta.')
''')
  pair(c,'Desconocidos y revisión','Calcular una señal solo cuando existen campos suficientes. No convertir None en cero.', '''
fields=[{'salary':3000000,'period':'mensual'}, {'salary':None,'period':'mensual'}, {'salary':3000000,'period':None}]
def normalize_or_review(field):
    if field['salary'] is None or field['period'] not in factors:return {'status':'review','income':None}
    return {'status':'ready','income':field['salary']*factors[field['period']]}
decisions=[normalize_or_review(x) for x in fields];display(pd.DataFrame(decisions))
assert decisions[1]['income'] is None and decisions[2]['income'] is None
''')
  pair(c,'Costo de revisión y pérdida por automatizar','Superficie de escenario: no se estima causalmente el costo ni la eficacia de la revisión.', '''
error_rates=np.array([.01,.05,.1,.2]);review_costs=np.array([1,5,10,20])
loss_per_error=100.
expected_auto=error_rates*loss_per_error
cost_matrix=np.minimum(expected_auto[:,None],review_costs[None,:])
fig,ax=plt.subplots();im=ax.imshow(cost_matrix,origin='lower',aspect='auto',cmap='Blues',vmin=0,vmax=20)
ax.set_xticks(range(4),review_costs);ax.set_yticks(range(4),error_rates)
for i in range(4):
    for j in range(4):ax.text(j,i,f'{cost_matrix[i,j]:.0f}',ha='center',va='center',color='white' if cost_matrix[i,j]>12 else 'black')
ax.set(xlabel='Costo de revisión perfecta supuesto',ylabel='Probabilidad de error supuesta',title='Mínimo costo esperado por caso (unidades)');fig.colorbar(im,ax=ax,label='Costo');plt.show()
''')
  c.append(md('## Hallazgos y uso\n\nLa validación literal detecta cambios de documento y spans inventados, pero el contraejemplo semántico pasa. La compresión por prefijo pierde correcciones y las transferencias inflan ingreso al sumarlas. Estos resultados justifican conservar fuente, separar concepto y mantener revisión; no acreditan un extractor comercial o un motor crediticio.'))
 from research_depth_experiments import experiments
 c.extend(experiments(index,md,code,pair))
 c.append(md('## Próximos experimentos\n\nComparar proveedores sobre corpus etiquetado y snapshots iguales; registrar versión y latencia medida. Añadir OCR real aprobado, idioma, distribución temporal y revisores falibles. Diseñar pruebas de integración antes de conectar efectos externos.\n\nFuentes y contrato de arquitectura: [README principal](../README.md).'))
 return c


def extend(path):
 p=Path(path).resolve()
 if p not in TARGETS: raise ValueError('Notebook fuera del alcance de esta ampliación')
 i=TARGETS.index(p)
 if i>=5:
    nb=nbf.v4.new_notebook(cells=architecture(i))
 else:
    nb=nbf.read(p,as_version=4)
    nb.cells=[x for x in nb.cells if not x.metadata.get('research_depth_20261023') and not x.metadata.get('depth_summary')]
    for cell in extensions(i):
        cell.metadata['research_depth_20261023']=True; nb.cells.append(cell)
 from academic_20261023 import sections
 for cell in sections(i,md,code,pair):
    cell.metadata['research_depth_20261023']=True;nb.cells.append(cell)
 nb.metadata['kernelspec']={'display_name':'Python 3','language':'python','name':'python3'}
 nb.metadata['language_info']={'name':'python','version':'3.12'}
 nb.metadata['depth_revision']='2026-10-23-academic-v2'
 for position,cell in enumerate(nb.cells):
    if i>=5 or cell.metadata.get('research_depth_20261023'):
        cell.id=hashlib.sha256((str(p.relative_to(ROOT))+str(position)+cell.source).encode()).hexdigest()[:12]
 nbf.validate(nb);p.parent.mkdir(parents=True,exist_ok=True);nbf.write(nb,p)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--path');args=parser.parse_args()
 for target in ([Path(args.path)] if args.path else TARGETS): extend(target)
