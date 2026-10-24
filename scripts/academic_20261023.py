"""Paper-linked, bounded experiments. Rebuilt into the seven dated notebooks."""
def sections(index,md,code,pair):
 c=[md('## Ampliación académica: literatura, fórmulas y experimento\n\nConsulta bibliográfica del 23 de octubre de 2026. Se distingue método publicado, derivación propia y experimento sintético. El [mapa bibliográfico](https://github.com/Jose85100/Portafolio/blob/research/2026-10-23-multi-domain-cycle/reviews/2026-10-23-academic/README.md) en la raíz del repositorio registra publicaciones, acceso y brechas; las fuentes específicas se enlazan debajo.')]
 if index==0:
  c.append(md(r'''### Inversión algebraica de Anderson–Rubin

Base: [Anderson y Rubin, 1949](https://www.jstor.org/stable/2236803). Alternativa pendiente: [Moreira, Econometrica 2003](https://doi.org/10.1111/1468-0262.00438). No se implementa CLR ni se atribuye a CLR la siguiente inversión de AR.

Con variables centradas, $r_b=y-bx$, $P_z=zz'/z'z$, $M_z=I-P_z$ y $c=F^{-1}_{1,n-2}(1-\alpha)$:

$$\mathcal C_{AR}=\{b:(n-2)r_b'P_zr_b-c\,r_b'M_zr_b\le0\}.$$

Equivale a $Ab^2+Bb+C\le0$. Para $h=n-2+c$:

$$A=h(z'x)^2/(z'z)-cx'x,$$
$$B=-2h(z'y)(z'x)/(z'z)+2cy'x,\quad C=h(z'y)^2/(z'z)-cy'y.$$

Esta es nuestra expansión algebraica del test. La aceptación puede ser un intervalo, dos rayos, toda la recta o vacío. Las raíces numéricas no son un certificado de aritmética exacta.'''))
  pair(c,'Topología del conjunto, sin truncarlo al grid','Se inspeccionan todas las raíces reales. Casos casi degenerados requieren diagnóstico de precisión y no se etiquetan como intervalos regulares.', '''
from scipy.stats import f as f_distribution
paper_rng=np.random.default_rng(2301)
def ar_polynomial(y,x,z,alpha=.05):
    yy,xx,zz=[v-np.mean(v) for v in (y,x,z)]
    critical=f_distribution.ppf(1-alpha,1,len(y)-2)
    h=len(y)-2+critical
    zy=float(zz@yy);zx=float(zz@xx);z2=float(zz@zz)
    return np.array([h*zx*zx/z2-critical*float(xx@xx),
                     -2*h*zy*zx/z2+2*critical*float(yy@xx),
                     h*zy*zy/z2-critical*float(yy@yy)])

def quadratic_topology(coef):
    a,b,c=coef
    scale=max(1.,float(np.max(np.abs(coef))))
    if abs(a)<1e-12*scale:return 'degenerado: revisar',[]
    discriminant=b*b-4*a*c
    if discriminant<0:return ('recta completa' if a<0 else 'vacio'),[]
    roots=np.sort(np.roots(coef).real)
    return ('intervalo' if a>0 else 'dos rayos'),roots.tolist()

poly_rows=[]
for strength in [0.,1.,8.]:
    yy,xx,zz=sample(312,150,strength)
    coef=ar_polynomial(yy,xx,zz)
    topology,roots=quadratic_topology(coef)
    comparison=np.r_[np.linspace(-20,20,400),[-1e6,1e6]]
    via_poly=np.polyval(coef,comparison)<=0
    via_test=np.array([ar_pvalue(yy,xx,zz,b)>=.05 for b in comparison])
    assert np.array_equal(via_poly,via_test)
    poly_rows.append({'strength':strength,'topologia':topology,'raices':roots})
display(pd.DataFrame(poly_rows))
''')
  pair(c,'Verificación aleatoria y raíces fuera del rango visible','Se comparan decisiones algebraicas y p-valores en 30 muestras nuevas; no se confunde un extremo del gráfico con un límite de confianza.', '''
agreements=0
for seed in range(30):
    yy,xx,zz=sample(1000000+seed,80,seed%5)
    coef=ar_polynomial(yy,xx,zz)
    candidates=paper_rng.uniform(-50,50,50)
    direct=np.array([ar_pvalue(yy,xx,zz,b)>=.05 for b in candidates])
    assert np.array_equal(np.polyval(coef,candidates)<=0,direct)
    agreements+=len(candidates)
print('Decisiones contrastadas:',agreements)
import json
print('ACADEMIC_METRICS:'+json.dumps({'AR_polynomial_decisions_checked':agreements,'topologies':[x['topologia'] for x in poly_rows]}))
''')
  c.append(md('### Qué falta para completar esta línea\n\nLa inversión anterior cierra la limitación del grid para este modelo. Siguen pendientes CLR, varios instrumentos, robustez HAC/clustering, potencia bajo alternativas y una aplicación con exclusión defendible. La lectura de Moreira se verificó en metadatos y resumen editorial; no se reprodujo su algoritmo.'))
 elif index==1:
  c.append(md(r'''### Lead–lag para conservar variación cuadrática discreta

Fuente publicada: [Chevyrev y Kormilitzin, Springer Finance, 2025, §3.1.14](https://doi.org/10.1007/978-3-031-97239-3_1), desarrollo del preprint de 2016. Es un capítulo académico publicado, no un artículo de revista de 2016.

Para la secuencia $x_0,\ldots,x_n$, usamos los vértices $(x_i,x_i)\to(x_{i+1},x_i)\to(x_{i+1},x_{i+1})$:

$$2A_{lead,lag}=\sum_{i=0}^{n-1}(x_{i+1}-x_i)^2.$$

El factor dos depende de definir $A=(S^2_{12}-S^2_{21})/2$. Es variación realizada sobre la malla observada, no varianza muestral ni recuperación de incrementos no observados.'''))
  pair(c,'Identidad con la implementación de firma existente','Se construye el embedding y se contrasta con la suma directa, sin introducir una biblioteca externa de firmas.', '''
def lead_lag(values):
    values=np.asarray(values,float)
    if values.ndim!=1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('finite scalar sequence required')
    vertices=[[values[0],values[0]]]
    for old,new in zip(values[:-1],values[1:]):
        vertices.extend([[new,old],[new,new]])
    return np.asarray(vertices)

paper_rng=np.random.default_rng(2302)
identity_errors=[]
for n in [1,4,16,64,256]:
    for repeat in range(20):
        stream=np.r_[0,np.cumsum(paper_rng.normal(size=n))]
        signature_value=2*signed_area(lead_lag(stream))
        direct_value=np.sum(np.diff(stream)**2)
        identity_errors.append(abs(signature_value-direct_value))
assert max(identity_errors)<1e-9
print('Error máximo de identidad:',max(identity_errors))
''')
  pair(c,'Misma variación, menor frecuencia de muestreo','Una sola realización no garantiza monotonía al agregar incrementos. Se muestran cuantiles Monte Carlo y no bandas de confianza de una volatilidad financiera.', '''
qv_rows=[]
for repeat in range(150):
    stream=np.r_[0,np.cumsum(paper_rng.normal(0,1/np.sqrt(256),256))]
    for step in [1,2,4,8,16,32]:
        sampled=stream[::step]
        qv_rows.append({'paso':step,'QV':2*signed_area(lead_lag(sampled))})
qv_table=pd.DataFrame(qv_rows)
summary_qv=qv_table.groupby('paso').QV.agg(['mean','std'])
display(summary_qv.round(4))
fig,ax=plt.subplots()
for q,style in [(.1,'--'),(.5,'-'),(.9,':')]:
    v=qv_table.groupby('paso').QV.quantile(q)
    ax.plot(v.index,v.values,ls=style,marker='o',label=f'Cuantil {q:g}')
ax.axhline(1,color=GRAY,ls='-.',label='E[QV] del generador')
ax.set(xlabel='Paso de submuestreo',ylabel='Variación realizada',title='Lead–lag conserva la malla observada, no la ausente')
ax.legend();plt.show()
import json
print('ACADEMIC_METRICS:'+json.dumps({'lead_lag_checks':len(identity_errors),'max_identity_error':float(max(identity_errors))}))
''')
  c.append(md('### Ideas y criterio de cierre\n\nExtender a covariación multicanal, comparar con sumas realizadas directas y ajustar un clasificador con separación temporal. La identidad no demuestra que firmas predigan mejor; tampoco reemplaza corrección de microestructura en precios reales.'))
 elif index==2:
  c.append(md(r'''### De falsas alertas individuales a FDR del lote

[Benjamini y Yekutieli, Annals of Statistics, 2001](https://doi.org/10.1214/aos/1013699998). Para p-valores marginalmente válidos, BY permite dependencia arbitraria:

$$k^*=\max\{k:p_{(k)}\le kq/(mH_m)\},\quad H_m=\sum_{j=1}^m1/j.$$

$$FDR=E[V/\max(R,1)].$$

BH omite $H_m$ y requiere supuestos adicionales de dependencia; Bonferroni controla otro objetivo, FWER. Ninguno transforma anomalías en fraude confirmado. Se trata de lotes fijos, no control online ilimitado.'''))
  pair(c,'Comparadores y oráculo de frontera','Los empates se incluyen. La prueba mínima contrasta umbrales conocidos y preserva la correspondencia con cada caso.', '''
def step_up(pvalues,q=.05,by=False):
    pvalues=np.asarray(pvalues,float)
    m=len(pvalues)
    order=np.argsort(pvalues)
    harmonic=np.sum(1/np.arange(1,m+1)) if by else 1.
    thresholds=q*np.arange(1,m+1)/(m*harmonic)
    eligible=np.flatnonzero(pvalues[order]<=thresholds)
    reject=np.zeros(m,dtype=bool)
    if len(eligible):reject=pvalues<=pvalues[order[eligible[-1]]]
    return reject

assert np.array_equal(step_up([.001,.02,.8]),[True,True,False])
assert not step_up([.1,.5,.9]).any()
''')
  pair(c,'Calibración compartida y dependencia entre alertas','Se regeneran calibración y lote por réplica. Cada legítimo comparte su marginal normal con calibración, pero los casos de test tienen un factor común; no se supone PRDS para defender BH.', '''
paper_rng=np.random.default_rng(2303)
batch_rows=[]
m=100;n_calibration=1999
for correlation in [0.,.7]:
    for repeat in range(200):
        reference=np.sort(paper_rng.normal(size=n_calibration))
        common=paper_rng.normal()
        scores=np.sqrt(correlation)*common+np.sqrt(1-correlation)*paper_rng.normal(size=m)
        truth=np.arange(m)>=90
        scores[truth]+=4.
        pvals=(1+n_calibration-np.searchsorted(reference,scores,side='left'))/(n_calibration+1)
        policies={'individual':pvals<=.05,'Bonferroni':pvals<=.05/m,
                  'BH':step_up(pvals),'BY':step_up(pvals,by=True)}
        for name,rejected in policies.items():
            discoveries=int(rejected.sum())
            false=int(np.sum(rejected & ~truth))
            batch_rows.append({'rho':correlation,'policy':name,'FDP':false/max(discoveries,1),
                               'power':float(np.sum(rejected & truth)/truth.sum()),'R':discoveries})
batch_table=pd.DataFrame(batch_rows)
batch_summary=batch_table.groupby(['rho','policy']).agg(FDR=('FDP','mean'),MCSE=('FDP',lambda x:x.std(ddof=1)/np.sqrt(len(x))),power=('power','mean'),alerts=('R','mean'))
display(batch_summary.round(4))
fig,ax=plt.subplots()
for j,(rho,g) in enumerate(batch_summary.groupby(level='rho')):
    labels=g.index.get_level_values('policy')
    ax.errorbar(np.arange(len(g))+(j-.5)*.15,g.FDR,yerr=[np.minimum(g.FDR,1.96*g.MCSE),np.minimum(1-g.FDR,1.96*g.MCSE)],fmt=['o','s'][j],capsize=3,label=f'rho={rho:g}')
ax.set_xticks(range(len(labels)),labels);ax.axhline(.05,color=GRAY,ls='--')
ax.set(ylabel='FDR e intervalo normal MC 95% truncado a [0,1]',title='Objetivos distintos: caso individual y lote')
ax.legend();plt.show()
import json
print('ACADEMIC_METRICS:'+json.dumps({'batch_replicates':400,'BY_FDR_by_rho':batch_summary.xs('BY',level='policy').FDR.to_dict()}))
''')
  c.append(md('### Ideas y cierre pendiente\n\nEstudiar FDR online, etiquetas retrasadas y calibración contaminada. La simulación ilustra potencia/costo de BY; no prueba el teorema ni valida p-valores de una cartera real. La validez marginal debe verificarse antes de controlar multiplicidad.'))
 elif index==3:
  c.append(md(r'''### Conformalized Quantile Regression para anchos heterogéneos

[Romano, Patterson y Candès, NeurIPS 2019, §2](https://proceedings.neurips.cc/paper/2019/file/5103c3584b063c431bd1268e9b5e76fb-Paper.pdf). Con cuantiles entrenados fuera de calibración:

$$s_i=\max\{\widehat q_{lo}(x_i)-y_i,\ y_i-\widehat q_{hi}(x_i)\},$$
$$\widehat C(x)=[\widehat q_{lo}(x)-Q,\widehat q_{hi}(x)+Q],\quad k=\lceil(n+1)(1-\alpha)\rceil.$$

Aquí usamos $s_i^+=\max(0,s_i)$: variante conservadora que solo ensancha. No es la variante de shrinkage del artículo. El experimento es IID heterocedástico; no se le transfiere la garantía de covariate shift del laboratorio original.'''))
  pair(c,'Entrenamiento, calibración y test separados','Se ajustan tres boosters en train: media y cuantiles 5%/95%. El test se usa exclusivamente para medir.', '''
from sklearn.ensemble import GradientBoostingRegressor
paper_rng=np.random.default_rng(2304)
def hetero_data(n):
    x=paper_rng.uniform(-2,2,n)
    y=np.sin(x)+(.15+.7*np.abs(x))*paper_rng.normal(size=n)
    return x[:,None],y
X_train,Y_train=hetero_data(1500)
X_cal,Y_cal=hetero_data(600)
X_eval,Y_eval=hetero_data(3000)
models_paper={}
for name,loss,quantile in [('mean','squared_error',.5),('low','quantile',.05),('high','quantile',.95)]:
    model=GradientBoostingRegressor(loss=loss,alpha=quantile,n_estimators=80,max_depth=2,random_state=23)
    models_paper[name]=model.fit(X_train,Y_train)

def bands(x):
    low=models_paper['low'].predict(x);high=models_paper['high'].predict(x)
    return np.minimum(low,high),np.maximum(low,high)

low_c,high_c=bands(X_cal)
cqr_scores=np.maximum(0,np.maximum(low_c-Y_cal,Y_cal-high_c))
abs_scores=np.abs(Y_cal-models_paper['mean'].predict(X_cal))
k=int(np.ceil((len(Y_cal)+1)*.9))
q_cqr=np.partition(cqr_scores,k-1)[k-1]
q_abs=np.partition(abs_scores,k-1)[k-1]
lo_e,hi_e=bands(X_eval)
lo_e=lo_e-q_cqr;hi_e=hi_e+q_cqr
mean_e=models_paper['mean'].predict(X_eval)
''')
  pair(c,'Cobertura y ancho por región','La cobertura marginal no equivale a cobertura en cada región. Se conserva el baseline simétrico y no se exige que CQR gane siempre.', '''
cqr_rows=[]
for name,lo,hi in [('simetrico',mean_e-q_abs,mean_e+q_abs),('CQR_positive',lo_e,hi_e)]:
    for region,mask in [('todos',np.ones(len(Y_eval),bool)),('central',np.abs(X_eval[:,0])<.6),('extremo',np.abs(X_eval[:,0])>1.4)]:
        cqr_rows.append({'method':name,'region':region,'n':int(mask.sum()),
                         'coverage':float(np.mean((Y_eval[mask]>=lo[mask])&(Y_eval[mask]<=hi[mask]))),
                         'mean_width':float(np.mean(hi[mask]-lo[mask]))})
cqr_table=pd.DataFrame(cqr_rows);display(cqr_table.round(4))
order=np.argsort(X_eval[:,0])[::20]
fig,ax=plt.subplots()
ax.scatter(X_eval[::15,0],Y_eval[::15],s=8,color=GRAY,alpha=.25,label='Test sintético')
ax.fill_between(X_eval[order,0],lo_e[order],hi_e[order],color=BLUE,alpha=.2,label='CQR ensanchado')
ax.plot(X_eval[order,0],mean_e[order]+q_abs,color=GOLD,ls='--',label='Simétrico')
ax.plot(X_eval[order,0],mean_e[order]-q_abs,color=GOLD,ls='--')
ax.set(xlabel='Covariable x',ylabel='Respuesta e intervalo',title='Adaptación del ancho a heterocedasticidad')
ax.legend();plt.show()
import json
print('ACADEMIC_METRICS:'+json.dumps({'CQR':cqr_table[cqr_table.region=='todos'].to_dict(orient='records')}))
''')
  c.append(md(r'''### Próximas líneas: adaptación temporal

[Gibbs y Candès, NeurIPS 2021, ecuación 2](https://proceedings.neurips.cc/paper/2021/file/0d441de75945e5acbc865406fc9a2559-Paper.pdf): $\alpha_{t+1}=\alpha_t+\gamma(\alpha-err_t)$. La evaluación requiere observar la etiqueta después de predecir y distinguir frecuencia temporal de cobertura condicional. Su ampliación [JMLR 2024](https://jmlr.org/papers/v25/22-1218.html) adapta el paso. Se documentan como próximos experimentos; no se afirma haber implementado ACI.'''))
 elif index==4:
  c.append(md(r'''### Piloto secuencial: detener, escalar o seguir aprendiendo

Marco de utilidad esperada: [Chaloner y Verdinelli, Statistical Science 1995](https://doi.org/10.1214/ss/1177009939). La recursión finita que sigue es una aplicación propia del principio de Bellman al modelo existente, no una reproducción de un algoritmo del artículo.

$$W(a,b,h)=\max\{0,V(a/(a+b)),\ -c_s+\tfrac{a}{a+b}W(a+1,b,h-1)+\tfrac{b}{a+b}W(a,b+1,h-1)\}.$$

Para $h=0$ solo se puede detener o escalar. El costo de apertura se descuenta una sola vez en la raíz. Los sujetos del piloto son separados de la población futura; no hay beneficio durante experimentación.'''))
  pair(c,'Programación dinámica finita con memoización','Se incluye siempre no estudiar. El horizonte máximo es 30 observaciones; el estado es posterior beta más presupuesto restante.', '''
from functools import lru_cache
case_seq=Case(experiment_fixed=20.,experiment_unit=20.)
@lru_cache(None)
def sequential_value(a,b,remaining):
    stop=max(0.,case_seq.payoff(a/(a+b)))
    if remaining==0:return stop
    continuation=-case_seq.experiment_unit+(a/(a+b))*sequential_value(a+1,b,remaining-1)+(b/(a+b))*sequential_value(a,b+1,remaining-1)
    return max(stop,continuation)

horizon=30
immediate_seq=max(0.,case_seq.payoff(case_seq.alpha/(case_seq.alpha+case_seq.beta)))
seq_net=max(immediate_seq,sequential_value(case_seq.alpha,case_seq.beta,horizon)-case_seq.experiment_fixed)
fixed_grid=list(range(horizon+1))
fixed_best=choose(case_seq,fixed_grid)
assert seq_net>=fixed_best['net_value']-1e-7
assert sequential_value(case_seq.alpha,case_seq.beta,0)==immediate_seq
print({'secuencial_neto':seq_net,'mejor_fijo_neto':fixed_best['net_value'],'ventaja':seq_net-fixed_best['net_value']})
''')
  pair(c,'Mapa de continuación según éxitos acumulados','Las decisiones se calculan antes de observar resultados futuros. El experimento sintético no evalúa sesgo de selección de usuarios o efectos de demorar el lanzamiento.', '''
state_rows=[]
for observed in range(horizon+1):
    for successes in range(observed+1):
        a=case_seq.alpha+successes;b=case_seq.beta+observed-successes
        stop=max(0.,case_seq.payoff(a/(a+b)))
        remaining=horizon-observed
        cont=(-case_seq.experiment_unit+(a/(a+b))*sequential_value(a+1,b,remaining-1)+(b/(a+b))*sequential_value(a,b+1,remaining-1)) if remaining else -np.inf
        action='continuar' if cont>stop else ('escalar' if stop>0 else 'detener')
        state_rows.append({'observed':observed,'successes':successes,'action':action})
state_table=pd.DataFrame(state_rows)
fig,ax=plt.subplots()
for name,color,marker in [('detener',GRAY,'x'),('continuar',BLUE,'o'),('escalar',GOLD,'s')]:
    sub=state_table[state_table.action==name]
    ax.scatter(sub.observed,sub.successes,s=12,color=color,marker=marker,label=name)
ax.set(xlabel='Observaciones acumuladas',ylabel='Éxitos acumulados',title='Política finita para un prior y costos explícitos')
ax.legend();plt.show()
import json
print('ACADEMIC_METRICS:'+json.dumps({'sequential_value':seq_net,'fixed_best_value':float(fixed_best['net_value']),'horizon':horizon,'states':len(state_rows)}))
''')
  pair(c,'Oráculo por enumeración de políticas, horizonte tres','Se enumeran 128 reglas binarias de continuar/parar sobre el árbol completo. Se evalúa cada política por probabilidades de camino, separada de la recursión memoizada.', '''
from itertools import product
small_horizon=3
policy_values=[]
for bits in product([0,1],repeat=2**small_horizon-1):
    # Node heap: root=0, success=2*j+1, failure=2*j+2.
    frontier=[(0,case_seq.alpha,case_seq.beta,0,1.,0.)]
    total=0.
    while frontier:
        node,a,b,depth,mass,spent=frontier.pop()
        stop=depth==small_horizon or bits[node]==0
        if stop:
            total+=mass*(max(0.,case_seq.payoff(a/(a+b)))-spent)
        else:
            p_success=a/(a+b)
            new_spent=spent+case_seq.experiment_unit
            frontier.append((2*node+1,a+1,b,depth+1,mass*p_success,new_spent))
            frontier.append((2*node+2,a,b+1,depth+1,mass*(1-p_success),new_spent))
    policy_values.append(total)
oracle=max(policy_values)
dp=sequential_value(case_seq.alpha,case_seq.beta,small_horizon)
assert abs(oracle-dp)<1e-7
print({'policies_enumerated':len(policy_values),'oracle_DP_gap':abs(oracle-dp)})
''')
  c.append(md('### Ideas y cierre pendiente\n\nContrastar el valor con un oráculo por enumeración para horizonte corto y con simulación fuera de la política ajustada; después introducir heterogeneidad, costo de demora y prior robusto. La desigualdad secuencial ≥ fijo solo se sostiene con el mismo menú, horizonte y costos.'))
 elif index==5:
  c.append(md(r'''### Regla de Chow y riesgo selectivo

[Chow, IEEE Transactions on Information Theory 1970](https://doi.org/10.1109/TIT.1970.1054406); [El-Yaniv y Wiener, JMLR 2010, definiciones 1–2](https://jmlr.org/papers/v11/el-yaniv10a.html).

Con costo de error $c_e$ y abstención perfecta $c_r$, se acepta si:

$$\max_k p_k\ge1-c_r/c_e.$$

La fórmula resulta de comparar riesgo Bayes de clasificar y abstenerse. Con fallback falible, el costo de derivar es $c_r+c_e\epsilon_f(x)$; cambia el umbral. Cobertura $\phi=E[g(X)]$ y riesgo selectivo $R=E[\ell(f(X),Y)g(X)]/\phi$ se reportan por separado. No se trasladan los teoremas sin ruido de JMLR a nuestras etiquetas Bernoulli ruidosas.'''))
  pair(c,'Oráculo Bayes: abstención perfecta y fallback falible','En este generador conocemos p verdadero. El oráculo sirve como referencia de decisión, no como un proveedor comercial.', '''
p_true=expit(z_test)
error_if_classify=np.minimum(p_true,1-p_true)
reject_cost=.1
rows_chow=[]
for fallback_error in [0.,.05,.15]:
    referral=reject_cost+fallback_error
    accept=error_if_classify<=referral
    oracle_cost=np.where(accept,error_if_classify,referral)
    threshold_cost=np.where(np.maximum(p_true,1-p_true)>=1-referral,error_if_classify,referral)
    assert np.allclose(oracle_cost,threshold_cost)
    rows_chow.append({'fallback_error':fallback_error,'threshold':1-referral,'coverage':float(accept.mean()),'expected_cost':float(oracle_cost.mean())})
display(pd.DataFrame(rows_chow).round(4))
''')
  pair(c,'Confianza reportada frente a incertidumbre real','Se comparan tres señales bajo el mismo costo de abstención perfecta; la confianza inflada puede aceptar demasiado.', '''
chow_comparison=[]
for name,probability in [('oraculo',p_true),('sin_calibrar',p_raw),('temperatura',p_calibrated)]:
    accept=np.maximum(probability,1-probability)>=.9
    decision=(probability>=.5)
    observed_cost=np.where(accept,decision!=y_test,.1)
    chow_comparison.append({'signal':name,'coverage':float(accept.mean()),'cost':float(observed_cost.mean()),
                            'selective_error':float(np.mean(decision[accept]!=y_test[accept])) if accept.any() else None})
chow_table=pd.DataFrame(chow_comparison);display(chow_table.round(4))
fig,ax=plt.subplots()
ax.bar(chow_table.signal,chow_table.cost,color=[GRAY,GOLD,BLUE])
ax.set(ylabel='Costo medio (error=1, abstención=0.1)',title='Una regla óptima requiere probabilidades pertinentes')
plt.show()
import json
print('ACADEMIC_METRICS:'+json.dumps({'Chow_comparison':chow_comparison}))
''')
  c.append(md('### Ideas y cierre pendiente\n\nEstimar error condicional del fallback con etiquetas independientes, comparar garantías exactas binomiales y cota Hoeffding, incorporar capacidad compartida y calibración por grupo. El costo de revisión perfecto es una referencia idealizada; la política real debe representar errores y demora.'))
 else:
  c.append(md(r'''### Procedencia literal y fidelidad semántica se evalúan por separado

[Maynez et al., ACL 2020](https://doi.org/10.18653/v1/2020.acl-main.173) estudia inconsistencias respecto de la fuente y evaluación de fidelidad en resúmenes. Aquí proponemos un test de contrato propio, sin reproducir su modelo de entailment ni usar XSum.

$$P_{soporte}=TP/(TP+FP),\quad R_{soporte}=TP/(TP+FN).$$

La etiqueta indica si la afirmación de ingreso está respaldada por este documento, no si es verdadera en el mundo. Las abstenciones se conservan; copiar una cifra real bajo el concepto equivocado puede pasar el hash.'''))
  pair(c,'Corpus adversarial con etiquetas explícitas','Cuatro clases sintéticas: campo respaldado, concepto incorrecto, valor inventado y cifra negada. Un verificador lexical es deliberadamente limitado.', '''
import re
paper_rng=np.random.default_rng(2307)
claim_rows=[]
for i in range(50):
    amount=int(paper_rng.integers(1,8))*1000000
    examples=[
        (f'Salario: {amount} COP.',str(amount),True,'respaldado'),
        (f'Transferencia: {amount} COP.',str(amount),False,'concepto'),
        (f'Salario: {amount} COP.',str(amount+12345),False,'inventado'),
        (f'No recibe salario: {amount} COP.',str(amount),False,'negado')]
    for source,literal,supported,kind in examples:
        ev=extract_literal(source,literal)
        span_ok=bool(ev and ev.verify(source))
        lexical=bool(span_ok and re.search(r'Salario: '+re.escape(literal)+r' COP',source))
        claim_rows.append({'kind':kind,'truth':supported,'span':span_ok,'lexical':lexical})
claims=pd.DataFrame(claim_rows)
''')
  pair(c,'Precisión, recall y fallo de paráfrasis','El verificador lexical puede ganar en la plantilla y perder al cambiar la redacción. Se incluye ese contraejemplo para evitar vender la regla como NLI.', '''
verification_rows=[]
for name in ['span','lexical']:
    predicted=claims[name].to_numpy();truth=claims.truth.to_numpy()
    tp=int(np.sum(predicted & truth));fp=int(np.sum(predicted & ~truth));fn=int(np.sum(~predicted & truth))
    verification_rows.append({'method':name,'TP':tp,'FP':fp,'FN':fn,'precision':tp/max(tp+fp,1),'recall':tp/max(tp+fn,1)})
verification=pd.DataFrame(verification_rows);display(verification)
paraphrase='Retribución laboral mensual: 3000000 COP.'
assert extract_literal(paraphrase,'3000000').verify(paraphrase)
assert not re.search(r'Salario: 3000000 COP',paraphrase)
fig,ax=plt.subplots()
verification.set_index('method')[['precision','recall']].plot.bar(ax=ax,color=[BLUE,GOLD],rot=0)
ax.set(ylim=(0,1.05),ylabel='Fracción sobre corpus etiquetado',title='La procedencia no verifica por sí sola el concepto')
plt.show()
import json
print('ACADEMIC_METRICS:'+json.dumps({'evidence_claim_metrics':verification_rows,'paraphrase_failure_retained':True}))
''')
  c.append(md('### Ideas y cierre pendiente\n\nCrear anotaciones humanas de concepto, negación, moneda, período y correcciones; medir acuerdo entre anotadores; comparar reglas con NLI y revisión humana bajo el mismo presupuesto. Añadir recuperación y OCR reales aprobados. La exactitud en plantillas no constituye generalización documental.'))
 return c
