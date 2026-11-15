"""Backtest mensual expansivo con corte de información hipotético de dos meses."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from threadpoolctl import threadpool_limits
from data import ROOT, load

RESULTS=ROOT/'results'; FIG=ROOT/'reports'/'figures'

def features(raw):
    out=pd.DataFrame(index=raw.index)
    out['real']=raw.icv_pp
    for k in [2,3,4,6,12,14]: out[f'icv_lag_{k}']=raw.icv_pp.shift(k)
    for seg in ['comercial','consumo','vivienda','microcredito']:
        out[f'{seg}_lag_2']=raw[f'icv_{seg}_pp'].shift(2)
    out['trm_lag_2']=raw.trm_cierre_cop_usd.shift(2)
    out['trm_var_anual_lag_2']=raw.trm_cierre_cop_usd.shift(2)/raw.trm_cierre_cop_usd.shift(14)-1
    out['cartera_crecimiento_anual_lag_2']=raw.bruto.shift(2)/raw.bruto.shift(14)-1
    out['mes_sin']=np.sin(2*np.pi*out.index.month/12)
    out['mes_cos']=np.cos(2*np.pi*out.index.month/12)
    return out.dropna()

FEATS=['icv_lag_2','icv_lag_3','icv_lag_4','icv_lag_6','icv_lag_12','icv_lag_14','comercial_lag_2','consumo_lag_2','vivienda_lag_2','microcredito_lag_2','trm_lag_2','trm_var_anual_lag_2','cartera_crecimiento_anual_lag_2','mes_sin','mes_cos']
MODELS=['persistencia','tendencia','ridge','boosting']

def forecast(train,row,model):
    if model=='persistencia': return float(row.icv_lag_2)
    if model=='tendencia': return float(row.icv_lag_2+(row.icv_lag_2-row.icv_lag_3))
    # Se aprende el cambio frente al dato de referencia para limitar extrapolación de nivel.
    y=train.real-train.icv_lag_2
    if model=='ridge': estimator=make_pipeline(StandardScaler(),Ridge(alpha=20))
    elif model=='boosting': estimator=HistGradientBoostingRegressor(max_iter=120,max_leaf_nodes=7,min_samples_leaf=12,learning_rate=.04,l2_regularization=5,early_stopping=False,random_state=17)
    else: raise ValueError(model)
    with threadpool_limits(limits=1):
        estimator.fit(train[FEATS],y)
        pred=float(estimator.predict(row[FEATS].to_frame().T)[0])
    return float(row.icv_lag_2+pred)

def backtest(df):
    output=[]
    for target in df.index[df.index>='2020-01-31']:
        # Solamente etiquetas hasta t-2 podrían estar disponibles al final de t-1.
        cutoff=target-pd.offsets.MonthEnd(2)
        train=df.loc[df.index<=cutoff]
        if len(train)<24: raise ValueError('Historia insuficiente')
        for name in MODELS:
            row=df.loc[target]
            output.append({'fecha':target,'modelo':name,'real_pp':row.real,'pred_pp':forecast(train,row,name),'train_max':cutoff,'n_train':len(train),'periodo':'desarrollo' if target.year<=2022 else 'evaluacion'})
    return pd.DataFrame(output)

def summarise(pred):
    records=[]
    for (period,model),g in pred.groupby(['periodo','modelo']):
        e=g.pred_pp-g.real_pp
        records.append({'periodo':period,'modelo':model,'n':len(g),'mae_pp':mean_absolute_error(g.real_pp,g.pred_pp),'rmse_pp':np.sqrt(mean_squared_error(g.real_pp,g.pred_pp)),'sesgo_pp':e.mean(),'max_abs_pp':e.abs().max()})
    return pd.DataFrame(records)

def plots(raw,pred,table,choice):
    FIG.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'figure.dpi':150,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10,4.8))
    for col,label in [('icv_pp','Total'),('icv_comercial_pp','Comercial'),('icv_consumo_pp','Consumo'),('icv_vivienda_pp','Vivienda'),('icv_microcredito_pp','Microcrédito')]: ax.plot(raw.index,raw[col],label=label,lw=1.4)
    ax.set(title='Cartera vencida / cartera bruta por modalidad',ylabel='% del saldo bruto',xlabel='Mes de corte'); ax.legend(ncol=3,frameon=False); ax.grid(alpha=.15); fig.tight_layout(); fig.savefig(FIG/'01_calidad_cartera.png'); plt.close(fig)
    p=pred[(pred.periodo=='evaluacion')&(pred.modelo==choice)].copy()
    fig,ax=plt.subplots(figsize=(10,4.5)); ax.plot(p.fecha,p.real_pp,label='Observado',color='#24364b');ax.plot(p.fecha,p.pred_pp,label=f'Pronóstico: {choice}',color='#007e81');ax.fill_between(p.fecha,p.inferior,p.superior,color='#007e81',alpha=.14,label='Banda empírica: objetivo 90 %')
    ax.set(title='Evaluación retrospectiva · cartera total',ylabel='Vencida / bruta (%)',xlabel='Mes');ax.grid(alpha=.15);ax.legend(frameon=False);fig.tight_layout();fig.savefig(FIG/'02_evaluacion.png');plt.close(fig)
    ev=table[table.periodo=='evaluacion'].set_index('modelo').loc[MODELS]
    fig,ax=plt.subplots(figsize=(8,4)); bars=ax.barh(ev.index,ev.mae_pp,color=['#aeb9bf','#74899a','#007e81','#c07b55']);ax.bar_label(bars,fmt='%.3f',padding=3);ax.set(xlabel='MAE · puntos porcentuales',title='Errores del periodo de evaluación');ax.set_xlim(0,ev.mae_pp.max()*1.25);ax.invert_yaxis();fig.tight_layout();fig.savefig(FIG/'03_modelos.png');plt.close(fig)
    fig,axes=plt.subplots(2,1,figsize=(10,6),sharex=True);axes[0].plot(raw.index,raw.trm_cierre_cop_usd,color='#4c7282');axes[0].set(ylabel='COP por USD',title='Contexto económico y composición de cartera'); axes[1].plot(raw.index,raw.bruto/1e6,color='#bf754e');axes[1].set(ylabel='Bruta · billones COP',xlabel='Mes de corte');[a.grid(alpha=.15) for a in axes];fig.tight_layout();fig.savefig(FIG/'04_contexto.png');plt.close(fig)

def main():
    raw=load(); df=features(raw)
    RESULTS.mkdir(parents=True,exist_ok=True);(ROOT/'data/processed').mkdir(parents=True,exist_ok=True)
    raw.to_csv(ROOT/'data/processed/serie_mensual.csv',index_label='fecha',float_format='%.10f')
    pred=backtest(df); table=summarise(pred)
    dev=table[table.periodo=='desarrollo'].set_index('modelo')
    choice=dev.mae_pp.idxmin()
    cal=pred[(pred.periodo=='desarrollo')&(pred.modelo==choice)]
    errors=np.sort(np.abs(cal.real_pp-cal.pred_pp).to_numpy())
    rank=min(int(np.ceil((len(errors)+1)*.9)),len(errors))-1
    radius=float(errors[rank]); pred['inferior']=pred.pred_pp-radius; pred['superior']=pred.pred_pp+radius
    test=pred[(pred.periodo=='evaluacion')&(pred.modelo==choice)]
    coverage=float(((test.real_pp>=test.inferior)&(test.real_pp<=test.superior)).mean())
    summary={'fecha_min':str(raw.index.min().date()),'fecha_max':str(raw.index.max().date()),'meses':len(raw),'cobertura':'Establecimientos de crédito sin IOE; valores agregados SFC','max_conciliacion_indicador':raw.attrs['max_ratio_difference'],'seleccion':choice,'criterio':'menor MAE 2020-2022','evaluacion':'2023-01 hasta último mes; entrenamiento expansivo y corte t-2','banda_radio_pp':radius,'banda_cobertura_evaluacion':coverage,'nota_intervalo':'residuos de desarrollo; sin garantía por dependencia temporal, selección y cambios de distribución'}
    pred.to_csv(RESULTS/'predicciones.csv',index=False,float_format='%.8f');table.to_csv(RESULTS/'metricas.csv',index=False,float_format='%.8f');(RESULTS/'resumen.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    plots(raw,pred,table,choice)
    print(table.to_string(index=False));print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
