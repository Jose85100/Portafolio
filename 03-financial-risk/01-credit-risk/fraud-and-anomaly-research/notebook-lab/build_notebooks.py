"""Author eight specialized research notebooks with nbformat (no cached results)."""
from pathlib import Path
import textwrap
import hashlib
import nbformat as nbf

BASE=Path(__file__).resolve().parents[1]
SETUP=r'''
%matplotlib inline
from pathlib import Path
import sys, math, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
from sklearn.metrics import average_precision_score, brier_score_loss
base = next(p for p in [Path.cwd(), *Path.cwd().parents] if p.name == 'fraud-and-anomaly-research')
sys.path.insert(0, str(base / 'loss-minimization-engine'))
from src.engine import Case, Action, Scenario, optimize, expected_cost, shared_entity_count
rng = np.random.default_rng(20261021)
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({'figure.figsize': (8, 4.5), 'figure.dpi': 120, 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False, 'grid.alpha': .25})
BLUE, TEAL, GOLD, PURPLE = '#386A96', '#217A72', '#B37D2E', '#73579D'
pd.options.display.float_format = '{:,.4f}'.format
'''

def md(text): return nbf.v4.new_markdown_cell(textwrap.dedent(text).strip())
def code(text): return nbf.v4.new_code_cell(textwrap.dedent(text).strip())
def start(title,question,assumptions):
    return [md('# '+title),md('## Resumen de la ejecución\n\nSe completará al ejecutar todas las celdas.'),
            md('## Objetivo y método\n\n'+question+'\n\n### Supuestos y población\n\n'+assumptions+'\n\nTodos los datos son sintéticos. Las cifras ilustran mecanismos y no constituyen desempeño observado en una entidad. Fecha de desarrollo: 21 de octubre de 2026.'),
            md('## Entorno reproducible\n\nEjecutar en orden, desde esta carpeta o una subcarpeta de la línea de fraude. La semilla y los parámetros quedan en las celdas; no se consulta internet ni se leen datos de clientes.'), code(SETUP)]
def section(cells,title,equation,source,interpretation):
    cells.extend([md('## '+title+'\n\n'+equation),code(source),md(interpretation)])
def end(cells,checks,metrics,questions,refs):
    cells.extend([md('## Comprobaciones y límites\n\nLas identidades y contraejemplos siguientes son parte del experimento; no verifican desempeño productivo.'),code(checks),
                  md('## Resultados computados'),code('metrics = '+metrics+'\nprint("LAB_METRICS:" + json.dumps(metrics, ensure_ascii=False))'),
                  md('## Ideas y preguntas para continuar\n\n'+questions),md('## Fuentes y relación con el proyecto\n\n'+refs+'\n\nConsultar también `../README.md` y `../../MODEL_AND_LOSS_METHODS.md`.')])
def save(project,name,cells):
    path=BASE/project/'notebooks'/name;path.parent.mkdir(exist_ok=True)
    nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'},'research_scope':'synthetic experiment; no production data'})
    for index,cell in enumerate(nb.cells):
        cell['id']=hashlib.sha256((str(path.relative_to(BASE))+':'+str(index)).encode()).hexdigest()[:16]
    nbf.validate(nb);nbf.write(nb,path)

# 1. Bayesian evidence and correlation.
c=start('KYC: Bayes, evidencia duplicada y calibración',
        '¿Cuánto cambia una probabilidad de fraude con una señal y qué error aparece al contar la misma evidencia dos veces? Derivamos Bayes, construimos un contraejemplo exacto y comparamos logit con calibración posterior.',
        'Una señal binaria tiene sensibilidad y falso positivo conocidos por el simulador. Los bloques de entrenamiento, calibración y prueba se ordenan por índice; su mecanismo es estacionario y las etiquetas están completas.')
section(c,'1. De prevalencia a probabilidad posterior',r'''
Sea $Y=1$ fraude y $E=1$ evidencia positiva. Con prevalencia $\pi$, sensibilidad $s$ y falso positivo $f$:

$$P(Y=1\mid E=1)=\frac{\pi s}{\pi s+(1-\pi)f}.$$

En odds, $O(Y\mid E)=O(Y)LR(E)$ y $LR(E=1)=s/f$. Una señal informativa puede tener precisión baja si la prevalencia es pequeña. No reemplazar $P(Y\mid E)$ por $P(E\mid Y)$.
''',r'''
prevalence, sensitivity, false_positive = .025, .82, .08
posterior = prevalence*sensitivity/(prevalence*sensitivity+(1-prevalence)*false_positive)
prior_grid = np.linspace(.001,.15,100)
posterior_grid = prior_grid*sensitivity/(prior_grid*sensitivity+(1-prior_grid)*false_positive)
display(pd.DataFrame({'prevalencia':[prevalence], 'sensibilidad':[sensitivity], 'falso_positivo':[false_positive], 'posterior_positivo':[posterior]}))
fig,ax=plt.subplots();ax.plot(prior_grid,posterior_grid,color=BLUE)
ax.set(xlabel='Prevalencia de fraude (fracción)',ylabel='Posterior ante evidencia positiva',title='La tasa base condiciona el valor de la evidencia')
plt.show()
''','La curva mantiene fija la calidad de la señal. Cambiar la prevalencia no convierte una misma verificación en una prueba concluyente. Las probabilidades provienen del supuesto conocido, no de una fuente KYC real.')
section(c,'2. Contraejemplo: dos campos, una sola evidencia',r'''
Si $E_2=E_1$, la información conjunta es la misma. La identidad correcta es
$P(Y\mid E_1,E_2)=P(Y\mid E_1)$. Bajo una independencia falsa se multiplicaría $LR^2$ y se exageraría la confianza.
''',r'''
prior_odds=prevalence/(1-prevalence)
likelihood_ratio=sensitivity/false_positive
naive_odds=prior_odds*likelihood_ratio**2
naive_probability=naive_odds/(1+naive_odds)
comparison=pd.DataFrame({'método':['Una evidencia / duplicación correcta','Duplicación con independencia falsa'],
                         'probabilidad':[posterior,naive_probability]})
display(comparison)
fig,ax=plt.subplots();ax.barh(comparison['método'],comparison['probabilidad'],color=[BLUE,GOLD])
ax.set(xlim=(0,1),xlabel='Probabilidad posterior',title='Duplicar evidencia no duplica información');fig.tight_layout();plt.show()
''','El segundo cálculo es deliberadamente inválido. Dos proveedores que copian el mismo origen no generan automáticamente dos confirmaciones independientes. La trazabilidad de origen importa tanto como el número de campos.')
section(c,'3. Estimación y calibración en ventanas separadas',r'''
Un logit estima $\hat p=\sigma(\beta_0+\beta^Tx)$ mediante log loss. Un calibrador posterior estima $\tilde p=\sigma(a+b\,\mathrm{logit}(\hat p))$. Las muestras para ambos ajustes son distintas. Brier es $n^{-1}\sum_i(\hat p_i-y_i)^2$.
''',r'''
from sklearn.linear_model import LogisticRegression
n=4000
y=rng.binomial(1,prevalence,n)
e1=rng.binomial(1,np.where(y==1,sensitivity,false_positive))
e2=e1.copy()
x=np.column_stack([e1,e2,rng.normal(size=n)])
train,cal,test=np.arange(2000),np.arange(2000,3000),np.arange(3000,4000)
model=LogisticRegression(C=1,max_iter=500).fit(x[train],y[train])
weighted=LogisticRegression(C=1,class_weight='balanced',max_iter=500).fit(x[train],y[train])
calibrator=LogisticRegression(C=100,max_iter=500).fit(weighted.decision_function(x[cal]).reshape(-1,1),y[cal])
predictions={'logit':model.predict_proba(x[test])[:,1],
             'logit balanceado sin calibrar':weighted.predict_proba(x[test])[:,1],
             'balanceado y calibrado':calibrator.predict_proba(weighted.decision_function(x[test]).reshape(-1,1))[:,1]}
score_table=pd.DataFrame([{'modelo':k,'AP':average_precision_score(y[test],v),'Brier':brier_score_loss(y[test],v),'media_p':v.mean()} for k,v in predictions.items()])
display(score_table)
print('Prevalencia de prueba:',y[test].mean(),'positivos:',y[test].sum())
''','Balancear clases cambia el ajuste y puede alterar la escala probabilística. La tabla permite comprobarlo sin asumir que calibrar siempre mejora. Con pocos positivos, otra semilla o ventana puede modificar el resultado; este notebook no elige hiperparámetros por el test.')
end(c,'assert posterior < naive_probability < 1\nassert np.array_equal(e1,e2)\nassert all(np.isfinite(v).all() and ((v>=0)&(v<=1)).all() for v in predictions.values())',
    "{'Posterior correcto': round(posterior,4), 'Posterior inválido por duplicación': round(naive_probability,4), 'Positivos de prueba': int(y[test].sum())}",
    '1. Estimar dependencia entre fuentes y conservar el origen de cada campo.\n2. Comparar calibración por proveedor con contracción jerárquica cuando haya pocos positivos.\n3. Evaluar degradación al cambiar prevalencia sin cambiar sensibilidad.\n4. Investigar reglas de abstención cuando faltan fuentes; faltante no significa legítimo.',
    '- [Calibración: documentación oficial scikit-learn](https://scikit-learn.org/stable/modules/calibration.html).\n- [NIST: identidad y gestión de evidencia](https://pages.nist.gov/800-63-4/sp800-63a.html).\nLas derivaciones de Bayes y el contraejemplo se calculan directamente en estas celdas.')
save('01-identity-kyc-consistency','01-bayes-evidence-and-calibration.ipynb',c)

# 2. KYC actions.
c=start('KYC: umbrales económicos y capacidad de revisión',
        '¿Cuándo conviene verificar, revisar o continuar? Derivamos el umbral económico y pasamos de decisiones aisladas a una asignación bajo un presupuesto común.',
        'Los casos son independientes. Probabilidad, pérdida neta, eficacia y fricción son supuestos numéricos; no hay rechazo automático ni efecto causal estimado.')
section(c,'1. Derivar el beneficio y el umbral',r'''
$$C_i(a)=p_iL_i(1-q_a)+c_a+(1-p_i)f_a,\quad B_i(a)=p_iL_iq_a-c_a-(1-p_i)f_a.$$

Si $Lq+f>0$, $B>0$ equivale a $p>(c+f)/(Lq+f)$. No existe un umbral universal de 0,5. Si el denominador es cero, comparar costos directamente.
''',r'''
actions=[Action('allow',0,0,0,0),Action('verify',.35,4000,2500,3),Action('review',.8,18000,15000,15)]
loss_grid=np.geomspace(50_000,10_000_000,90)
p_grid=np.linspace(.001,.8,80)
cost_tensor=np.array([[[expected_cost(Case('grid',float(p),float(L)),a) for a in actions] for L in loss_grid] for p in p_grid])
choices=np.argmin(cost_tensor,axis=2)
from matplotlib.colors import ListedColormap
fig,ax=plt.subplots();im=ax.pcolormesh(loss_grid/1e6,p_grid,choices,cmap=ListedColormap(['#D6DFE5',BLUE,TEAL]),vmin=-.5,vmax=2.5,shading='auto')
ax.set(xscale='log',xlabel='Pérdida condicionada a fraude (millones COP)',ylabel='Probabilidad de fraude',title='Acción de menor costo sin restricción de capacidad')
cb=fig.colorbar(im,ax=ax,ticks=[0,1,2]);cb.ax.set_yticklabels(['Continuar','Verificar','Revisar']);plt.show()
''','El mapa se resuelve sin presupuesto común y solo muestra el efecto de monto y probabilidad. No debe interpretarse como política operativa: al limitar minutos, algunos casos reciben otra acción.')
section(c,'2. Elegir acciones conjuntamente',r'''
$$\min_{x_{ia}\in\{0,1\}}\sum_{ia}x_{ia}C_i(a),\quad\sum_a x_{ia}=1,\quad\sum_{ia}t_ax_{ia}\leq T.$$

Se compara el mismo conjunto de casos al aumentar capacidad. El conjunto factible crece: el costo óptimo no puede aumentar bajo los mismos supuestos.
''',r'''
probabilities=rng.beta(1,8,35);losses=rng.lognormal(np.log(1_500_000),.8,35)
cases=[Case(f'synthetic-{i}',float(p),float(L)) for i,(p,L) in enumerate(zip(probabilities,losses))]
capacities=[0,15,30,60,90,150]
plans=[optimize(cases,actions,T) for T in capacities]
capacity_table=pd.DataFrame([{'presupuesto_min':T,'usado_min':p['effort_minutes'],'costo_COP':p['objective_cop'],'revisiones':p['actions'].count('review'),'verificaciones':p['actions'].count('verify')} for T,p in zip(capacities,plans)])
display(capacity_table)
fig,ax=plt.subplots();ax.plot(capacities,capacity_table['costo_COP']/1e6,color=TEAL,marker='o')
ax.set(xlabel='Capacidad de investigación (minutos)',ylabel='Costo esperado (millones COP)',title='Frontera económica con casos y costos fijos');plt.show()
''','La pendiente depende de casos concretos; no es una estimación del retorno de contratar investigadores. El presupuesto se aplica en minutos y puede quedar sin usar cuando la intervención no tiene beneficio.')
section(c,'3. Política congelada ante eficacia incierta',r'''
Se conserva el plan elegido con $T=60$ y se reevalúa con $q'_a=\gamma q_a$ acotado a 1. Esto es sensibilidad de supuestos, no recalibración con resultados de prueba.
''',r'''
frozen=plans[3];lookup={a.name:a for a in actions}
no_action=sum(expected_cost(case,actions[0]) for case in cases)
sensitivity=[]
for gamma in [0,.25,.5,.75,1,1.25]:
    scenario=Scenario('efficacy',effectiveness_multiplier=gamma)
    total=sum(expected_cost(case,lookup[a],scenario) for case,a in zip(cases,frozen['actions']))
    sensitivity.append({'gamma':gamma,'costo_COP':total,'beneficio_vs_continuar_COP':no_action-total})
display(pd.DataFrame(sensitivity))
''','Con eficacia cero no hay prevención, pero persisten costos y fricción. Una probabilidad bien estimada no basta: la intervención necesita demostrar utilidad y el supuesto de eficacia debe investigarse.')
end(c,"assert all(a['objective_cop']>=b['objective_cop']-1e-6 for a,b in zip(plans,plans[1:]))\nassert sensitivity[0]['beneficio_vs_continuar_COP'] < 0\nassert plans[0]['actions']==['allow']*len(cases)",
    "{'Costo sin capacidad (COP)': round(plans[0]['objective_cop'],2), 'Costo con 60 minutos (COP)': round(plans[3]['objective_cop'],2), 'Costo adicional con eficacia cero (COP)': round(-sensitivity[0]['beneficio_vs_continuar_COP'],2)}",
    '1. Estimar eficacia por tipo de verificación con un piloto defendible.\n2. Añadir tiempo por caso y dos recursos: analista y proveedor.\n3. Comparar valor de información de una verificación antes de decidir la revisión.\n4. Incorporar demoras y abandono de clientes legítimos como resultados separados.',
    '- Motor local: `../../loss-minimization-engine/src/engine.py`.\n- [SciPy MILP](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html).')
save('01-identity-kyc-consistency','02-economic-thresholds-and-capacity.ipynb',c)

# 3. Temporal graph.
c=start('Redes: variables al corte y fuga de información',
        '¿Cómo distinguir reutilización observada de conexiones que solo se conocen después? Construimos enlaces sintéticos reales, agregados bitemporales y un contraejemplo retrospectivo.',
        'Un enlace tiene application_id, entity, event_at y available_at. No se usan etiquetas de vecinos. Compartir un dispositivo puede ser legítimo; el conteo no es una probabilidad de fraude.')
section(c,'1. Construir el grafo temporal',r'''
$$N_v(t,w)=\left|\{i: v_i=v,\ t-w\le e_i<t,\ a_i\le t,\ i\ne i_{actual}\}\right|.$$

$e_i$ es fecha del hecho y $a_i$ disponibilidad. Se cuentan solicitudes distintas y se excluye la solicitud actual. Un dato tardío no pertenece al pasado disponible.
''',r'''
links=[]
for i in range(120):
    entity='campaign-device' if 55<=i<80 else ('shared-hub' if i%5==0 else f'private-{i}')
    delay=12 if i%9==0 else 0
    links.append({'application_id':f'app-{i}','entity':entity,'event_at':float(i),'available_at':float(i+delay)})
rows=[]
for link in links:
    t=link['event_at'];entity=link['entity']
    safe=shared_entity_count(links,entity,t,link['application_id'],window=30)
    # Deliberately invalid: future degree from the complete retrospective graph.
    future_degree=len({z['application_id'] for z in links if z['entity']==entity and z['application_id']!=link['application_id']})
    rows.append({'day':int(t),'entity':entity,'causal_count':safe,'invalid_retrospective_degree':future_degree})
graph_data=pd.DataFrame(rows)
display(graph_data[graph_data['entity']=='campaign-device'].head(8))
fig,ax=plt.subplots();subset=graph_data[graph_data['entity']=='campaign-device']
ax.plot(subset['day'],subset['causal_count'],label='Disponible al corte',color=TEAL,marker='o')
ax.plot(subset['day'],subset['invalid_retrospective_degree'],label='Retrospectivo inválido',color=GOLD,linestyle='--')
ax.set(xlabel='Día de solicitud',ylabel='Solicitudes vinculadas',title='La primera solicitud no puede conocer la campaña futura');ax.legend();plt.show()
''','La serie retrospectiva incluye hechos posteriores y una ventana distinta. Se muestra como contraejemplo inválido y nunca alimenta un resultado de desempeño. Las diferencias no prueban por sí solas qué modelo detecta mejor.')
section(c,'2. Hubs legítimos y señales insuficientes',r'''
Un grado alto puede tener varias explicaciones. Una normalización propuesta es $R_v=N_v/\log(2+D_v)$, donde $D_v$ es grado histórico disponible. Atenúa infraestructura compartida, pero también puede atenuar campañas: debe validarse, no presumirse correcta.
''',r'''
summary=graph_data[graph_data['entity'].isin(['shared-hub','campaign-device'])].groupby('entity').agg(solicitudes=('day','size'),conteo_medio=('causal_count','mean'),conteo_maximo=('causal_count','max'))
display(summary)
fig,ax=plt.subplots();
for entity,color in [('shared-hub',BLUE),('campaign-device',TEAL)]:
    subset=graph_data[graph_data['entity']==entity]
    ax.plot(subset['day'],subset['causal_count'],marker='o',label=entity,color=color)
ax.set(xlabel='Día de solicitud',ylabel='Conteo observado en 30 días',title='Infraestructura legítima también crea vínculos');ax.legend();plt.show()
''','El hub se etiqueta legítimo por construcción del ejemplo, no por inferencia del detector. Un solo conteo no distingue intención, titulares ni destino final de fondos. Se requieren fuentes y adjudicación independientes.')
section(c,'3. Eventos tardíos y deduplicación',r'''
La condición $a_i\le t$ se vuelve visible con un enlace antiguo que llega tarde. Una duplicación física de fila no debe duplicar la entidad lógica.
''',r'''
late={'application_id':'late-app','entity':'test-device','event_at':5.,'available_at':20.}
observations=[shared_entity_count([late,late],'test-device',float(t),window=30) for t in [10,19,20,21]]
display(pd.DataFrame({'corte':[10,19,20,21],'solicitudes_distintas':observations}))
future={'application_id':'future','entity':'campaign-device','event_at':200.,'available_at':200.}
before=shared_entity_count(links,'campaign-device',65.,'app-65')
after=shared_entity_count(links+[future],'campaign-device',65.,'app-65')
''','La igualdad al instante de disponibilidad está permitida; la ventana del hecho excluye la solicitud en t. No se afirma que el ejemplo implemente resolución de identidad, GNN ni separación de campañas fuera de muestra.')
end(c,"assert before==after\nassert observations==[0,0,1,1]\nassert graph_data.loc[55,'causal_count']==0\nassert graph_data.loc[55,'invalid_retrospective_degree']>0",
    "{'Primer conteo válido de campaña': int(graph_data.loc[55,'causal_count']), 'Grado retrospectivo inválido': int(graph_data.loc[55,'invalid_retrospective_degree']), 'Invariancia a eventos futuros': bool(before==after)}",
    '1. Construir variables de cuenta destino y dispositivo por separado.\n2. Evaluar campañas nuevas con partición de componentes y fecha.\n3. Medir cuánto cambia la señal al rotar entidades y perder enlaces.\n4. Incorporar confianza del enlace y ambigüedad de resolución antes de una GNN.',
    '- Primitivo local: `shared_entity_count` en el motor.\n- [Duan et al., grafos temporales en fraude transaccional](https://arxiv.org/abs/2402.14708): antecedente; no valida este ejemplo de originación.')
save('02-temporal-application-graphs','01-point-in-time-graph-features.ipynb',c)

# 4. Network overlap.
c=start('Redes: campañas, solapamiento y pérdida prevenible',
        '¿Por qué sumar beneficios individuales puede asignar dos revisiones a la misma pérdida? Derivamos cobertura máxima y contrastamos un MILP contra enumeración exacta.',
        'Tres acciones de investigación cubren conjuntos conocidos en un grafo hipotético. Se supone eficacia uno sobre exposición cubierta y un mismo costo por acción. No se estima que investigar realmente contenga una campaña.')
section(c,'1. Beneficio por unión, no por suma de listas',r'''
Con acción $i$ que cubre $S_i$, el beneficio correcto bajo cobertura perfecta es
$$B(A)=\sum_{j\in\cup_{i\in A}S_i}\ell_j-\sum_{i\in A}c_i.$$

Sumar $\sum_{i\in A}\sum_{j\in S_i}\ell_j$ cuenta pérdidas varias veces si los conjuntos se solapan. Aquí $\ell_j$ es pérdida prevenible esperada, no saldo bruto.
''',r'''
import itertools
from scipy.optimize import milp,Bounds,LinearConstraint
exposure=np.array([60_000.,60_000.,110_000.])
coverage=np.array([[1,1,0],[1,1,0],[0,0,1]])
cost=np.array([5_000.,5_000.,5_000.])
def benefit(indices):
    if not len(indices):return 0.
    covered=coverage[list(indices)].any(axis=0)
    return float(exposure[covered].sum()-cost[list(indices)].sum())
naive_order=np.argsort(-(coverage@exposure-cost),kind='stable')
naive_two=naive_order[:2].tolist()
all_pairs=list(itertools.combinations(range(3),2))
exact_two=max(all_pairs,key=benefit)
display(pd.DataFrame({'acciones':['A+B','A+C','B+C'],'beneficio_union_COP':[benefit(a) for a in all_pairs]}))
fig,ax=plt.subplots();ax.imshow(coverage,cmap='Blues',vmin=0,vmax=1)
ax.set_xticks(range(3),['Exposición 1','Exposición 2','Exposición 3']);ax.set_yticks(range(3),['Acción A','Acción B','Acción C'])
for i in range(3):
    for j in range(3):ax.text(j,i,str(coverage[i,j]),ha='center',va='center',color='white' if coverage[i,j] else '#263238')
ax.set_title('Dos acciones comparten exactamente la misma exposición');plt.show()
''','A y B parecen igualmente atractivas si se suman listas. Sin embargo, revisarlas juntas no alcanza la exposición 3. El ejemplo es una restricción de conjunto conocida, no un resultado empírico de grafos.')
section(c,'2. MILP con variables de cobertura',r'''
Con $x_i$ acción y $z_j$ exposición cubierta:
$$\max\sum_j\ell_jz_j-\sum_i c_ix_i,\quad z_j\le\sum_{i:j\in S_i}x_i,\quad\sum_i x_i\le K.$$

$x,z$ son binarias. Al tener pérdidas no negativas, el objetivo hace que se marque la cobertura disponible. Esta formulación no representa eficacia parcial ni efectos negativos entre acciones.
''',r'''
def coverage_milp(K):
    # Variables [x_A,x_B,x_C,z_1,z_2,z_3]. Negative benefit for minimization.
    objective=np.r_[cost,-exposure]/1000
    rows=[np.r_[np.ones(3),np.zeros(3)]]
    for j in range(3):
        row=np.zeros(6);row[:3]=-coverage[:,j];row[3+j]=1;rows.append(row)
    result=milp(objective,integrality=np.ones(6),bounds=Bounds(np.zeros(6),np.ones(6)),
                constraints=LinearConstraint(np.array(rows),[-np.inf]*4,[K,0,0,0]),options={'mip_rel_gap':0})
    assert result.status==0
    selected=np.flatnonzero(result.x[:3]>.5).tolist()
    return selected,benefit(selected)
frontier=[]
for K in range(4):
    chosen,value=coverage_milp(K)
    oracle=max(benefit(s) for k in range(K+1) for s in itertools.combinations(range(3),k))
    frontier.append({'K':K,'beneficio_MILP_COP':value,'oracle_COP':oracle,'suma_ingenua_realizada_COP':benefit(naive_order[:K].tolist())})
frontier=pd.DataFrame(frontier);display(frontier)
fig,ax=plt.subplots();ax.plot(frontier['K'],frontier['beneficio_MILP_COP']/1000,marker='o',color=TEAL,label='Cobertura conjunta')
ax.plot(frontier['K'],frontier['suma_ingenua_realizada_COP']/1000,marker='s',linestyle='--',color=GOLD,label='Ranking aditivo evaluado por unión')
ax.set(xlabel='Acciones disponibles',ylabel='Beneficio esperado supuesto (miles COP)',title='El solapamiento modifica la asignación');ax.legend();plt.show()
''','La búsqueda exhaustiva da un oráculo independiente en este problema pequeño. La tercera acción no añade exposición cuando las otras ya cubren todo y puede reducir beneficio por su costo. La optimización permite usar menos de K.')
section(c,'3. Eficacia parcial: un supuesto adicional',r'''
Si dos intervenciones tienen eficacia $q$ sobre la misma exposición y sus éxitos fueran independientes, la probabilidad conjunta sería $1-(1-q)^2$, no $2q$. La independencia es un supuesto fuerte: si ambas dependen de la misma verificación podrían no aportar nada adicional.
''',r'''
q=np.array([.2,.5,.8])
display(pd.DataFrame({'q':q,'suma_incorrecta':2*q,'independencia_supuesta':1-(1-q)**2,'dependencia_total':q}))
''','El MILP de arriba usa cobertura perfecta y no implementa esta extensión parcial. No transferir la aparente ganancia de una fórmula de independencia a una campaña real sin conocer cómo actúa la intervención.')
end(c,"assert benefit(exact_two)>benefit(naive_two)\nassert np.allclose(frontier['beneficio_MILP_COP'],frontier['oracle_COP'])\nassert np.all(1-(1-q)**2<=1)",
    "{'Beneficio ranking aditivo con K=2 (COP)': benefit(naive_two), 'Beneficio cobertura conjunta K=2 (COP)': benefit(exact_two), 'Presupuestos contrastados con oráculo': len(frontier)}",
    '1. Modelar cobertura incierta y medir sensibilidad a vínculos falsos.\n2. Estimar el efecto incremental de investigar un segundo caso de una campaña.\n3. Añadir tiempos heterogéneos y retraso hasta contener fondos.\n4. Contrastar cobertura máxima, submodularidad y complementariedad antes de elegir un optimizador.',
    '- [SciPy: programación lineal entera](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html).\n- El contraejemplo de unión se deriva y enumera aquí, sin usar etiquetas de clientes.')
save('02-temporal-application-graphs','02-network-overlap-and-loss-coverage.ipynb',c)

# 5. Income quantiles and conformal calibration.
c=start('Ingresos: cuantiles, bandas y cobertura por segmento',
        '¿Qué rango de ingreso es compatible con una actividad y cuánta incertidumbre conserva? Ajustamos cuantiles, ampliamos bandas con una calibración separada y distinguimos cobertura de detección de fraude.',
        'Ingreso mensual corroborado simulado, en COP. Mezcla de asalariados e independientes con ruido diferente. Entrenamiento, calibración y test son independientes y estacionarios por construcción; no se presupone intercambiabilidad de una cartera real.')
section(c,'1. Pérdida cuantílica y mecanismo generador',r'''
$$\rho_\tau(u)=u(\tau-\mathbf{1}_{u<0}),\quad \hat q_\tau(x)=\arg\min_f\sum_i\rho_\tau(y_i-f(x_i)).$$

Modelamos $y=\log(I)$ con $I>0$ y cuantiles 0,1 y 0,9 para una banda nominal 80%. La población del experimento no contiene ingresos cero; no extrapolar la transformación a ese caso sin un modelo aparte.
''',r'''
from sklearn.ensemble import GradientBoostingRegressor
n=2200
independent=rng.binomial(1,.4,n)
month=rng.integers(0,12,n)
activity=rng.uniform(0,1,n)
x=np.column_stack([activity,independent,np.sin(2*np.pi*month/12),np.cos(2*np.pi*month/12)])
mean=np.log(2_000_000)+.6*activity+.2*independent+.12*np.sin(2*np.pi*month/12)
y=mean+rng.normal(size=n)*(.12+.25*independent)
train,cal,test=np.arange(1000),np.arange(1000,1500),np.arange(1500,2200)
quantiles={tau:GradientBoostingRegressor(loss='quantile',alpha=tau,n_estimators=90,max_depth=2,random_state=21).fit(x[train],y[train]) for tau in [.1,.9]}
def bands(indices):
    a,b=quantiles[.1].predict(x[indices]),quantiles[.9].predict(x[indices])
    return np.minimum(a,b),np.maximum(a,b)
lo_cal,hi_cal=bands(cal);lo,hi=bands(test)
display(pd.DataFrame({'grupo':['asalariado','independiente'],'sigma_log':[.12,.37],'train_n':[(independent[train]==k).sum() for k in [0,1]]}))
''','El generador permite comprobar heterocedasticidad conocida. Ordenar los cuantiles elimina cruces en este ejercicio, pero no garantiza calibración ni aprende un modelo de fraude.')
section(c,'2. Ampliación conformal conservadora',r'''
Sobre la muestra de calibración: $s_i=\max(\hat q_{.1}(x_i)-y_i,y_i-\hat q_{.9}(x_i),0)$.

Sea $k=\lceil(n_{cal}+1)(1-\alpha)\rceil$ y $\hat s=s_{(k)}$. La banda ampliada es $[\hat q_{.1}-\hat s,\hat q_{.9}+\hat s]$. Se usa la variante conservadora con scores no negativos: solo amplía. El rango k debe existir; para niveles extremos se requiere una banda no acotada u otro tratamiento explícito.
''',r'''
alpha=.2
scores=np.maximum.reduce([lo_cal-y[cal],y[cal]-hi_cal,np.zeros(len(cal))])
k=math.ceil((len(cal)+1)*(1-alpha))
assert k<=len(cal)
qhat=np.sort(scores)[k-1]
lo_c,hi_c=lo-qhat,hi+qhat
coverage_raw=((y[test]>=lo)&(y[test]<=hi))
coverage_c=((y[test]>=lo_c)&(y[test]<=hi_c))
coverage_table=[]
for label,mask in [('Todos',np.ones(len(test),bool)),('Asalariados',independent[test]==0),('Independientes',independent[test]==1)]:
    coverage_table.append({'población':label,'n':int(mask.sum()),'cobertura_original':coverage_raw[mask].mean(),'cobertura_ampliada':coverage_c[mask].mean(),'ancho_medio_COP':np.mean(np.exp(hi_c[mask])-np.exp(lo_c[mask]))})
coverage_table=pd.DataFrame(coverage_table);display(coverage_table)
fig,ax=plt.subplots();positions=np.arange(3)
ax.bar(positions-.18,coverage_table['cobertura_original'],width=.36,label='Cuantiles',color=BLUE)
ax.bar(positions+.18,coverage_table['cobertura_ampliada'],width=.36,label='Ampliación',color=TEAL)
ax.axhline(.8,linestyle='--',color='#333333',label='Nominal 80%');ax.set_xticks(positions,coverage_table['población'])
ax.set(ylim=(0,1),ylabel='Cobertura observada (fracción)',title='Cobertura agregada y por grupo: test sintético');ax.legend();plt.show()
''','La garantía marginal de la construcción requiere intercambiabilidad; no promete cobertura en cada segmento. La tabla muestra grupo, tamaño y ancho. Conservar grupos con peor cobertura aunque el agregado esté cerca de 80%.')
section(c,'3. Bandas en moneda y cambio de distribución',r'''
La exponencial es monótona: la banda de log ingreso puede transformarse a COP. Después se desplaza solo el ingreso de prueba en 0,4 log puntos, manteniendo la banda congelada: se viola el mecanismo estacionario de calibración.
''',r'''
order=np.argsort((lo_c+hi_c)/2)[:100]
fig,ax=plt.subplots();axis=np.arange(len(order))
ax.fill_between(axis,np.exp(lo_c[order])/1e6,np.exp(hi_c[order])/1e6,color=TEAL,alpha=.2,label='Banda ampliada 80% nominal')
ax.scatter(axis,np.exp(y[test][order])/1e6,s=12,color=BLUE,label='Ingreso corroborado')
ax.set(xlabel='Primeros 100 casos ordenados por centro de banda',ylabel='Ingreso mensual (millones COP)',title='Bandas predictivas; no intervalos de un promedio');ax.legend();plt.show()
shifted=y[test]+.4
shift_coverage=((shifted>=lo_c)&(shifted<=hi_c)).mean()
display(pd.DataFrame({'escenario':['Estacionario','Desplazamiento +0,4 log'],'cobertura':[coverage_c.mean(),shift_coverage]}))
''','La banda describe un ingreso corroborado hipotético, no la honestidad de una declaración. Una declaración fuera de banda puede motivar aclaración; no confirma fraude. La sensibilidad bajo cambio de distribución conserva un fallo potencial de cobertura.')
end(c,"assert qhat>=0\nassert np.all(lo_c<=hi_c)\nassert coverage_c.mean()>=coverage_raw.mean()\nassert shift_coverage<coverage_c.mean()",
    "{'Cobertura nominal': .8, 'Cobertura test ampliada': round(float(coverage_c.mean()),4), 'Cobertura con cambio de ingreso': round(float(shift_coverage),4), 'Ampliación en log puntos': round(float(qhat),4)}",
    '1. Comparar calibración marginal y por segmento, con tamaños mínimos.\n2. Incorporar ingresos cero mediante un modelo en dos partes.\n3. Tratar períodos faltantes como cobertura de evidencia y no ingreso cero.\n4. Diseñar indicadores de cambio de régimen antes de recalibrar.\n5. Separar discrepancia de ingreso de tergiversación adjudicada.',
    '- [Romano, Patterson y Candès: Conformalized Quantile Regression](https://arxiv.org/abs/1905.03222).\n- [scikit-learn: regresión cuantílica con boosting](https://scikit-learn.org/stable/auto_examples/ensemble/plot_gradient_boosting_quantile.html).')
save('03-income-document-consistency','01-income-quantiles-and-coverage.ipynb',c)

# 6. Income reconciliation and contamination.
c=start('Ingresos: conciliación, periodicidad y contaminación',
        '¿Una entrada de dinero representa ingreso disponible? Construimos un caso contable verificable, probamos conversiones de periodicidad y medimos sensibilidad de la normalización a contaminación.',
        'Un período mensual y una moneda. Las categorías de flujo se conocen por construcción. En producción requieren evidencia, reglas de conciliación y fuentes independientes; no se infiere intención del cliente.')
section(c,'1. Conciliar antes de modelar',r'''
$$I_{mes}=\sum_{j\in\mathrm{ingresos\ elegibles}}F_j,\quad \mathrm{abonos\ brutos}=I_{mes}+\mathrm{traslados}+\mathrm{créditos}+\mathrm{otros}.$$

Una transferencia entre cuentas propias y un desembolso de préstamo no son ingreso laboral. Sumar ambos al ingreso puede crear capacidad de pago ficticia.
''',r'''
flows=pd.DataFrame({'tipo':['salario','traslado propio','préstamo','salario'],
                    'monto_COP':[1_500_000,2_000_000,5_000_000,1_500_000],
                    'elegible_ingreso':[True,False,False,True]})
gross=flows['monto_COP'].sum();eligible=flows.loc[flows['elegible_ingreso'],'monto_COP'].sum()
display(flows)
fig,ax=plt.subplots();ax.bar(['Abonos brutos','Ingreso elegible'],[gross/1e6,eligible/1e6],color=[GOLD,TEAL])
ax.set(ylabel='Millones COP mensuales',title='Conciliar evita convertir financiación en ingreso');plt.show()
''','El ejemplo expone un error de definición y no demuestra fraude. Una categoría mal etiquetada es un problema del contrato de datos antes de ser un problema del clasificador.')
section(c,'2. Periodicidad y pruebas dimensionales',r'''
$$I_{mensual}=I_{anual}/12=2I_{quincenal}=I_{semanal}\,52/12.$$

Quincenal se define aquí como dos pagos al mes, no cada 14 días. En este último caso el factor anualizado sería 26/12. Registrar la convención evita reconciliaciones falsas.
''',r'''
def monthly(amount,period):
    factors={'mensual':1.,'anual':1/12,'quincenal':2.,'semanal':52/12,'cada_14_días':26/12}
    if period not in factors or not np.isfinite(amount) or amount<0:raise ValueError('Monto/período inválido')
    return amount*factors[period]
conversions=pd.DataFrame({'periodo':['mensual','anual','quincenal','semanal','cada_14_días'],
                          'monto_COP':[3_000_000,36_000_000,1_500_000,3_000_000*12/52,3_000_000*12/26]})
conversions['mensual_COP']=[monthly(a,p) for a,p in zip(conversions['monto_COP'],conversions['periodo'])]
display(conversions)
''','El redondeo debe aplicarse al presentar o según contrato, no antes de toda conversión. El mismo flujo observado no debe sumarse dos veces por estar en dos cuentas o dos extracciones.')
section(c,'3. Media y escala robusta ante contaminación',r'''
Para evidencia comparable de log ingreso, $z_{rob}=(x-\mathrm{mediana})/(1,4826\,MAD)$ y $MAD=\mathrm{mediana}|x-\mathrm{mediana}|$.

El factor 1,4826 aproxima la desviación normal cuando el supuesto es apropiado. La robustez de una estadística no verifica autenticidad de documentos ni justifica un umbral universal.
''',r'''
clean=rng.normal(np.log(3_000_000),.18,1000)
legitimate_test=rng.normal(np.log(3_000_000),.18,800)
shifted_test=rng.normal(np.log(3_000_000)+.6,.18,200)
records=[]
for contamination in [0,.05,.1,.2,.35]:
    mixed=clean.copy();count=int(contamination*len(mixed))
    mixed[:count]+=2.
    mean,sd=mixed.mean(),mixed.std(ddof=1)
    median=np.median(mixed);scale=1.4826*np.median(np.abs(mixed-median))
    for method,center,spread in [('media/desviación',mean,sd),('mediana/MAD',median,scale)]:
        # Threshold fixed before evaluation. Shifted examples are discrepancies,
        # not adjudicated fraud; 'detection' means a synthetic numeric shift.
        records.append({'contaminacion':contamination,'metodo':method,
                        'alarma_legitimos':np.mean((legitimate_test-center)/spread>3),
                        'deteccion_desplazamiento':np.mean((shifted_test-center)/spread>3),
                        'centro_log':center,'escala_log':spread})
robustness=pd.DataFrame(records);display(robustness.round(4))
fig,ax=plt.subplots()
for method,color in [('media/desviación',GOLD),('mediana/MAD',TEAL)]:
    subset=robustness[robustness['metodo']==method]
    ax.plot(subset['contaminacion'],subset['deteccion_desplazamiento'],marker='o',label=method,color=color)
ax.set(xlabel='Fracción contaminada en referencia',ylabel='Fracción de desplazamientos señalados',ylim=(0,1),title='Contaminación de referencia y señal numérica sintética');ax.legend();plt.show()
''','La curva evalúa un desplazamiento numérico, no fraude. El MAD también cambia con contaminación alta y con mezclas de actividades; segmentar y validar sigue siendo necesario. En caso de escala cero o población escasa se debe abstener o usar un fallback documentado.')
end(c,"assert gross==10_000_000 and eligible==3_000_000\nassert np.allclose(conversions['mensual_COP'],3_000_000)\nassert np.isfinite(robustness.select_dtypes('number')).all().all()",
    "{'Abonos brutos (COP)': int(gross), 'Ingreso elegible (COP)': int(eligible), 'Sobreestimación por sumar abonos': round(float(gross/eligible),3), 'Conversiones reconciliadas': len(conversions)}",
    '1. Añadir trazabilidad entre cuenta origen y destino para deduplicar traslados.\n2. Conciliar ingreso bruto, neto y ventas de negocio por separado.\n3. Repetir el experimento con grupos multimodales y escalas casi cero.\n4. Cuantificar efecto de ruido OCR sin llamar fraude a un error de extracción.\n5. Evaluar el costo de pedir soportes adicionales frente a la información que aportan.',
    'Derivaciones y flujos sintéticos construidos dentro del notebook. Las conversiones declaran su convención; las categorías de flujo no proceden de clientes. Modelo de referencia del proyecto: `../README.md`.')
save('03-income-document-consistency','02-flow-reconciliation-and-robustness.ipynb',c)

# 7. Process mixture adjustment.
c=start('Originación: mezcla de cartera, tasas y contracción',
        '¿Un canal tiene más omisiones o simplemente atiende una población distinta? Comparamos tasas brutas, esperadas según mezcla y contracción hacia una referencia conocida.',
        'Eventos de omisión de control simulados en 80 grupos, no etiquetas de fraude. Dos productos con tasas base diferentes. Las probabilidades de referencia son conocidas por el simulador y no se estiman con el mismo resultado a evaluar.')
section(c,'1. El denominador y la mezcla cambian la tasa',r'''
$$E_g=\sum_i p_{ig}^{ref},\quad O_g=\sum_i y_{ig},\quad z_g=\frac{O_g-E_g}{\sqrt{\sum_i p_{ig}^{ref}(1-p_{ig}^{ref})}}.$$

La varianza supone independencia condicional. En lotes dependientes o sobredispersión puede subestimar incertidumbre; no se usa como prueba universal de fraude.
''',r'''
groups=80
volumes=rng.integers(8,300,groups)
mixture=rng.beta(1.5,1.5,groups)
anomalous=np.zeros(groups,dtype=bool);anomalous[[7,18,33,52]]=True
records=[]
for g in range(groups):
    high=rng.binomial(1,mixture[g],volumes[g])
    reference=np.where(high==1,.15,.025)
    actual=np.minimum(1,reference+.13*anomalous[g])
    observed=rng.binomial(1,actual).sum()
    expected=reference.sum();variance=np.sum(reference*(1-reference))
    records.append({'grupo':g,'n':volumes[g],'mezcla_alta':high.mean(),'O':observed,'E':expected,
                    'tasa_bruta':observed/volumes[g],'tasa_esperada':expected/volumes[g],
                    'z':(observed-expected)/np.sqrt(variance),'anomalia_simulada':anomalous[g]})
process=pd.DataFrame(records)
display(process.sort_values('tasa_bruta',ascending=False).head(8))
fig,ax=plt.subplots()
for flag,color,label in [(False,BLUE,'Sin incremento artificial'),(True,GOLD,'Incremento artificial')]:
    subset=process[process['anomalia_simulada']==flag]
    ax.scatter(subset['tasa_esperada'],subset['tasa_bruta'],color=color,label=label,s=30)
ax.plot([0,.25],[0,.25],color='#444444',linestyle='--')
ax.set(xlabel='Tasa esperada por mezcla',ylabel='Tasa observada de omisión',title='Las tasas brutas comparan poblaciones diferentes');ax.legend();plt.show()
''','Las cuatro anomalías se inyectan por construcción. Un punto sobre la diagonal puede aparecer por azar, una política nueva o un problema de registro. El gráfico compara un evento de control, no prueba intención ni fraude.')
section(c,'2. Contracción explícita de grupos pequeños',r'''
Con una referencia $p_g^{ref}=E_g/n_g$ y fuerza previa $\tau$, una media regularizada es
$$\tilde p_g=\frac{O_g+\tau p_g^{ref}}{n_g+\tau}.$$

Aquí es una regla de contracción motivada por beta-binomial. No es un modelo jerárquico completo: ni $\tau$ ni la referencia se estiman de forma bayesiana en este notebook.
''',r'''
tau=40.
process['tasa_contraida']=(process['O']+tau*process['tasa_esperada'])/(process['n']+tau)
process['exceso_contraido']=process['tasa_contraida']-process['tasa_esperada']
ranked=process.sort_values('z',ascending=False).head(10)
display(ranked[['grupo','n','tasa_bruta','tasa_esperada','tasa_contraida','z','anomalia_simulada']])
fig,ax=plt.subplots();ax.barh(ranked['grupo'].astype(str),ranked['z'],color=TEAL)
ax.invert_yaxis();ax.set(xlabel='Residuo ajustado por mezcla',ylabel='Grupo sintético',title='Diez grupos con mayor residuo; sin umbral de culpabilidad');plt.show()
''','El ranking ofrece una prioridad de investigación, no significancia corregida por probar 80 grupos. Una contracción fuerte puede ocultar cambios reales en grupos pequeños; debe contrastarse con demora y carga de casos.')
section(c,'3. Sensibilidad a la fuerza de la referencia',r'''
Para $\tau\to0$ se recupera la tasa bruta; para $\tau\to\infty$ la referencia domina. Contar anomalías inyectadas entre los primeros K sirve como diagnóstico del simulador, no como recall de fraude real.
''',r'''
comparison=[]
K=8
for score in ['tasa_bruta','z','exceso_contraido']:
    selected=process.nlargest(K,score)
    comparison.append({'criterio':score,'K':K,'cambios_inyectados_en_K':int(selected['anomalia_simulada'].sum()),'volumen_medio':selected['n'].mean()})
display(pd.DataFrame(comparison))
small=process.nsmallest(1,'n').iloc[0]
tau_table=pd.DataFrame({'tau':[0,10,40,100,1000]})
tau_table['tasa_contraida']=(small['O']+tau_table['tau']*small['tasa_esperada'])/(small['n']+tau_table['tau'])
display(tau_table)
''','No elegimos tau con el conteo de anomalías de este test. Una extensión debe separar entrenamiento y validación, estimar la mezcla sin fuga y considerar correlación dentro del canal y a través del tiempo.')
end(c,"assert ((process['tasa_contraida']>=process[['tasa_bruta','tasa_esperada']].min(axis=1)-1e-12)&(process['tasa_contraida']<=process[['tasa_bruta','tasa_esperada']].max(axis=1)+1e-12)).all()\nassert process['n'].min()>0\nassert np.isfinite(process['z']).all()",
    "{'Grupos simulados': groups, 'Cambios inyectados': int(anomalous.sum()), 'Grupos revisados por criterio': K, 'Mayor residuo ajustado': round(float(process['z'].max()),3)}",
    '1. Estimar tasas base por producto en una ventana histórica cerrada.\n2. Ajustar sobredispersión y dependencia por lotes antes de usar p-valores.\n3. Comparar contracción con modelo jerárquico de efectos de grupo.\n4. Incluir versión de política y cambios de logging como explicaciones alternativas.\n5. Diseñar un presupuesto de alertas y criterios de escalamiento, no acusaciones automáticas.',
    'La referencia y las anomalías se conocen solo por construcción del simulador. La contracción es una identidad algebraica explícita; no se presenta como un modelo bayesiano estimado. Proyecto: `../README.md`.')
save('04-origination-process-anomalies','01-case-mix-and-shrinkage.ipynb',c)

# 8. CUSUM calibration and attribution.
c=start('Originación: CUSUM, falsas alarmas y demora',
        '¿Qué umbral detecta un cambio sin alertar constantemente? Calibramos el máximo de CUSUM en horizontes de 120 días y evaluamos falsas alarmas en réplicas independientes.',
        'Residuos diarios normales e independientes bajo estabilidad. Se simula un cambio después del día 60. El límite se calibra para una sola serie y un solo horizonte; no controla automáticamente muchos canales ni monitoreo indefinido.')
section(c,'1. Acumular evidencia de un cambio',r'''
$$S_t=\max(0,S_{t-1}+z_t-k),\quad \mathrm{alarma}\iff S_t>h.$$

$k$ penaliza pequeñas oscilaciones y $h$ fija tolerancia de evidencia. Un umbral no puede copiarse sin considerar escala, dependencia, número de series y horizonte.
''',r'''
def cusum(z,k=.5):
    result=np.zeros_like(z,dtype=float);state=0.
    for t,value in enumerate(z):
        state=max(0.,state+value-k);result[t]=state
    return result
horizon=120;change_day=60
calibration_paths=rng.normal(size=(600,horizon))
maxima=np.array([cusum(path).max() for path in calibration_paths])
h=float(np.quantile(maxima,.95,method='higher'))
validation_paths=rng.normal(size=(600,horizon))
false_alarm=np.array([cusum(path).max()>h for path in validation_paths])
false_alarm_rate=float(false_alarm.mean())
def wilson(success,n,z=1.96):
    p=success/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den
    radius=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return center-radius,center+radius
ci=wilson(int(false_alarm.sum()),len(false_alarm))
display(pd.DataFrame({'umbral_h':[h],'FA_horizonte_test':[false_alarm_rate],'limite95_inferior':[ci[0]],'limite95_superior':[ci[1]],'replicas':[len(false_alarm)]}))
''','El intervalo Wilson corresponde a la tasa de réplicas con al menos una alarma en 120 días. No es la tasa diaria ni un intervalo del umbral. Las simulaciones de calibración y validación son diferentes.')
section(c,'2. Cambio y causa no son lo mismo',r'''
Una subida en omisiones observadas puede provenir de un cambio de proceso o de un cambio en registro. Si producen la misma serie $z_t$, CUSUM devuelve exactamente la misma evidencia: no identifica causalidad ni intención.
''',r'''
noise=rng.normal(size=horizon)
stable=noise.copy();deviation=noise.copy();deviation[change_day:]+=1.3
logging=deviation.copy()
fig,ax=plt.subplots()
ax.plot(cusum(stable),label='Sin cambio',color=BLUE)
ax.plot(cusum(deviation),label='Cambio de proceso',color=TEAL)
ax.plot(cusum(logging),label='Cambio de logging: misma serie',color=GOLD,linestyle='--')
ax.axhline(h,color='#333333',linestyle=':',label='Umbral calibrado')
ax.axvline(change_day,color='#777777',linestyle='--');ax.set(xlabel='Día desde inicio',ylabel='CUSUM unilateral',title='Detectar un desvío no identifica su causa');ax.legend(fontsize=9);plt.show()
''','Las dos curvas de cambio coinciden deliberadamente. La explicación necesita bitácora de versión, conciliación de eventos y verificación independiente. El detector estadístico por sí solo no demuestra fraude.')
section(c,'3. Tamaño de cambio y tiempo de detección',r'''
La primera alarma puede llegar antes del cambio. Se reporta por separado la tasa pre-cambio y la detección dentro del horizonte entre trayectorias sin alarma previa. La mediana de demora usa solo trayectorias detectadas; omite censuradas y se etiqueta así.
''',r'''
records=[]
for shift in [.3,.6,1.,1.5,2.]:
    paths=rng.normal(size=(400,horizon));paths[:,change_day:]+=shift
    pre_count=0;eligible=0;delays=[]
    for path in paths:
        series=cusum(path);alarms=np.flatnonzero(series>h)
        if len(alarms) and alarms[0]<change_day:pre_count+=1;continue
        eligible+=1
        later=alarms[alarms>=change_day]
        if len(later):delays.append(int(later[0]-change_day+1))
    records.append({'shift':shift,'replicas':400,'prealarma':pre_count/400,'elegibles_sin_prealarma':eligible,
                    'deteccion_en_elegibles':len(delays)/eligible,'detectados':len(delays),
                    'mediana_dias_solo_detectados':float(np.median(delays)) if delays else np.nan})
detection=pd.DataFrame(records);display(detection)
fig,ax=plt.subplots();ax.plot(detection['shift'],detection['deteccion_en_elegibles'],color=TEAL,marker='o')
ax.set(xlabel='Cambio en desviaciones estándar',ylabel='Fracción detectada antes de día 120',ylim=(0,1.02),title='Detección entre trayectorias sin alarma previa');plt.show()
''','La comparación mantiene h y k congelados y varía solo la simulación de cambio. La tasa pre-cambio y los casos censurados se conservan en la tabla; no se presenta la mediana de detectados como demora poblacional.')
end(c,"assert np.array_equal(cusum(deviation),cusum(logging))\nassert 0<=false_alarm_rate<=1\nassert ((detection['detectados']<=detection['elegibles_sin_prealarma'])&(detection['elegibles_sin_prealarma']>0)).all()\nassert ci[0]<=false_alarm_rate<=ci[1]",
    "{'Umbral calibrado': round(h,3), 'Falsa alarma en 120 días': round(false_alarm_rate,4), 'Réplicas independientes de evaluación': len(false_alarm), 'Escenarios de cambio': len(detection)}",
    '1. Introducir residuos autocorrelacionados para probar cuándo se pierde la calibración.\n2. Calibrar máximos conjuntos de varios canales, en vez de copiar el umbral de una serie.\n3. Comparar reinicios y períodos de espera después de investigar una alarma.\n4. Modelar señales de logging y calidad en un canal separado.\n5. Incorporar el costo de demora y la capacidad de revisión a la selección de umbral.',
    '- [NIST: CUSUM](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm).\n- [NIST: average run length](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc3131.htm).\nEste notebook evalúa probabilidad de alarma a horizonte fijo, no estima ARL infinito.')
save('04-origination-process-anomalies','02-cusum-false-alarms-and-delay.ipynb',c)
from deepen_notebooks import deepen_all
deepen_all()
print('Authored and deepened eight notebooks')
