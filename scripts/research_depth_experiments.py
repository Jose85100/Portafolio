"""Additional falsification experiments for the dated notebook extension."""
def experiments(index,md,code,pair):
 c=[]
 if index==0:
  pair(c,'Heterocedasticidad: límite del F exacto','El contraste robusto usa una covarianza sandwich HC1 con aproximación normal. No es una garantía finita ni la misma distribución F del experimento homocedástico.', '''
from scipy.stats import norm
hetero_rows=[]
for amplitude in [0.,1.,3.]:
    exact_reject=0
    robust_reject=0
    for seed in range(200):
        local=np.random.default_rng(90000+seed)
        zz=local.normal(size=200)
        vv=local.normal(size=200)
        noise=local.normal(size=200)
        uu=(1+amplitude*np.abs(zz))*noise
        xx=zz/np.sqrt(200)+vv
        yy=xx+uu
        exact_reject+=ar_pvalue(yy,xx,zz,1.)<=.05
        design=np.column_stack([np.ones(200),zz])
        inv=np.linalg.inv(design.T@design)
        coef=inv@design.T@(yy-xx)
        resid=yy-xx-design@coef
        meat=design.T@(resid[:,None]**2*design)
        cov=inv@meat@inv*200/198
        p_hc1=2*norm.sf(abs(coef[1]/np.sqrt(cov[1,1])))
        robust_reject+=p_hc1<=.05
    hetero_rows.append({'amplitud':amplitude,'F_homocedastico':exact_reject/200,'HC1_asintotico':robust_reject/200})
display(pd.DataFrame(hetero_rows))
''')
  pair(c,'Incertidumbre Monte Carlo','Los intervalos Wilson describen incertidumbre de estas 120 repeticiones por escenario. Un estimado cercano a 5% no prueba igualdad exacta.', '''
fig,ax=plt.subplots()
centers=checks_iv.AR.to_numpy()
lower=checks_iv.AR_lo.to_numpy()
upper=checks_iv.AR_hi.to_numpy()
ax.errorbar(np.arange(len(centers)),centers,yerr=[centers-lower,upper-centers],fmt='o',color=BLUE,capsize=4)
ax.axhline(.05,color=GRAY,ls='--')
ax.set_xticks(range(len(centers)),[f'c={x.c}, g={x.gamma}' for x in checks_iv.itertuples()])
ax.set(ylabel='Rechazo AR e intervalo Wilson 95%',title='Precisión finita del experimento de tamaño')
plt.show()
''')
  pair(c,'Primera etapa y dispersión del estimador','La razón IV puede ser extrema aun con datos finitos. Se reportan cuantiles, sin recortar los valores antes de calcularlos.', '''
estimates=[]
for strength in [0.,1.,8.]:
    sample_est=[]
    for seed in range(300):
        yy,xx,zz=sample(300000+seed,150,strength)
        zc=zz-zz.mean()
        denom=float(zc@(xx-xx.mean()))
        if denom!=0:
            sample_est.append(float(zc@(yy-yy.mean()))/denom)
    values=np.array(sample_est)
    estimates.append({'c':strength,'q01':np.quantile(values,.01),'mediana':np.median(values),'q99':np.quantile(values,.99),'max_abs':np.max(np.abs(values))})
display(pd.DataFrame(estimates).round(3))
''')
 elif index==1:
  pair(c,'Escala, traslación y parametrización','Trasladar coordenadas no cambia incrementos. Escalar todas las coordenadas por k multiplica nivel uno por k y nivel dos por k².', '''
base_path=circle(80)
base_a,base_b=signature(base_path)
shift_a,shift_b=signature(base_path+np.array([100.,-25.]))
scale_a,scale_b=signature(3*base_path)
assert np.allclose(base_a,shift_a,atol=1e-10)
assert np.allclose(base_b,shift_b,atol=1e-10)
assert np.allclose(scale_b,9*base_b,atol=1e-10)
print('Área original:',signed_area(base_path),'Área escala 3:',signed_area(3*base_path))
''')
  pair(c,'Clasificación de orientación con ruido','Monte Carlo sobre pares ida/reversa con ruido independiente. Los intervalos Wilson son marginales por nivel de ruido, no simultáneos.', '''
from scipy.stats import binomtest
noise_rows=[]
for sigma in [0,.1,.3,.8,1.5]:
    correct=0
    for repeat in range(200):
        orientation=1 if repeat%2==0 else -1
        noisy=circle(40,orientation=orientation)+rng_depth.normal(0,sigma,(41,2))
        noisy[-1]=noisy[0]
        correct+=np.sign(signed_area(noisy))==orientation
    interval=binomtest(correct,200).proportion_ci(method='wilson')
    noise_rows.append({'sigma':sigma,'accuracy':correct/200,'lo':interval.low,'hi':interval.high})
noise_table=pd.DataFrame(noise_rows)
display(noise_table.round(4))
fig,ax=plt.subplots()
ax.errorbar(noise_table.sigma,noise_table.accuracy,yerr=[noise_table.accuracy-noise_table.lo,noise_table.hi-noise_table.accuracy],fmt='o-',capsize=4,color=BLUE)
ax.axhline(.5,color=GRAY,ls='--')
ax.set(xlabel='Desviación del ruido por coordenada',ylabel='Exactitud e IC Wilson 95%',title='Orientación bajo contaminación de observación')
plt.show()
''')
  pair(c,'Estado recurrente y particiones irregulares','La composición se verifica con cortes no equiespaciados sobre una misma trayectoria; no recupera datos que nunca se observaron.', '''
x=path_d
cuts=[0,7,19,66,len(x)-1]
acc=signature(x[:1])
for left,right in zip(cuts[:-1],cuts[1:]):
    part=signature(x[left:right+1])
    acc=compose(acc,part)
assert all(np.allclose(a,b,atol=1e-9) for a,b in zip(acc,signature(x)))
print('Particiones:',cuts,'residual:',np.max(np.abs(acc[1]-signature(x)[1])))
''')
 elif index==2:
  pair(c,'Contaminación de calibración','Casos anómalos incluidos como legítimos elevan la referencia. Aquí se mide además detección de anomalías simuladas, sin llamarla sensibilidad a fraude real.', '''
contamination_rows=[]
legit_eval=rng_depth.normal(0,1,3000)
anomaly_eval=rng_depth.normal(3,1,3000)
for contamination in [0,.02,.1,.25]:
    n_bad=int(400*contamination)
    reference=np.r_[rng_depth.normal(size=400-n_bad),rng_depth.normal(4,1,size=n_bad)]
    calibrator=TailCalibrator(reference)
    fpr=np.mean([calibrator.alert(s,.05) for s in legit_eval])
    detection=np.mean([calibrator.alert(s,.05) for s in anomaly_eval])
    contamination_rows.append({'fraccion_contaminada':contamination,'FPR':fpr,'deteccion_sintetica':detection})
display(pd.DataFrame(contamination_rows))
''')
  pair(c,'Alertas múltiples y evento de al menos una','Control por caso no controla el evento de cualquier alerta del lote. El comparador IID ilustra la diferencia sin asumir que todos los lotes reales sean independientes.', '''
batch_sizes=np.array([1,5,20,100])
alpha=.05
any_alert=1-(1-alpha)**batch_sizes
display(pd.DataFrame({'tamano_lote':batch_sizes,'prob_al_menos_una_IID':any_alert}))
assert any_alert[-1]>.99
# Límite de Bonferroni: para controlar el lote se requeriría alpha/m por caso.
display(pd.DataFrame({'tamano_lote':batch_sizes,'alpha_bonferroni':alpha/batch_sizes,'n_min_resolucion':np.ceil(batch_sizes/alpha)-1}))
''')
  pair(c,'Calibración repetida: variación entre muestras','El error observado depende del conjunto de calibración. No se reutiliza el test para ajustar cada umbral.', '''
repeated=[]
for repeat in range(100):
    reference=rng_depth.normal(size=99)
    test=rng_depth.normal(size=500)
    cal=TailCalibrator(reference)
    repeated.append(np.mean([cal.alert(v,.05) for v in test]))
fig,ax=plt.subplots()
ax.hist(repeated,bins=15,color=BLUE,edgecolor='white')
ax.axvline(.05,color=GOLD,ls='--',label='Nominal')
ax.set(xlabel='FPR por calibración independiente',ylabel='Número de réplicas',title='Variabilidad del umbral con n=99')
ax.legend();plt.show()
print({'media_FPR':np.mean(repeated),'q10':np.quantile(repeated,.1),'q90':np.quantile(repeated,.9)})
''')
 elif index==3:
  pair(c,'Pesos extremos y abstención útil','Se mide el límite de resolución sin clipping silencioso; una razón de densidad extrema es parte del problema de solapamiento.', '''
concentration=[]
for sigma in [0,.5,1,2,3]:
    weights=np.exp(sigma*rng_depth.normal(size=200))
    test_w=np.exp(sigma*rng_depth.normal(size=1000))
    quantile=thresholds(np.abs(rng_depth.normal(size=200)),weights,test_w)
    concentration.append({'sigma_log_peso':sigma,'ESS':weights.sum()**2/np.sum(weights**2),'fraccion_infinita':np.mean(~np.isfinite(quantile))})
display(pd.DataFrame(concentration).round(4))
''')
  pair(c,'Cobertura por subgrupo','Una garantía marginal no promete 90% en cada grupo. Los denominadores se muestran y los intervalos Wilson describen este test condicionado a calibración.', '''
from scipy.stats import binomtest
subgroup=[]
for name,mask in [('grupo0',~g_test),('grupo1',g_test)]:
    covered=s_test[mask]<=q_correct[mask]
    interval=binomtest(int(covered.sum()),len(covered)).proportion_ci(method='wilson')
    subgroup.append({'grupo':name,'n':int(mask.sum()),'cobertura':covered.mean(),'lo':interval.low,'hi':interval.high,'fraccion_finita':np.isfinite(q_correct[mask]).mean()})
display(pd.DataFrame(subgroup).round(4))
''')
  pair(c,'Cobertura útil y cobertura total','Los infinitos cubren por construcción; reportar solo cobertura puede premiar abstenerse siempre. La cobertura entre finitos es descriptiva y no hereda la garantía marginal.', '''
finite_mask=np.isfinite(q_correct)
covered=s_test<=q_correct
useful_covered=np.mean(covered & finite_mask)
finite_coverage=float(covered[finite_mask].mean()) if finite_mask.any() else None
print({'cobertura_total':covered.mean(),'fraccion_finita':finite_mask.mean(),'cobertura_entre_finitos':finite_coverage,'cobertura_util_sobre_todos':useful_covered})
assert useful_covered<=covered.mean()
assert useful_covered<=finite_mask.mean()
''')
 elif index==4:
  pair(c,'EVSI con prior de igual media y distinta certeza','La media no resume el valor de aprender: se cambia concentración del prior manteniendo E(theta)=0.6.', '''
prior_rows=[]
for concentration in [2,5,10,30,100]:
    candidate=replace(case_d,alpha=.6*concentration,beta=.4*concentration)
    best=choose(candidate,sizes)
    prior_rows.append({'concentracion':concentration,'media':.6,'n_elegido':best['n'],'EVSI':best['evsi'],'incremento':best['increment']})
prior_table=pd.DataFrame(prior_rows)
display(prior_table.round(3))
fig,ax=plt.subplots()
ax.plot(prior_table.concentracion,prior_table.incremento,'o-',color=BLUE)
ax.set(xscale='log',xlabel='Concentración a+b del prior',ylabel='Incremento neto del mejor candidato',title='Incertidumbre previa y valor de experimentar')
plt.show()
''')
  pair(c,'Demora y valor neto','Se incorpora una penalidad hipotética por día. Esto es sensibilidad estática, no un modelo dinámico de competencia.', '''
delay_rows=[]
for cost_per_day in [0,25,100]:
    adjusted=design_d.copy()
    adjusted['dias']=np.where(adjusted.n>0,5+adjusted.n/10,0)
    adjusted['neto_con_demora']=adjusted.increment-cost_per_day*adjusted.dias
    best=adjusted.loc[adjusted.neto_con_demora.idxmax()]
    delay_rows.append({'costo_dia':cost_per_day,'n':best.n,'incremento_neto':best.neto_con_demora})
display(pd.DataFrame(delay_rows).round(2))
''')
  pair(c,'El piloto puede no pagar su costo','La alternativa n=0 permanece disponible. Los costos no se restan dos veces al comparar contra decidir hoy.', '''
expensive=replace(case_d,experiment_fixed=1000000.)
no_study=choose(expensive,sizes)
assert no_study['n']==0
assert no_study['increment']==0
print(no_study)
# Con información inútil, comprarla tampoco se justifica.
zero_population=replace(case_d,population=0)
assert choose(zero_population,sizes)['n']==0
''')
 elif index==5:
  pair(c,'Bootstrap pareado de diferencia de costo','Las políticas se evalúan sobre las mismas etiquetas. IC percentil del generador test IID, condicionado a los modelos y parámetros ya ajustados; no incluye incertidumbre de eficacia.', '''
a=fixed
cost_fixed=y_test*loss[a]*(1-efficacy[a])+cost[a]+(1-y_test)*friction[a]
a=actions
cost_economic=y_test*loss[a]*(1-efficacy[a])+cost[a]+(1-y_test)*friction[a]
difference=cost_economic-cost_fixed
bootstrap=[]
for repeat in range(400):
    sample_index=rng_depth.integers(0,n_test,n_test)
    bootstrap.append(difference[sample_index].mean())
print({'diferencia_economico_menos_fijo':difference.mean(),'IC95_percentil':np.quantile(bootstrap,[.025,.975]).tolist()})
''')
  pair(c,'Error selectivo por segmento','Un umbral global puede ocultar regiones difíciles. Los grupos están definidos por magnitud de z, sin observar etiquetas de test.', '''
from scipy.stats import binomtest
segments=[]
for label,mask in [('cerca_frontera',np.abs(z_test)<1),('intermedio',(np.abs(z_test)>=1)&(np.abs(z_test)<2)),('extremo',np.abs(z_test)>=2)]:
    selected=keep & mask
    errors=(~correct_test[selected])
    interval=binomtest(int(errors.sum()),len(errors)).proportion_ci(method='wilson') if len(errors) else None
    segments.append({'segmento':label,'n':int(mask.sum()),'aceptados':int(selected.sum()),'cobertura':selected.sum()/mask.sum(),'error':errors.mean() if len(errors) else None,'IC_lo':interval.low if interval else None,'IC_hi':interval.high if interval else None})
display(pd.DataFrame(segments).round(4))
''')
  pair(c,'Presupuesto de error y cobertura','La cota se recalcula solo con calibración. El presupuesto más estricto puede hacer imposible automatizar.', '''
selectivity=[]
for budget in [.03,.05,.1,.15,.2]:
    accepted,cut,bound=select_threshold(conf_select,correct_select,max_error=budget)
    selected=conf_test>=cut
    selectivity.append({'presupuesto_error':budget,'umbral':cut,'cota':bound,'cobertura_test':selected.mean(),'error_test':(~correct_test[selected]).mean() if selected.any() else None})
display(pd.DataFrame(selectivity).round(4))
''')
  pair(c,'Latencia y costo como escenarios, no benchmarks','Una cascada suma el costo inicial y el fallback en la fracción derivada. El p95 de la mezcla no se calcula promediando p95 individuales.', '''
latency_fast=rng_depth.lognormal(np.log(100),.2,n_test)
latency_fallback=rng_depth.lognormal(np.log(1000),.4,n_test)
latency_cascade=latency_fast+(~keep)*latency_fallback
comparison=[]
for name,latency,unit_cost in [('siempre fallback',latency_fallback,1.),('cascada',latency_cascade,.05+float((~keep).mean()))]:
    comparison.append({'politica':name,'p50_ms_simulado':np.quantile(latency,.5),'p95_ms_simulado':np.quantile(latency,.95),'costo_medio_simulado':unit_cost})
display(pd.DataFrame(comparison).round(3))
''')
 else:
  pair(c,'Duplicados de eventos y datos conflictivos','La clave de evento evita sumar dos veces, pero un duplicado con valores distintos requiere revisión y no se elimina silenciosamente.', '''
ledger=[{'event':'a','amount':3000000,'kind':'salary'},{'event':'a','amount':3000000,'kind':'salary'},
        {'event':'b','amount':2000000,'kind':'internal'}]
unique={}
for event in ledger:
    key=event['event']
    if key in unique and unique[key]!=event:raise ValueError('duplicado conflictivo')
    unique[key]=event
income=sum(e['amount'] for e in unique.values() if e['kind']=='salary')
assert income==3000000
assert sum(e['amount'] for e in ledger)==8000000
print({'suma_sin_conciliar':8000000,'ingreso_unico_externo':income})
''')
  pair(c,'Disponibilidad de documentos','Un hecho con fecha anterior pero recibido después no puede informar una decisión pasada.', '''
from datetime import date
application=date(2026,10,23)
events=[{'event_date':date(2026,10,1),'available':date(2026,10,22),'amount':3000000},
        {'event_date':date(2026,10,2),'available':date(2026,10,24),'amount':9000000}]
known=[e for e in events if e['event_date']<=application and e['available']<=application]
assert len(known)==1
print({'ingreso_disponible':sum(e['amount'] for e in known),'suma_retrospectiva_con_fuga':sum(e['amount'] for e in events)})
''')
  pair(c,'OCR y normalización: preservar ambas versiones','Cambiar O por 0 puede reparar un monto o alterar un identificador. Una normalización no es universal y no conserva el hash original.', '''
raw='Monto: 3OOO000 COP; referencia: ABCO1.'
normalized=raw.replace('O','0')
assert hashlib.sha256(raw.encode()).hexdigest()!=hashlib.sha256(normalized.encode()).hexdigest()
print({'raw':raw,'normalizado_global':normalized,'referencia_alterada':'ABC01' in normalized})
# La versión corregida necesita su propio mapa al original; no reutilizar offsets sin validación.
print('Revisión requerida para resolver el campo y conservar procedencia.')
''')
  pair(c,'Matriz de evaluación semántica','Procedencia y concepto son ejes separados. El ejemplo contiene casos válidos, incorrectos y abstenciones; no es exactitud de un proveedor.', '''
examples=pd.DataFrame([
 {'span_verificado':True,'concepto_correcto':True,'estado':'automatable'},
 {'span_verificado':True,'concepto_correcto':False,'estado':'error_semantico'},
 {'span_verificado':False,'concepto_correcto':True,'estado':'fuente_no_verificada'},
 {'span_verificado':False,'concepto_correcto':False,'estado':'review'}])
display(examples)
assert not (examples.span_verificado==examples.concepto_correcto).all()
''')
 c.append(md('### Interpretación de las pruebas adicionales\n\nCada experimento modifica un supuesto concreto. Las comparaciones conservan denominadores, unidades y desconocidos; los resultados negativos forman parte de la evidencia. Las simulaciones no convierten un diseño en un sistema operativo ni sustituyen validación independiente con datos aprobados.'))
 return c
