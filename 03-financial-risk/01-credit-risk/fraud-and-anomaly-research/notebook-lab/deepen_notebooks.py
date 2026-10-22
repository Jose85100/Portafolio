"""Add derivations, fitted alternatives and operational interpretation to 8 labs.

Idempotent on executed notebooks. build_notebooks invokes this after scaffolding.
"""
from pathlib import Path
import hashlib,textwrap
import nbformat as nbf
from model_reference import reference_cells
BASE=Path(__file__).resolve().parents[1]
LABS={}
def md(x):return nbf.v4.new_markdown_cell(textwrap.dedent(x).strip())
def code(x):return nbf.v4.new_code_cell(textwrap.dedent(x).strip())
def lab(key,card):
    cells=[md('## Desarrollo ampliado: modelo, estimación y uso\n\n'+card),code('advanced_metrics = {}\nadvanced_rng = np.random.default_rng(9221)')]
    LABS[key]=cells;return cells

def block(cells,title,math,source,reading):
    cells.extend([md('### '+title+'\n\n'+math),code(source),md('**Interpretación y uso.** '+reading)])

c=lab('01-bayes-evidence-and-calibration.ipynb',r'''
**Uso:** priorizar comprobaciones KYC cuando varias fuentes discrepan. **Unidad:** solicitud al cierre de una etapa. **Entrada:** indicadores de contradicción y disponibilidad; **salida:** probabilidad calibrada, nunca identidad certificada. Se separan tres objetos: calidad de evidencia, probabilidad de fraude y decisión económica.

El modelo logit supone log odds aditivas; una interacción requiere un término explícito. La estimación minimiza log loss regularizada. Las etiquetas deben representar adjudicación y estar disponibles en el corte de ajuste. Aquí son completas por construcción. Una auditoría institucional debe analizar también clientes sin etiqueta, cambios de proveedor y población rechazada.
''')
block(c,'4. Derivar log loss, gradiente y curvatura',r'''
Con $z_i=\beta_0+x_i^T\beta$ y $p_i=\sigma(z_i)$, la log-verosimilitud Bernoulli es $\sum_i[y_i z_i-\log(1+e^{z_i})]$. Minimizar su negativo medio más penalización da:

$$J(\theta)=\frac1n\sum_i[\log(1+e^{z_i})-y_i z_i]+\frac\lambda2\|\beta\|^2,$$
$$\nabla J=\frac1n X_*^T(p-y)+\lambda D\theta,\qquad H=\frac1n X_*^TWX_*+\lambda D.$$

$X_*$ añade intercepto; $D=\operatorname{diag}(0,1,\ldots,1)$ evita penalizarlo y $W_{ii}=p_i(1-p_i)$. Esta convención de lambda no se identifica sin más con C de una librería. `logaddexp` evita desbordamiento.
''',r'''
from scipy.special import expit
from scipy.optimize import minimize
X_star=np.column_stack([np.ones(len(train)),x[train]])
D=np.diag([0.,1.,1.,1.]);penalty=.02
def logistic_objective(theta):
    z=X_star@theta;p_hat=expit(z)
    value=np.mean(np.logaddexp(0,z)-y[train]*z)+penalty/2*(theta@D@theta)
    gradient=X_star.T@(p_hat-y[train])/len(train)+penalty*D@theta
    return value,gradient
fit=minimize(logistic_objective,np.zeros(4),jac=True,method='BFGS',options={'gtol':1e-8})
theta=fit.x
step=1e-5
finite_gradient=np.array([(logistic_objective(theta+np.eye(4)[j]*step)[0]-logistic_objective(theta-np.eye(4)[j]*step)[0])/(2*step) for j in range(4)])
analytic_gradient=logistic_objective(theta)[1]
fit_p=expit(X_star@theta)
hessian=(X_star.T*(fit_p*(1-fit_p)))@X_star/len(train)+penalty*D
display(pd.DataFrame({'parámetro':['intercepto','E1','E2','ruido'],'coeficiente':theta,'gradiente':analytic_gradient,'diferencia_finita':finite_gradient}))
assert np.linalg.norm(analytic_gradient,ord=np.inf)<1e-6
assert np.max(np.abs(finite_gradient-analytic_gradient))<1e-6
assert np.linalg.eigvalsh(hessian).min()>-1e-10
''','La derivación concilia con diferencias finitas y una curvatura no negativa. Los dos indicadores duplicados no son efectos causales independientes. La penalización estabiliza coeficientes, pero no valida las fuentes ni corrige sesgo de adjudicación.')
block(c,'5. Dependencia parcial entre evidencias',r'''
Supongamos que una segunda señal copia la primera con probabilidad $r$ y, de lo contrario, se genera independientemente condicionada a Y. Entonces
$$P(E_1=E_2=1\mid Y=1)=rs+(1-r)s^2,$$
$$P(E_1=E_2=1\mid Y=0)=rf+(1-r)f^2.$$
$r$ es probabilidad de copia, no coeficiente de correlación. Bayes debe usar estas probabilidades conjuntas, no un producto de marginales impuesto.
''',r'''
copy_grid=np.linspace(0,1,41)
true_joint=prevalence*(copy_grid*sensitivity+(1-copy_grid)*sensitivity**2)
false_joint=(1-prevalence)*(copy_grid*false_positive+(1-copy_grid)*false_positive**2)
correct_joint=true_joint/(true_joint+false_joint)
fig,ax=plt.subplots();ax.plot(copy_grid,correct_joint,color=TEAL,label='Posterior con dependencia declarada')
ax.axhline(naive_probability,color=GOLD,linestyle='--',label='Independencia impuesta')
ax.set(xlabel='Probabilidad de copiar la evidencia',ylabel='Posterior con ambas señales positivas',title='Aporte incremental de una segunda fuente');ax.legend(fontsize=9);plt.show()
assert np.isclose(correct_joint[0],naive_probability)
assert np.isclose(correct_joint[-1],posterior)
''','Una fuente puede aportar menos a medida que aumenta su dependencia. Antes de añadir un proveedor, preguntar cuál es su origen informativo y si hay una validación externa o solo una réplica.')
block(c,'6. Confiabilidad y tamaño de muestra',r'''
Para un grupo B de predicciones, comparar $\bar p_B$ con $\bar y_B$. Una discrepancia es un diagnóstico de calibración, no una prueba concluyente con pocos casos. Se usan cinco bins por cuantiles de score y se publica n por bin.
''',r'''
calibration_rows=[]
for name,p_values in predictions.items():
    bins=pd.qcut(pd.Series(p_values),5,labels=False,duplicates='drop')
    for b in sorted(bins.dropna().unique()):
        mask=(bins.to_numpy()==b)
        calibration_rows.append({'modelo':name,'bin':int(b),'n':int(mask.sum()),'predicho':float(p_values[mask].mean()),'observado':float(y[test][mask].mean())})
reliability=pd.DataFrame(calibration_rows)
display(reliability.round(4))
fig,ax=plt.subplots()
for name,color in zip(predictions,[BLUE,GOLD,TEAL]):
    subset=reliability[reliability['modelo']==name]
    ax.plot(subset['predicho'],subset['observado'],marker='o',label=name,color=color)
ax.plot([0,1],[0,1],linestyle='--',color='#333333');ax.set(xlim=(0,1),ylim=(0,1),xlabel='Probabilidad media predicha',ylabel='Frecuencia de fraude sintético',title='Calibración en prueba: cinco bins por modelo');ax.legend(fontsize=8);plt.show()
''','Dos modelos pueden ordenar igual y tener costos distintos por mala escala probabilística. Las frecuencias de este test tienen solo 26 positivos; no se presentan como curvas poblacionales exactas.')
block(c,'7. Cambio de tasa base y actualización de odds',r'''
Si solo cambia $\pi$ y se conservan las distribuciones de evidencia condicionadas a Y, las odds se ajustan por
$$O_{new}(Y\mid E)=O_{old}(Y\mid E)\frac{\pi_{new}/(1-\pi_{new})}{\pi_{old}/(1-\pi_{old})}.$$
Es una hipótesis de cambio de prior, no una solución universal a drift. Si el atacante cambia el mecanismo de evidencia, no basta ajustar la tasa base.
''',r'''
new_prior=.10
new_y=advanced_rng.binomial(1,new_prior,5000)
new_e=advanced_rng.binomial(1,np.where(new_y==1,sensitivity,false_positive))
def exact_posterior(prior,e):
    positive=prior*sensitivity/(prior*sensitivity+(1-prior)*false_positive)
    negative=prior*(1-sensitivity)/(prior*(1-sensitivity)+(1-prior)*(1-false_positive))
    return np.where(e==1,positive,negative)
old_prob=exact_posterior(prevalence,new_e)
old_odds=old_prob/(1-old_prob)
ratio=(new_prior/(1-new_prior))/(prevalence/(1-prevalence))
adjusted=old_odds*ratio/(1+old_odds*ratio)
reference=exact_posterior(new_prior,new_e)
display(pd.DataFrame({'escala':['Prior antiguo','Ajuste de odds'],'Brier':[brier_score_loss(new_y,old_prob),brier_score_loss(new_y,adjusted)],'media_p':[old_prob.mean(),adjusted.mean()]}))
assert np.allclose(adjusted,reference)
advanced_metrics.update({'Error máximo de gradiente':float(np.max(np.abs(finite_gradient-analytic_gradient))),'Posterior con copia total':round(float(correct_joint[-1]),4)})
''','La igualdad con Bayes es una comprobación analítica bajo un supuesto controlado. La prevalencia futura no estaría conocida en una aplicación: debe estimarse con etiquetas maduras y la incertidumbre debe conservarse.')

c=lab('02-economic-thresholds-and-capacity.ipynb',r'''
**Uso:** decidir qué solicitud requiere información adicional cuando no alcanza la capacidad para revisar todas. **Entrada:** probabilidad con población/versión, pérdida neta en COP, costos, eficacia y minutos. **Salida:** acción sugerida y costo bajo supuestos. No se deriva una política de aprobación de crédito completa.

El costo esperado supone casos independientes y una acción por caso. El monto es pérdida condicionada a fraude y no necesariamente saldo total. La fricción corresponde a clientes legítimos. La eficacia de la acción y la calidad de una prueba informativa son conceptos distintos; los ejercicios siguientes los separan.
''')
block(c,'4. Umbral con ejemplo numérico completo',r'''
De $B=pLq-c-(1-p)f$ se obtiene $B=p(Lq+f)-(c+f)$. La frontera es
$$p^*=\frac{c+f}{Lq+f},\quad\frac{\partial p^*}{\partial L}=-\frac{q(c+f)}{(Lq+f)^2}.$$

Si $p^*>1$ no hay probabilidad admisible que justifique la acción bajo ese costo. Un umbral bajo no elimina la restricción de capacidad.
''',r'''
review=actions[2]
example_loss=2_000_000.
threshold=(review.cost_cop+review.legitimate_friction_cop)/(example_loss*review.prevent_fraction+review.legitimate_friction_cop)
example_rows=[]
for probability in [threshold/2,threshold,threshold*2,.2]:
    case=Case('example',float(probability),example_loss)
    allow_cost=expected_cost(case,actions[0]);review_cost=expected_cost(case,review)
    example_rows.append({'p':probability,'continuar_COP':allow_cost,'revisar_COP':review_cost,'beneficio_COP':allow_cost-review_cost})
display(pd.DataFrame(example_rows))
assert abs(example_rows[1]['beneficio_COP'])<1e-6
''','El mismo cálculo puede documentarse para un comité de riesgo con moneda, horizonte y fuente de cada parámetro. No interpretar el umbral de este ejemplo como apetito institucional de fraude.')
block(c,'5. Valor de información: verificar antes de actuar',r'''
Para una prueba binaria Z con sensibilidad s y falso positivo f, $P(Z=1)=ps+(1-p)f$. Cada resultado actualiza p por Bayes. El valor esperado de información muestral neto es
$$EVSI=\min_a C(a,p)-\sum_z P(z)\min_a C(a,p_z)-c_Z.$$

La prueba de este ejercicio solo informa: no previene directamente. Sus costos no deben sumarse otra vez como eficacia q del motor.
''',r'''
terminal_actions=[actions[0],actions[2]]
verification_sensitivity,verification_fp,test_cost=.85,.07,3000.
def info_value(p,L,test_fee=test_cost):
    positive=p*verification_sensitivity+(1-p)*verification_fp
    negative=1-positive
    p_pos=p*verification_sensitivity/positive
    p_neg=p*(1-verification_sensitivity)/negative
    baseline=min(expected_cost(Case('info',p,L),a) for a in terminal_actions)
    posterior_cost=positive*min(expected_cost(Case('pos',p_pos,L),a) for a in terminal_actions)+negative*min(expected_cost(Case('neg',p_neg,L),a) for a in terminal_actions)
    return baseline-posterior_cost-test_fee,positive,p_pos,p_neg
information=[]
for probability in np.linspace(.001,.3,80):
    evsi,z_prob,p_pos,p_neg=info_value(float(probability),example_loss)
    information.append({'p':probability,'EVSI_COP':evsi})
information=pd.DataFrame(information)
fig,ax=plt.subplots();ax.plot(information['p'],information['EVSI_COP'],color=TEAL)
ax.axhline(0,color='#333333',linestyle='--');ax.set(xlabel='Probabilidad antes de verificar',ylabel='Valor neto de información (COP)',title='Una prueba es útil cerca de decisiones que puede cambiar');plt.show()
value,zp,pp,pn=info_value(.05,example_loss)
assert np.isclose(zp*pp+(1-zp)*pn,.05)
''','La probabilidad posterior promedio conserva el prior. El beneficio surge al cambiar una decisión, no al aumentar siempre el score. Si el resultado no modifica ninguna acción, la información no justifica su costo en este modelo.')
block(c,'6. Límite de información perfecta y costo máximo',r'''
La información perfecta revela Y antes de elegir acción. Su costo esperado es
$$C_{PI}=p\min_a C(a,1)+(1-p)\min_a C(a,0).$$

La información muestral sin costo no puede valer más que la perfecta en el modelo especificado. La comparación se hace con el mismo menú de acciones y sin costo de esperar.
''',r'''
info_checks=[]
for probability in [.005,.02,.05,.1,.2]:
    base=min(expected_cost(Case('x',probability,example_loss),a) for a in terminal_actions)
    perfect=probability*min(expected_cost(Case('fraud',1.,example_loss),a) for a in terminal_actions)+(1-probability)*min(expected_cost(Case('legit',0.,example_loss),a) for a in terminal_actions)
    sample_free=info_value(probability,example_loss,test_fee=0)[0]
    info_checks.append({'p':probability,'EVPI_COP':base-perfect,'EVSI_sin_costo_COP':sample_free})
info_checks=pd.DataFrame(info_checks);display(info_checks)
assert (info_checks['EVSI_sin_costo_COP']>=-1e-7).all()
assert (info_checks['EVSI_sin_costo_COP']<=info_checks['EVPI_COP']+1e-7).all()
''','El límite permite detectar doble conteo o una actualización de Bayes incoherente. La información perfecta no significa pérdida cero: revisar un fraude tiene costo y eficacia menor que uno.')
block(c,'7. Capacidad, costo sombra y límite dual',r'''
Al relajar la capacidad con $\lambda\ge0$:
$$g(\lambda)=\sum_i\min_a[C_i(a)+\lambda t_a]-\lambda T.$$

Cada g es un límite inferior del costo mínimo. El MILP es discreto; maximizar este dual no necesariamente recupera su valor exacto. Lambda se interpreta como COP por minuto en el problema relajado, no como salario óptimo de un analista.
''',r'''
T=60.
base_cost=np.array([[expected_cost(case,a) for a in actions] for case in cases])
effort=np.array([a.effort_minutes for a in actions])
lambdas=np.linspace(0,100_000,250)
dual=np.array([np.min(base_cost+lam*effort,axis=1).sum()-lam*T for lam in lambdas])
primal=plans[3]['objective_cop']
fig,ax=plt.subplots();ax.plot(lambdas,dual/1e6,color=BLUE,label='Límite dual')
ax.axhline(primal/1e6,color=TEAL,linestyle='--',label='Óptimo MILP')
ax.set(xlabel='Lambda (COP por minuto)',ylabel='Costo o límite (millones COP)',title='Capacidad como restricción económica');ax.legend();plt.show()
assert np.max(dual)<=primal+1e-5
advanced_metrics.update({'Umbral de revisión para 2 millones':round(float(threshold),5),'EVSI neto con p=0,05 (COP)':round(float(value),2),'Brecha sobre límite dual de grilla (COP)':round(float(primal-dual.max()),2)})
''','La grilla aproxima el mejor dual y no certifica su máximo continuo. El solver conserva su propia verificación de integralidad y restricciones. Para colas y casos relacionados habría que cambiar la formulación, no reutilizar el mismo límite sin más.')

c=lab('01-point-in-time-graph-features.ipynb',r'''
**Uso:** buscar coordinación en solicitudes que comparten dispositivos o destinos. **Entrada:** enlaces fechados y una señal individual de contradicción. **Salida:** ranking probabilístico experimental más razones de variables. Un vínculo compartido no adjudica fraude; la infraestructura legítima se incluye como control negativo.

A continuación se ajustan dos modelos a un nuevo generador: individual y con variables de red. El target es latente en el simulador y origina señales imperfectas; no se define por cruzar un umbral del conteo. El split es temporal con maduración de etiquetas y campañas nuevas por bloque.
''')
block(c,'4. Generador con infraestructura legítima y campañas nuevas',r'''
Sea $Y_i\sim Bernoulli(\pi)$; una parte de fraudes comparte dispositivo por campaña, mientras algunos legítimos usan un hub. La evidencia individual A tiene distribuciones solapadas. Se generan enlaces observables antes de adjudicar Y; las etiquetas llegan 12 días después.
''',r'''
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
network_n=1000
network_time=np.arange(network_n)/5
network_y=advanced_rng.binomial(1,.09,network_n)
individual_signal=np.clip(advanced_rng.normal(.22+.25*network_y,.18,network_n),0,1)
network_links=[];is_hub=[]
for i in range(network_n):
    hub=bool(network_y[i]==0 and advanced_rng.random()<.18)
    campaign=bool(network_y[i]==1 and advanced_rng.random()<.75)
    entity=(f'ring-{int(network_time[i]//20)}' if campaign else ('legitimate-hub' if hub else f'private-{i}'))
    delay=2. if i%11==0 else 0.
    network_links.append({'application_id':str(i),'entity':entity,'event_at':float(network_time[i]),'available_at':float(network_time[i]+delay)})
    is_hub.append(hub)
entity_available=np.array([e['available_at']<=e['event_at'] for e in network_links])
network_count=np.array([shared_entity_count(network_links,e['entity'],e['event_at'],e['application_id'],window=20) if known else 0 for e,known in zip(network_links,entity_available)])
network_x=np.column_stack([individual_signal,np.log1p(network_count),individual_signal*np.log1p(network_count),(~entity_available).astype(float)])
network_train=(network_time<100)&(network_time+12<=120)
network_test=network_time>=140
assert network_time[network_train].max()+12<=120
assert network_time[network_test].min()>=140
print('Train:',network_train.sum(),'test:',network_test.sum(),'positivos de prueba:',network_y[network_test].sum())
''','Las asignaciones de dispositivo dependen del target latente por diseño causal del generador; el constructor de variables solo ve los enlaces, no el target. Esta simulación no es evidencia de cómo opera una campaña real.')
block(c,'5. Modelo individual frente a modelo de red',r'''
El baseline usa $\operatorname{logit}(p)=\beta_0+\beta_1 A$. El challenger añade $R=\log(1+N)$ e interacción:
$$\operatorname{logit}(p)=\beta_0+\beta_1 A+\beta_2 R+\beta_3 AR+\beta_4 M.$$

La interacción permite que una discrepancia individual y reutilización tengan aporte conjunto. M indica que la entidad actual aún no estaba disponible; su conteo se codifica como cero junto a ese indicador, diferenciándolo de cero observado. Escalado y logit se ajustan solo en entrenamiento; no se seleccionan hiperparámetros mirando la prueba.
''',r'''
individual_model=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=500))
network_model=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=500))
individual_model.fit(network_x[network_train,:1],network_y[network_train])
network_model.fit(network_x[network_train],network_y[network_train])
individual_p=individual_model.predict_proba(network_x[network_test,:1])[:,1]
network_p=network_model.predict_proba(network_x[network_test])[:,1]
network_scores=pd.DataFrame([{'modelo':name,'AP':average_precision_score(network_y[network_test],p),'Brier':brier_score_loss(network_y[network_test],p)} for name,p in [('individual',individual_p),('individual + red',network_p)]])
display(network_scores)
fig,ax=plt.subplots();ax.bar(network_scores['modelo'],network_scores['AP'],color=[BLUE,TEAL])
ax.axhline(network_y[network_test].mean(),color='#333333',linestyle='--',label='Prevalencia test')
ax.set(ylim=(0,1),ylabel='Average precision',title='Aporte de la red: prueba temporal sintética');ax.legend();plt.show()
''','AP y Brier responden a preguntas distintas. El resultado corresponde al mecanismo generado, con dispositivos nuevos por campaña en prueba; no certifica generalización a redes de personas reales ni reemplaza calibración posterior.')
block(c,'6. Falsos positivos en un hub legítimo',r'''
A igual capacidad K se revisan los primeros K scores. La precisión es $TP/K$; una tasa de derivación en legítimos requiere denominador explícito. No se usa 0,5 como umbral de aprobación.
''',r'''
network_K=25
network_eval=[]
legitimate=network_y[network_test]==0
hub_mask=np.array(is_hub)[network_test]
for name,p in [('individual',individual_p),('individual + red',network_p)]:
    selected=np.zeros(len(p),bool);selected[np.argsort(-p,kind='stable')[:network_K]]=True
    network_eval.append({'modelo':name,'K':network_K,'precision_K':network_y[network_test][selected].mean(),
                         'legitimos_derivados':int((selected&legitimate).sum()),
                         'hubs_legitimos_revisados':int((selected&hub_mask).sum()),'hubs_disponibles':int(hub_mask.sum())})
display(pd.DataFrame(network_eval))
fig,ax=plt.subplots()
for flag,label,color in [(False,'Otros casos',BLUE),(True,'Hub legítimo',GOLD)]:
    mask=hub_mask==flag
    ax.scatter(network_count[network_test][mask],network_p[mask],s=22,alpha=.7,label=label,color=color)
ax.set(xlabel='Solicitudes previas en 20 días',ylabel='Probabilidad del modelo de red',title='La reutilización necesita contexto individual');ax.legend();plt.show()
''','La tabla muestra si un hub consume la cola aunque sea legítimo. Si la variable de red solo penaliza compartir infraestructura, la mejora agregada no basta para promoverla. Revisar errores y razones por segmento.')
block(c,'7. Prueba de fuga y uso operativo',r'''
La condición temporal se verifica sobre el constructor, no solo sobre el nombre del modelo. Se añade un enlace disponible en el futuro a una entidad del pasado y se exige invariancia. Las etiquetas posteriores nunca se incorporan a los features de este ejemplo.
''',r'''
probe=network_links[150]
probe_before=shared_entity_count(network_links,probe['entity'],probe['event_at'],probe['application_id'],window=20)
added={'application_id':'not-yet','entity':probe['entity'],'event_at':500.,'available_at':500.}
probe_after=shared_entity_count(network_links+[added],probe['entity'],probe['event_at'],probe['application_id'],window=20)
assert probe_before==probe_after
assert np.isfinite(network_p).all()
train_campaigns={e['entity'] for e,keep in zip(network_links,network_train) if keep and e['entity'].startswith('ring-')}
test_campaigns={e['entity'] for e,keep in zip(network_links,network_test) if keep and e['entity'].startswith('ring-')}
assert train_campaigns.isdisjoint(test_campaigns)
assert (network_count[~entity_available]==0).all()
advanced_metrics.update({'AP individual temporal':round(float(network_scores.iloc[0]['AP']),4),'AP con red temporal':round(float(network_scores.iloc[1]['AP']),4),'Campañas de prueba no vistas por bloque':bool(train_campaigns.isdisjoint(test_campaigns))})
''','Para usar este modelo se necesita snapshot versionado, evidencia de titularidad, resolución de entidades y adjudicación de casos. El ejemplo aporta un baseline ajustado y pruebas temporales; la operación institucional completa permanece pendiente.')

c=lab('02-network-overlap-and-loss-coverage.ipynb',r'''
**Uso:** asignar acciones cuando varias solicitudes comparten exposición o una investigación puede contener más de un caso. **Unidad económica:** flujo prevenible único. **Entrada:** matriz de cobertura y su incertidumbre. **Salida:** conjunto de acciones con beneficio conciliado por exposición.

Este modelo de red tiene otra función que el clasificador de solicitudes: optimiza una intervención compartida. No se deben sumar sus beneficios a los del motor individual sin deduplicar pérdidas. El MILP de cobertura tiene un alcance exacto solo bajo eficacia perfecta y vínculos declarados.
''')
block(c,'4. Enumeración como referencia y valor marginal',r'''
Para añadir acción i a S:
$$\Delta_i(S)=B(S\cup\{i\})-B(S)=\sum_{j\in S_i\setminus\cup_{k\in S}S_k}\ell_j-c_i.$$

Con cobertura no negativa hay rendimientos decrecientes de la cobertura; el costo puede hacer negativa una adición. La siguiente tabla identifica redundancia en vez de sumar listas.
''',r'''
marginal_rows=[]
for chosen_set in [(),(0,),(2,)]:
    for candidate in range(3):
        if candidate in chosen_set:continue
        new_set=tuple(sorted(set(chosen_set)|{candidate}))
        marginal_rows.append({'elegidas':str(chosen_set),'candidata':candidate,'marginal_COP':benefit(new_set)-benefit(chosen_set)})
display(pd.DataFrame(marginal_rows))
assert benefit((0,1))-benefit((0,))==-cost[1]
''','La segunda investigación redundante solo añade costo en este supuesto. Eso no demuestra que dos investigaciones reales sean redundantes: habría que medir si aportan evidencia o previenen pérdidas adicionales.')
block(c,'5. Cobertura incierta: expectativa y peor escenario',r'''
Cada escenario s define una matriz $A^{(s)}$. Para mantener transparencia en un caso pequeño se enumeran acciones:
$$B_s(S)=\sum_j\ell_j\mathbf1\{\sum_{i\in S}A^{(s)}_{ij}>0\}-\sum_{i\in S}c_i.$$

Se comparan $\max_S\sum_s w_sB_s(S)$ y $\max_S\min_sB_s(S)$ con el mismo K. Los escenarios son supuestos, no probabilidades estimadas de una campaña.
''',r'''
scenario_coverages=[coverage.copy(),np.array([[1,0,0],[0,1,0],[0,0,1]]),np.array([[0,0,0],[1,1,0],[0,0,1]])]
scenario_weights=np.array([.6,.25,.15])
sets=[s for size in range(3) for s in itertools.combinations(range(3),size)]
def scenario_benefit(selected,matrix):
    covered=matrix[list(selected)].any(axis=0) if selected else np.zeros(3,bool)
    return float(exposure[covered].sum()-cost[list(selected)].sum())
benefit_matrix=np.array([[scenario_benefit(s,matrix) for matrix in scenario_coverages] for s in sets])
expected_choice=int(np.argmax(benefit_matrix@scenario_weights))
robust_choice=int(np.argmax(benefit_matrix.min(axis=1)))
display(pd.DataFrame({'acciones':[str(s) for s in sets],'esperado_COP':benefit_matrix@scenario_weights,'peor_COP':benefit_matrix.min(axis=1)}))
fig,ax=plt.subplots();positions=np.arange(3)
for offset,index,label,color in [(-.18,expected_choice,'Esperado',BLUE),(.18,robust_choice,'Minimax',TEAL)]:
    ax.bar(positions+offset,benefit_matrix[index]/1000,width=.36,label=label,color=color)
ax.set_xticks(positions,['Base','Enlace parcial','Origen perdido']);ax.set(ylabel='Beneficio supuesto (miles COP)',title='La incertidumbre de enlaces cambia el problema');ax.legend();plt.show()
''','Ambos criterios pueden coincidir en un problema pequeño; se conserva ese resultado si ocurre. Minimax protege solo contra estos escenarios y puede sacrificar beneficio esperado. No se interpreta como CVaR de pérdidas realizadas.')
block(c,'6. Eficacia parcial y dependencia de acciones',r'''
Con eficacias $q_{ij}$ y éxitos independientes condicionados, $q_j(S)=1-\prod_{i\in S}(1-q_{ij})$. En dependencia total, el aporte conjunto puede ser solo $\max_i q_{ij}$. Una fórmula aditiva puede superar uno y es inválida.
''',r'''
def partial_benefit(selected,mode):
    if not selected:return 0.
    q_matrix=.6*coverage[list(selected)]
    joint=1-np.prod(1-q_matrix,axis=0) if mode=='independent' else q_matrix.max(axis=0)
    return float(exposure@joint-cost[list(selected)].sum())
partial=[]
for selected in [(0,),(0,1),(0,2)]:
    partial.append({'acciones':str(selected),'éxitos_independientes_COP':partial_benefit(selected,'independent'),'dependencia_total_COP':partial_benefit(selected,'dependent')})
display(pd.DataFrame(partial))
assert partial_benefit((0,1),'dependent')<partial_benefit((0,),'dependent')
''','La diferencia entre columnas es riesgo de supuesto. La estimación de eficacia conjunta necesita adjudicación temporal y una estrategia causal; no se deriva del simple hecho de que dos solicitudes compartan una cuenta.')
block(c,'7. Costos, presupuesto y valor de información del vínculo',r'''
Una investigación adicional puede aclarar un enlace antes de elegir las acciones. Un límite de costo de ese conocimiento es
$$EVPI=\sum_s w_s\max_S B_s(S)-\max_S\sum_s w_sB_s(S).$$

Cada máximo usa el mismo presupuesto; si se revela el escenario se permite adaptar la decisión. El valor no es el costo de comprar datos, sino un máximo teórico bajo la lista de escenarios.
''',r'''
perfect_information=float(scenario_weights@benefit_matrix.max(axis=0))
fixed_best=float((benefit_matrix@scenario_weights).max())
link_information_value=perfect_information-fixed_best
print('Valor perfecto de conocer el escenario (COP):',link_information_value)
coverage_counts=coverage.sum(axis=0)
fig,ax=plt.subplots();ax.bar(np.arange(3),coverage_counts,color=PURPLE)
ax.set_xticks(np.arange(3),['Exposición 1','Exposición 2','Exposición 3'])
ax.set(ylabel='Acciones que incluyen la exposición',title='Auditar la multiplicidad antes de sumar pérdida');plt.show()
assert link_information_value>=-1e-7
advanced_metrics.update({'Valor perfecto de información de vínculos (COP)':round(link_information_value,2),'Alternativas enumeradas con K<=2':len(sets),'Mayor multiplicidad de exposición':int(coverage_counts.max())})
''','En una aplicación se pediría origen del vínculo, fecha, confianza y exposición única. El costo de aclarar no debe exceder el beneficio posible; aun con este límite favorable hacen falta costos de demora y eficacia real.')

c=lab('01-income-quantiles-and-coverage.ipynb',r'''
**Uso:** estimar un rango de ingreso corroborado y decidir cuándo pedir aclaraciones. **Entrada:** actividad, estacionalidad, cobertura de evidencia y tipo de ingreso; **salida:** distribución o banda monetaria, no probabilidad de fraude. El target debe ser ingreso verificado en la misma base temporal y monetaria que la declaración.

Los cuantiles describen dispersión individual, no incertidumbre de una media. La calibración conformal requiere condiciones de intercambio; una evaluación temporal debe investigar dependencia y cambio de régimen. Se amplía el desarrollo con pérdida pinball, un modelo de dos partes, validación por grupo y severidad de discrepancia.
''')
block(c,'4. Por qué la pérdida pinball estima un cuantil',r'''
Para una predicción constante a, $E[\rho_\tau(Y-a)]$ tiene derivada $F_Y(a)-\tau$ donde existe. El mínimo satisface $F_Y(a)=\tau$. Por eso variar tau cambia el punto de la distribución que se estima.

$$\rho_\tau(u)=\begin{cases}\tau u,&u\ge0,\\(\tau-1)u,&u<0.\end{cases}$$

El error cuadrático estima una media y no sustituye a esta pérdida. El siguiente contraste verifica numéricamente la posición del mínimo en una población asimétrica.
''',r'''
pinball_sample=advanced_rng.lognormal(0,.7,1500)
constant_grid=np.linspace(.1,4,500)
pinball_records=[]
for tau in [.1,.5,.9]:
    u=pinball_sample[:,None]-constant_grid[None,:]
    losses=np.mean(np.maximum(tau*u,(tau-1)*u),axis=0)
    minimizer=constant_grid[np.argmin(losses)]
    empirical=float(np.quantile(pinball_sample,tau))
    pinball_records.append({'tau':tau,'minimo_grilla':minimizer,'cuantil_empirico':empirical,'error':abs(minimizer-empirical)})
display(pd.DataFrame(pinball_records))
assert max(z['error'] for z in pinball_records)<.03
''','El mínimo se aproxima con una grilla; el error permitido refleja su resolución. En un modelo condicional, la misma lógica se aplica para cada X bajo capacidad de estimación suficiente y no demuestra calibración por grupo.')
block(c,'5. Ingresos cero: probabilidad y monto positivo',r'''
Con $\pi_0(X)=P(I=0\mid X)$ y $F_+(u\mid X)$ para I positivo:
$$F_I(u\mid X)=\pi_0(X)+(1-\pi_0(X))F_+(u\mid X),\quad u>0.$$

Para obtener el cuantil tau: es cero si $\tau\le\pi_0$; si no, se busca el cuantil positivo $(\tau-\pi_0)/(1-\pi_0)$. Un cero observado y ausencia de evidencia son estados distintos.
''',r'''
from sklearn.linear_model import LogisticRegression,LinearRegression
from scipy.stats import norm
hurdle_n=2500
hurdle_x=advanced_rng.uniform(0,1,(hurdle_n,2))
true_zero_p=1/(1+np.exp(-(-2+2*hurdle_x[:,1])))
hurdle_zero=advanced_rng.binomial(1,true_zero_p)
positive_log=np.log(2_000_000)+.5*hurdle_x[:,0]+advanced_rng.normal(0,.25,hurdle_n)
hurdle_income=np.where(hurdle_zero==1,0,np.exp(positive_log))
hurdle_train=np.arange(1500);hurdle_test=np.arange(1500,2500)
zero_model=LogisticRegression(C=10,max_iter=500).fit(hurdle_x[hurdle_train],hurdle_zero[hurdle_train])
positive_train=hurdle_train[hurdle_zero[hurdle_train]==0]
amount_model=LinearRegression().fit(hurdle_x[positive_train],positive_log[positive_train])
residual_sigma=float(np.std(positive_log[positive_train]-amount_model.predict(hurdle_x[positive_train]),ddof=3))
p0=zero_model.predict_proba(hurdle_x[hurdle_test])[:,1]
mu=amount_model.predict(hurdle_x[hurdle_test])
def hurdle_quantile(tau):
    adjusted=np.clip((tau-p0)/(1-p0),1e-9,1-1e-9)
    return np.where(tau<=p0,0,np.exp(mu+residual_sigma*norm.ppf(adjusted)))
hurdle_lower,hurdle_upper=hurdle_quantile(.1),hurdle_quantile(.9)
hurdle_coverage=np.mean((hurdle_income[hurdle_test]>=hurdle_lower)&(hurdle_income[hurdle_test]<=hurdle_upper))
display(pd.DataFrame({'metrica':['Brier de ingreso cero','Cobertura banda 0,1–0,9','Fracción cero real test'],'valor':[brier_score_loss(hurdle_zero[hurdle_test],p0),hurdle_coverage,hurdle_zero[hurdle_test].mean()]}))
assert (hurdle_lower<=hurdle_upper).all()
''','El monto positivo se supone lognormal y homocedástico en este nuevo generador; es un modelo distinto del boosting anterior. La masa puntual en cero puede hacer conservadora una banda nominal. No se fija un cero porque no llegó el extracto.')
block(c,'6. Cobertura por grupo con incertidumbre binomial',r'''
Para una cobertura observada $\hat c=k/n$, el intervalo Wilson evita el intervalo normal simétrico que puede salir de [0,1]. Su forma usa
$$\frac{\hat c+z^2/(2n)\ \pm\ z\sqrt{\hat c(1-\hat c)/n+z^2/(4n^2)}}{1+z^2/n}.$$

Es incertidumbre de proporción bajo observaciones independientes, no garantía bajo dependencia temporal ni corrección por seleccionar muchos grupos.
''',r'''
def coverage_wilson(k,n,z=1.96):
    proportion=k/n;denominator=1+z*z/n
    center=(proportion+z*z/(2*n))/denominator
    radius=z*np.sqrt(proportion*(1-proportion)/n+z*z/(4*n*n))/denominator
    return center-radius,center+radius
coverage_intervals=[]
for group in [0,1]:
    mask=independent[test]==group
    successes=int(coverage_c[mask].sum());size=int(mask.sum())
    low,high=coverage_wilson(successes,size)
    coverage_intervals.append({'grupo':['Asalariados','Independientes'][group],'n':size,'cobertura':successes/size,'low':low,'high':high})
coverage_intervals=pd.DataFrame(coverage_intervals);display(coverage_intervals)
fig,ax=plt.subplots();positions=np.arange(2)
ax.errorbar(positions,coverage_intervals['cobertura'],yerr=[coverage_intervals['cobertura']-coverage_intervals['low'],coverage_intervals['high']-coverage_intervals['cobertura']],fmt='o',color=TEAL,capsize=5)
ax.axhline(.8,color='#333333',linestyle='--');ax.set_xticks(positions,coverage_intervals['grupo'])
ax.set(ylim=(0,1),ylabel='Cobertura observada y Wilson 95%',title='No confundir cobertura marginal y cobertura por grupo');plt.show()
''','Una diferencia entre grupos necesita una comparación específica; no se declara significancia por mirar dos barras de error. El intervalo cuantifica muestreo en este generador, no corrige cambio de distribución.')
block(c,'7. De una banda a una discrepancia investigable',r'''
Una señal propuesta, no una probabilidad de fraude, es
$$d_i=\max\left(0,\frac{\log D_i-\hat q_u(X_i)}{\hat q_u(X_i)-\hat q_l(X_i)+\varepsilon}\right).$$

D es ingreso declarado en la misma base. Al usar el ancho, una discrepancia en un grupo incierto tiene otra interpretación. Se requiere evidencia independiente para una etiqueta de tergiversación.
''',r'''
declaration=np.exp(y[test])
synthetic_overstatement=advanced_rng.binomial(1,.07,len(test)).astype(bool)
declaration[synthetic_overstatement]*=1.8
width=hi_c-lo_c
income_discrepancy=np.maximum(0,(np.log(declaration)-hi_c)/(width+1e-8))
fig,ax=plt.subplots()
for flag,label,color in [(False,'Sin sobrerreporte inyectado',BLUE),(True,'Sobrerreporte inyectado',GOLD)]:
    values=income_discrepancy[synthetic_overstatement==flag]
    ax.hist(values,bins=np.linspace(0,3,25),density=True,histtype='step',linewidth=1.8,color=color,label=label)
ax.set(xlabel='Score de discrepancia (sin unidad)',ylabel='Densidad dentro del rango mostrado',title='Discrepancia económica no equivale a fraude confirmado');ax.legend(fontsize=8);plt.show()
print('Casos fuera del rango gráfico:',int((income_discrepancy>3).sum()))
advanced_metrics.update({'Cobertura modelo de dos partes':round(float(hurdle_coverage),4),'AP de sobrerreporte sintético':round(float(average_precision_score(synthetic_overstatement,income_discrepancy)),4),'Error máximo de pinball en grilla':round(max(z['error'] for z in pinball_records),4)})
''','El target inyectado sirve para explorar sensibilidad, no para declarar desempeño de detección documental. El histograma acota su rango y se publica el número de casos omitidos; los faltantes requieren ruta de evidencia y no score artificialmente bajo.')

c=lab('02-flow-reconciliation-and-robustness.ipynb',r'''
**Uso:** preparar evidencia económica consistente antes de estimar ingreso o capacidad de pago. **Entrada:** eventos con ID, titularidad, categoría, signo, moneda, período y disponibilidad. **Salida:** conciliación, excepciones de calidad y una base agregada por período.

Este notebook no decide qué documento es auténtico. Desarrolla un motor pequeño de reconciliación sintética, robustez de la referencia y una ruta de abstención cuando el dato no es identificable. La periodicidad declarada debe distinguir pago cada 14 días de dos veces por mes.
''')
block(c,'4. Invariancia de flujos internos y deduplicación',r'''
Para cuentas consolidadas de un titular, los traslados internos deben cancelarse. Se usa
$$\Delta B=\sum F_{externos}^{in}-\sum F_{externos}^{out}+F_{financiacion}-F_{servicio\ deuda}.$$

La identidad de caja no convierte toda entrada externa en ingreso. La deduplicación se hace por evento y los registros contradictorios con el mismo ID son una excepción, no se escoge silenciosamente el primero.
''',r'''
ledger=[{'id':'pay-1','type':'salary','amount':3_000_000.,'available':1.},
        {'id':'transfer-in','type':'internal','amount':2_000_000.,'available':2.},
        {'id':'transfer-out','type':'internal','amount':-2_000_000.,'available':2.},
        {'id':'loan-1','type':'loan','amount':5_000_000.,'available':3.},
        {'id':'spend-1','type':'expense','amount':-1_000_000.,'available':4.}]
def reconcile(records,cutoff):
    unique={}
    for event in records:
        if event['available']>cutoff:continue
        if event['id'] in unique and event!=unique[event['id']]:raise ValueError('Conflicting duplicate')
        if not np.isfinite(event['amount']):raise ValueError('Invalid amount')
        unique[event['id']]=event
    income=sum(e['amount'] for e in unique.values() if e['type']=='salary')
    delta=sum(e['amount'] for e in unique.values())
    internal=sum(e['amount'] for e in unique.values() if e['type']=='internal')
    return {'income':income,'balance_change':delta,'internal_net':internal,'events':len(unique)}
clean_result=reconcile(ledger,10)
assert clean_result==reconcile(ledger+[ledger[0]],10)
without_internal=reconcile([e for e in ledger if e['type']!='internal'],10)
assert clean_result['income']==without_internal['income']
assert clean_result['balance_change']==without_internal['balance_change']
display(pd.DataFrame([clean_result,without_internal],index=['Completo','Sin traslado interno']))
''','Esta igualdad supone que ambas patas internas llegaron al corte. Si solo llegó una, aparece una partida de conciliación; no se debe inventar la otra ni sumarla a ingreso disponible.')
block(c,'5. Datos tardíos y contradicciones de identidad de evento',r'''
Un snapshot en t usa $a_j\le t$. La reconstrucción histórica no usa eventos que se conocieron después. Si dos filas con el mismo ID discrepan en monto o tipo, la igualdad contable no justifica sobrescribir la historia.
''',r'''
late_salary={'id':'pay-late','type':'salary','amount':800_000.,'available':15.}
cutoffs=[5,10,15,20]
cutoff_rows=[{'corte':t,**reconcile(ledger+[late_salary],t)} for t in cutoffs]
display(pd.DataFrame(cutoff_rows))
assert reconcile(ledger,10)==reconcile(ledger+[late_salary],10)
conflict_rejected=False
try:reconcile(ledger+[{**ledger[0],'amount':4_000_000.}],10)
except ValueError:conflict_rejected=True
assert conflict_rejected
''','Para producción se necesita también fecha del hecho, versión y correcciones bitemporales. Este motor de ejemplo cubre disponibilidad y conflicto de ID; no implementa un libro mayor ni una política contable institucional.')
block(c,'6. Cuándo abstenerse de normalizar con MAD',r'''
Si $MAD=0$ o la referencia es muy pequeña, dividir por un epsilon puede fabricar un score enorme. La alternativa operacional propuesta es devolver estado de cobertura insuficiente:
$$score(x)=\varnothing\quad\text{si }n<n_{min}\text{ o escala}<s_{min}.$$

Un fallback debe tener propósito y población documentados. No se fuerza una probabilidad porque una API exige un número.
''',r'''
def robust_discrepancy(value,reference,min_n=30,min_scale=1e-6):
    reference=np.asarray(reference,dtype=float)
    reference=reference[np.isfinite(reference)]
    if len(reference)<min_n:return None,'insufficient_reference'
    location=np.median(reference);scale=1.4826*np.median(np.abs(reference-location))
    if scale<min_scale:return None,'degenerate_scale'
    return float((value-location)/scale),'ok'
coverage_states=[robust_discrepancy(15.,np.ones(40)*14.),robust_discrepancy(15.,np.arange(10)),robust_discrepancy(15.,clean)]
display(pd.DataFrame(coverage_states,columns=['score','estado']))
assert coverage_states[0][0] is None and coverage_states[1][0] is None
assert coverage_states[2][1]=='ok'
''','La abstención es un resultado válido del contrato. Puede derivar a verificación adicional o revisión de calidad; no confirma ni descarta una irregularidad del solicitante.')
block(c,'7. Contaminación, mezcla y sensibilidad del umbral',r'''
Un método robusto no resuelve una mezcla legítima de actividades. Se comparan umbrales z>2/3/4 sobre dos grupos con distinta media, usando una referencia agregada frente a referencias separadas. La salida es fracción señalada en legítimos simulados.
''',r'''
group_a=advanced_rng.normal(14.5,.15,1200)
group_b=advanced_rng.normal(15.2,.30,600)
pooled=np.r_[group_a,group_b]
threshold_rows=[]
for cutoff in [2.,3.,4.]:
    for name,values in [('A',group_a),('B',group_b)]:
        pooled_scores=np.array([robust_discrepancy(float(v),pooled)[0] for v in values])
        local_scores=np.array([robust_discrepancy(float(v),values)[0] for v in values])
        threshold_rows.append({'grupo':name,'umbral':cutoff,'alarma_referencia_agregada':np.mean(pooled_scores>cutoff),'alarma_referencia_local':np.mean(local_scores>cutoff)})
threshold_rows=pd.DataFrame(threshold_rows);display(threshold_rows)
fig,ax=plt.subplots()
for group,color in [('A',BLUE),('B',GOLD)]:
    part=threshold_rows[threshold_rows['grupo']==group]
    ax.plot(part['umbral'],part['alarma_referencia_agregada'],marker='o',color=color,label=f'{group}: agregada')
    ax.plot(part['umbral'],part['alarma_referencia_local'],marker='s',linestyle='--',color=color,label=f'{group}: local')
ax.set(xlabel='Umbral del score robusto',ylabel='Fracción de legítimos señalados',ylim=(0,1),title='Segmentación de referencia y falsas discrepancias');ax.legend(fontsize=8);plt.show()
advanced_metrics.update({'Ingreso conciliado por eventos (COP)':int(clean_result['income']),'Cambio de saldo consolidado (COP)':int(clean_result['balance_change']),'Duplicado contradictorio rechazado':conflict_rejected})
''','Las referencias de este experimento se construyen con los propios grupos legítimos para aislar el efecto de mezcla; no se presenta como validación fuera de muestra. Una implementación debe estimar la referencia en entrenamiento y evaluar en un período posterior.')

c=lab('01-case-mix-and-shrinkage.ipynb',r'''
**Uso:** priorizar investigación de omisiones de control por canal, comercio o equipo. **Entrada:** denominadores por producto, versión de política y eventos maduros. **Salida:** exceso ajustado e incertidumbre; no una acusación de fraude interno.

Se distinguen mezcla, dispersión entre grupos y variación temporal. El modelo de referencia anterior es conocido por el generador. Ahora se ajusta un modelo beta-binomial a un conjunto de entrenamiento separado y se contrasta con un baseline binomial sobre grupos posteriores.
''')
block(c,'4. De binomial a beta-binomial',r'''
Si $p_g\sim Beta(a,b)$ y $O_g\mid p_g\sim Binomial(n_g,p_g)$:
$$E[p_g]=\mu=\frac a{a+b},\quad\rho=\frac1{a+b+1},$$
$$E[O_g]=n_g\mu,\quad Var(O_g)=n_g\mu(1-\mu)[1+(n_g-1)\rho].$$

La verosimilitud marginal es $\binom nO B(O+a,n-O+b)/B(a,b)$. No aplica sin ajuste a grupos con mezclas de producto diferentes; el experimento usa una referencia homogénea independiente del anterior.
''',r'''
from scipy.special import betaln,gammaln
from scipy.optimize import minimize
from scipy.stats import betabinom,binom,beta
bb_n=100
bb_p_train=advanced_rng.beta(2.,18.,250)
bb_o_train=advanced_rng.binomial(bb_n,bb_p_train)
bb_p_test=advanced_rng.beta(2.,18.,180)
bb_o_test=advanced_rng.binomial(bb_n,bb_p_test)
def bb_negative_log_likelihood(log_ab):
    a,b=np.exp(log_ab)
    log_choose=gammaln(bb_n+1)-gammaln(bb_o_train+1)-gammaln(bb_n-bb_o_train+1)
    return -float(np.sum(log_choose+betaln(bb_o_train+a,bb_n-bb_o_train+b)-betaln(a,b)))
bb_fit=minimize(bb_negative_log_likelihood,np.log([2.,18.]),method='L-BFGS-B',bounds=[(-5,8),(-5,8)])
assert bb_fit.success
a_hat,b_hat=np.exp(bb_fit.x);mu_hat=a_hat/(a_hat+b_hat);rho_hat=1/(a_hat+b_hat+1)
display(pd.DataFrame({'parametro':['a','b','mu','rho'],'estimado':[a_hat,b_hat,mu_hat,rho_hat],'verdad_sintetica':[2,18,.1,1/21]}))
''','El ajuste aprende hiperparámetros en 250 grupos, no en los grupos evaluados. La beta-binomial capta heterogeneidad de tasas bajo su supuesto, no distingue por qué varían ni identifica fraude.')
block(c,'5. Comparación predictiva en grupos no usados en ajuste',r'''
La densidad predictiva se evalúa con log score: $-m^{-1}\sum_g\log P(O_g\mid n_g)$. Se comparan binomial con media estimada y beta-binomial con hiperparámetros estimados. Ambos usan el mismo entrenamiento y n.
''',r'''
mu_bin=bb_o_train.sum()/(len(bb_o_train)*bb_n)
bin_ll=binom.logpmf(bb_o_test,bb_n,mu_bin)
bb_ll=betabinom.logpmf(bb_o_test,bb_n,a_hat,b_hat)
predictive_scores=pd.DataFrame({'modelo':['Binomial','Beta-binomial'],'NLL_promedio':[-bin_ll.mean(),-bb_ll.mean()]})
display(predictive_scores)
counts=np.arange(bb_n+1)
fig,ax=plt.subplots();ax.plot(counts,binom.pmf(counts,bb_n,mu_bin),color=BLUE,label='Binomial ajustada')
ax.plot(counts,betabinom.pmf(counts,bb_n,a_hat,b_hat),color=TEAL,label='Beta-binomial ajustada')
ax.set(xlabel='Omisiones por 100 solicitudes',ylabel='Probabilidad predictiva',title='La sobredispersión cambia las colas esperadas');ax.legend();plt.show()
assert np.isclose(betabinom.pmf(counts,bb_n,a_hat,b_hat).sum(),1)
''','Si se usa una binomial demasiado estrecha pueden aparecer falsas anomalías. Un modelo disperso también puede ocultar un cambio real: evaluar únicamente log score no determina la política de alertas.')
block(c,'6. Actualización de una tasa por grupo',r'''
Con hiperparámetros ya ajustados y un nuevo grupo observado:
$$p_g\mid O_g\sim Beta(a+O_g,b+n_g-O_g).$$

La media posterior contrae la tasa y sus cuantiles resumen incertidumbre condicional al prior ajustado. La inferencia empirical Bayes no incluye incertidumbre de los hiperparámetros; debe decirse explícitamente.
''',r'''
posterior_rows=[]
for observed in [0,5,15,30]:
    aa,bb=a_hat+observed,b_hat+bb_n-observed
    posterior_rows.append({'O':observed,'n':bb_n,'tasa_bruta':observed/bb_n,'media_posterior':aa/(aa+bb),'low95':beta.ppf(.025,aa,bb),'high95':beta.ppf(.975,aa,bb)})
posterior_rows=pd.DataFrame(posterior_rows);display(posterior_rows)
fig,ax=plt.subplots();ax.errorbar(posterior_rows['O'],posterior_rows['media_posterior'],yerr=[posterior_rows['media_posterior']-posterior_rows['low95'],posterior_rows['high95']-posterior_rows['media_posterior']],fmt='o',color=TEAL,capsize=5)
ax.scatter(posterior_rows['O'],posterior_rows['tasa_bruta'],marker='x',color=GOLD,label='Tasa bruta')
ax.set(xlabel='Omisiones observadas en 100 solicitudes',ylabel='Tasa e intervalo posterior 95%',title='Contracción y dispersión de un grupo nuevo');ax.legend();plt.show()
''','Estos intervalos no son p-valores ni evidencia de conducta indebida. Para comparar grupos con productos diferentes hay que ajustar la media de referencia por mezcla antes de interpretar el exceso.')
block(c,'7. Alarmas predictivas y alcance de la evaluación',r'''
Una cola superior de referencia es $P(O\ge O_{obs})$. Se compara la fracción de grupos de prueba con cola menor que 1% bajo ambas referencias. La distribución es discreta y el ajuste es estimado; no se exige exactamente 1%.
''',r'''
bin_tail=binom.sf(bb_o_test-1,bb_n,mu_bin)
bb_tail=betabinom.sf(bb_o_test-1,bb_n,a_hat,b_hat)
display(pd.DataFrame({'referencia':['Binomial','Beta-binomial'],'fraccion_grupos_en_cola_1pct':[np.mean(bin_tail<.01),np.mean(bb_tail<.01)],'grupos_test':[len(bb_o_test)]*2}))
assert np.isfinite(bb_tail).all()
advanced_metrics.update({'rho beta-binomial ajustado':round(float(rho_hat),4),'NLL beta-binomial test':round(float(-bb_ll.mean()),4),'NLL binomial test':round(float(-bin_ll.mean()),4)})
''','La comparación usa grupos generados por beta-binomial, lo que favorece al modelo correctamente especificado. Conservar el resultado como recuperación de un mecanismo conocido, no como ganador universal; probar cambios de mezcla y lotes dependientes antes de promoverlo.')

c=lab('02-cusum-false-alarms-and-delay.ipynb',r'''
**Uso:** detectar aumentos persistentes de una señal de control y organizar revisión. **Entrada:** residuos estandarizados con referencia congelada, horizonte y canales. **Salida:** fecha de alerta y evidencia acumulada. El modelo no atribuye causa ni intención.

El umbral de una sola serie normal independiente no se puede copiar a cincuenta canales correlacionados. Se amplían derivaciones con razón de verosimilitud, autocorrelación, multiplicidad y censura de demoras. Estos ejercicios cambian supuestos de forma controlada sin volver a elegir h con el test.
''')
block(c,'4. CUSUM como acumulación de log-verosimilitud',r'''
Para $z\sim N(0,1)$ contra $N(\delta,1)$:
$$\log\frac{f_\delta(z)}{f_0(z)}=\delta z-\frac{\delta^2}{2}=\delta(z-\delta/2).$$

Para delta positivo y constante, la recursión normalizada usa k=delta/2. El h calibrado controla otra dimensión: tolerancia a falsas alarmas bajo la referencia. Una referencia estimada o autocorrelación modifica esa calibración.
''',r'''
from scipy.stats import norm
z_grid=np.linspace(-3,4,50);delta=1.
llr_direct=norm.logpdf(z_grid,loc=delta)-norm.logpdf(z_grid,loc=0)
llr_formula=delta*z_grid-delta**2/2
assert np.allclose(llr_direct,llr_formula)
llr_table=pd.DataFrame({'z':z_grid[::8],'log_ratio':llr_direct[::8],'incremento_normalizado':z_grid[::8]-.5})
display(llr_table)
''','Esta derivación explica k=0,5 para un cambio de una desviación estándar en el caso idealizado. No justifica usarlo igual sobre tasas crudas, volúmenes variables o residuos con otra distribución.')
block(c,'5. Autocorrelación rompe la referencia independiente',r'''
Se genera $z_t=\phi z_{t-1}+\sqrt{1-\phi^2}\epsilon_t$ con inicio estacionario. Su varianza marginal es 1, pero observaciones positivas se agrupan si phi>0. Se conserva h de la referencia independiente para medir sensibilidad.
''',r'''
correlation_rows=[]
for phi in [0.,.3,.6,.85]:
    simulations=advanced_rng.normal(size=(400,horizon))
    paths=np.empty_like(simulations);paths[:,0]=simulations[:,0]
    for t in range(1,horizon):paths[:,t]=phi*paths[:,t-1]+np.sqrt(1-phi*phi)*simulations[:,t]
    rate=np.mean([cusum(path).max()>h for path in paths])
    correlation_rows.append({'phi':phi,'FA_en_120_dias':rate,'replicas':len(paths)})
correlation_rows=pd.DataFrame(correlation_rows);display(correlation_rows)
fig,ax=plt.subplots();ax.plot(correlation_rows['phi'],correlation_rows['FA_en_120_dias'],color=GOLD,marker='o')
ax.axhline(.05,color='#333333',linestyle='--',label='Objetivo nominal de referencia')
ax.set(ylim=(0,1),xlabel='Autocorrelación phi',ylabel='Réplicas con al menos una alarma',title='Misma varianza marginal, distinta falsa alarma');ax.legend(fontsize=8);plt.show()
''','No se recalibra con estas réplicas: la curva muestra un fallo del supuesto original. Para una aplicación se necesita modelar residuos, recalibrar con bloques o simular la dependencia relevante y reservar otro conjunto para evaluar.')
block(c,'6. Múltiples canales: del umbral individual al conjunto',r'''
Para canales independientes con probabilidad individual alpha, la probabilidad de alguna alarma es $1-(1-\alpha)^G$. Esa fórmula no vale automáticamente con correlación. Se calibra además un umbral por máximo conjunto de cinco canales a horizonte fijo.
''',r'''
G=5
multi_cal=advanced_rng.normal(size=(300,G,horizon))
max_joint=np.array([max(cusum(channel).max() for channel in replication) for replication in multi_cal])
h_joint=float(np.quantile(max_joint,.95,method='higher'))
multi_test=advanced_rng.normal(size=(300,G,horizon))
max_joint_test=np.array([max(cusum(channel).max() for channel in replication) for replication in multi_test])
individual_reuse_rate=float(np.mean(max_joint_test>h))
joint_rate=float(np.mean(max_joint_test>h_joint))
display(pd.DataFrame({'politica':['Reutilizar h individual','Calibrar máximo conjunto'],'umbral':[h,h_joint],'FA_alguno_en_5_canales':[individual_reuse_rate,joint_rate],'replicas':[300,300]}))
fig,ax=plt.subplots();ax.bar(['h individual','h conjunto'],[individual_reuse_rate,joint_rate],color=[GOLD,TEAL])
ax.axhline(.05,color='#333333',linestyle='--');ax.set(ylim=(0,1),ylabel='Réplicas con alarma en algún canal',title='Multiplicidad a horizonte fijo: cinco canales');plt.show()
''','La calibración usa otras réplicas y respeta el presupuesto nominal solo en el sentido estadístico del simulador. No controla una operación indefinida, reinicios ni nuevas versiones de canal. Publicar incertidumbre de Monte Carlo antes de exigir una igualdad exacta.')
block(c,'7. Demoras censuradas y costo de detección',r'''
La demora de un cambio es $D=T_{alarma}-T_{cambio}+1$. Si no se detecta antes de H, D está censurada; la mediana de detectados no estima la mediana de todos. Se añade un costo ilustrativo por día de exposición y un costo por prealarma, con parámetros declarados.
''',r'''
per_day_loss=25_000.;false_case_cost=30_000.
delay_cost_rows=[]
for row in records:
    eligible=row['elegibles_sin_prealarma'];detected=row['detectados']
    # This is a proxy based on a detected-only median, NOT expected full delay.
    median_proxy=row['mediana_dias_solo_detectados']
    censoring=1-detected/eligible
    delay_cost_rows.append({'cambio':row['shift'],'censura_en_elegibles':censoring,
                            'mediana_detectados_dias':median_proxy,
                            'costo_mediana_detectados_COP':median_proxy*per_day_loss,
                            'costo_prealarma_promedio_COP':row['prealarma']*false_case_cost})
display(pd.DataFrame(delay_cost_rows))
assert h_joint>=h
advanced_metrics.update({'FA con phi=0,85':round(float(correlation_rows.iloc[-1]['FA_en_120_dias']),4),'FA al reutilizar umbral en 5 canales':round(individual_reuse_rate,4),'FA con umbral conjunto':round(joint_rate,4)})
''','El costo basado en mediana se etiqueta como proxy y no se suma para declarar beneficio esperado. Un modelo completo de pérdida necesita tiempos de exposición, casos censurados, contención real y capacidad de investigación; esos datos no están simulados aquí.')


def deepen_all():
    for path in sorted(BASE.glob('*/notebooks/*.ipynb')):
        if path.name not in LABS:continue
        nb=nbf.read(path,as_version=4)
        if nb.metadata.get('depth_version')==2:continue
        position=next(i for i,cell in enumerate(nb.cells) if cell.cell_type=='markdown' and cell.source.startswith('## Comprobaciones y límites'))
        inserted=LABS[path.name]
        # Put a model map before the new experiments, keeping the old derivations.
        nb.cells[position:position]=inserted
        for cell in nb.cells:
            if cell.cell_type=='code' and 'LAB_METRICS:' in cell.source:
                cell.source=cell.source.replace('print("LAB_METRICS:', 'metrics.update(advanced_metrics)\nprint("LAB_METRICS:')
        nb.cells.append(md('## Uso responsable y ficha mínima de salida\n\nAntes de una aplicación institucional, registrar población, corte de información, versión del modelo, horizonte, unidades y cobertura de fuentes. Separar score de anomalía, probabilidad estimada y costo por acción. Una discrepancia o un desvío requiere evidencia independiente antes de llamarlo fraude. El experimento está completo en su alcance sintético; no sustituye calibración externa, integración de datos o validación independiente.'))
        nb.cells.append(md('## Preguntas para refutar el desarrollo\n\n1. ¿La mejora persiste al cambiar el mecanismo generador y la cohorte?\n2. ¿Qué variable solo estaría disponible después de decidir?\n3. ¿Cuánto del beneficio depende de una eficacia o cobertura supuesta?\n4. ¿Qué caso legítimo produce la misma señal?\n5. ¿Puede otra persona reconstruir el resultado desde las celdas y los parámetros?'))
        nb.cells.extend(reference_cells(path.name))
        for index,cell in enumerate(nb.cells):cell['id']=hashlib.sha256((str(path.relative_to(BASE))+':'+str(index)).encode()).hexdigest()[:16]
        nb.metadata['depth_version']=2
        nbf.validate(nb);nbf.write(nb,path)
    print('Deepened eight specialized notebooks')

if __name__=='__main__':deepen_all()
