"""Challengers con inflación rezagada: comparación exploratoria, sin reselección."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from data import ROOT,load
from model import features,FEATS,summarise
from contexto_economico import check,read_ipc

def make_features(raw,ipc):
    df=features(raw)
    # El IPC original se desplaza dos meses con índice mensual continuo.
    series=ipc.set_index('fecha').reindex(raw.index)
    df['inflacion_12m_lag2']=series.inflacion_12m_pct.shift(2).reindex(df.index)
    return df.dropna()

def run():
    check(); raw=load(); df=make_features(raw,read_ipc(ROOT/'data/territorial/raw/ipc_dane_oct2026.xlsx'))
    cols=FEATS+['inflacion_12m_lag2']; rows=[]
    for t in df.index[df.index>='2020-01-31']:
        train=df.loc[:t-pd.offsets.MonthEnd(2)]; row=df.loc[t]
        if len(train)<24: raise ValueError('Historia insuficiente')
        for name in ['ridge_ipc','boosting_ipc']:
            estimator=make_pipeline(StandardScaler(),Ridge(alpha=20)) if name=='ridge_ipc' else HistGradientBoostingRegressor(max_iter=120,max_leaf_nodes=7,min_samples_leaf=12,learning_rate=.04,l2_regularization=5,early_stopping=False,random_state=17)
            with threadpool_limits(limits=1):
                estimator.fit(train[cols],train.real-train.icv_lag_2)
                pred=float(row.icv_lag_2+estimator.predict(row[cols].to_frame().T)[0])
            rows.append({'fecha':t,'modelo':name,'periodo':'desarrollo' if t.year<=2022 else 'evaluacion','real_pp':row.real,'pred_pp':pred})
    predictions=pd.DataFrame(rows)
    predictions.to_csv(ROOT/'results/predicciones_ipc.csv',index=False,float_format='%.8f')
    metrics=summarise(predictions); metrics.to_csv(ROOT/'results/metricas_ipc.csv',index=False,float_format='%.8f')
    base=pd.read_csv(ROOT/'results/predicciones.csv',parse_dates=['fecha'])
    for period in ['desarrollo','evaluacion']:
        baseline=base[(base.periodo==period)&(base.modelo=='persistencia')].sort_values('fecha')
        challenger=predictions[(predictions.periodo==period)&(predictions.modelo=='boosting_ipc')].sort_values('fecha')
        if not baseline.fecha.reset_index(drop=True).equals(challenger.fecha.reset_index(drop=True)) or not np.allclose(baseline.real_pp,challenger.real_pp,atol=1e-7):
            raise ValueError('Los modelos no comparten fechas y observaciones')
    table=pd.concat([summarise(base),metrics],ignore_index=True)
    eval_=table[table.periodo=='evaluacion'].set_index('modelo').loc[['persistencia','boosting','boosting_ipc','ridge_ipc']]
    plt.rcParams.update({'font.size':10,'figure.dpi':150,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(8,4));bars=ax.barh(['Persistencia seleccionada','Boosting original','Boosting + IPC','Ridge + IPC'],eval_.mae_pp,color=['#768b98','#007e81','#b66e4d','#b66e4d']);ax.bar_label(bars,fmt='%.3f',padding=3);ax.set(xlabel='MAE · puntos porcentuales',title='Comparación exploratoria en 2023–2026');ax.set_xlim(0,eval_.mae_pp.max()*1.25);ax.invert_yaxis();fig.tight_layout();fig.savefig(ROOT/'reports/figures/11_modelos_ipc.png');plt.close(fig)
    print(metrics.to_string(index=False))

if __name__=='__main__':run()
