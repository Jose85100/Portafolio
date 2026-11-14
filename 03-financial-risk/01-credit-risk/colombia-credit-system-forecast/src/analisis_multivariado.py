"""PCA, análisis factorial y regímenes descriptivos; ajuste solo en 2017–2022."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.metrics import silhouette_score
from sklearn.metrics import adjusted_rand_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from data import ROOT, load
from contexto_economico import check, read_ipc

OUT=ROOT/'results/multivariado'; FIG=ROOT/'reports/figures'
COLS=['mora_comercial_pp','mora_consumo_pp','mora_vivienda_pp','mora_microcredito_pp','crecimiento_real_cartera_pct','inflacion_anual_pct','variacion_trm_anual_pct']

def build_features(raw,ipc):
    """Variables contemporáneas descriptivas, sin interpretación de disponibilidad histórica."""
    d=pd.DataFrame(index=raw.index)
    for seg in ['comercial','consumo','vivienda','microcredito']:
        d[f'mora_{seg}_pp']=raw[f'icv_{seg}_pp']
    index=ipc.set_index('fecha').reindex(raw.index)['ipc']
    if index.isna().any() or (index<=0).any(): raise ValueError('IPC incompleto para la ventana financiera')
    d['crecimiento_real_cartera_pct']=100*((raw.bruto/raw.bruto.shift(12))/(index/index.shift(12))-1)
    d['inflacion_anual_pct']=100*(index/index.shift(12)-1)
    d['variacion_trm_anual_pct']=100*(raw.trm_cierre_cop_usd/raw.trm_cierre_cop_usd.shift(12)-1)
    if d.index.has_duplicates or not np.isfinite(d.dropna().to_numpy()).all(): raise ValueError('Variables inválidas')
    return d.dropna()

def fit_analysis(data):
    train=data.loc[:'2022-12-31']; test=data.loc['2023-01-01':]
    if len(train)<48 or len(test)<24: raise ValueError('Historia insuficiente')
    scaler=StandardScaler().fit(train[COLS]); ztrain=scaler.transform(train[COLS]); ztest=scaler.transform(test[COLS]); zall=scaler.transform(data[COLS])
    pca=PCA().fit(ztrain)
    # Fijamos dos factores para interpretabilidad; no se afirma un número verdadero de factores.
    fa=FactorAnalysis(n_components=2,rotation='varimax',max_iter=1000,random_state=17).fit(ztrain)
    scores=[]; fitted={}
    with threadpool_limits(limits=1):
        for k in [2,3,4,5]:
            model=KMeans(n_clusters=k,n_init=30,random_state=17).fit(ztrain)
            fitted[k]=model
            scores.append({'k':k,'silhouette_desarrollo':float(silhouette_score(ztrain,model.labels_)),'inercia':float(model.inertia_)})
        best=max(scores,key=lambda x:x['silhouette_desarrollo'])['k']
        cluster=fitted[best]; labels=cluster.predict(zall)
        gmm=GaussianMixture(n_components=best,covariance_type='diag',reg_covar=1e-4,n_init=10,random_state=17).fit(ztrain)
    return train,test,scaler,pca,fa,cluster,labels,pd.DataFrame(scores),ztrain,ztest,zall,gmm

def plot_outputs(data,pca,fa,labels,train,diagnostics):
    plt.rcParams.update({'font.size':9,'figure.dpi':150,'axes.spines.top':False,'axes.spines.right':False})
    corr=train[COLS].corr(); fig,ax=plt.subplots(figsize=(8,7)); im=ax.imshow(corr,vmin=-1,vmax=1,cmap='RdBu_r')
    ax.set_xticks(range(len(COLS)),COLS,rotation=55,ha='right');ax.set_yticks(range(len(COLS)),COLS)
    for i in range(len(COLS)):
        for j in range(len(COLS)): ax.text(j,i,f'{corr.iloc[i,j]:.2f}',ha='center',va='center',fontsize=7,color='white' if abs(corr.iloc[i,j])>.55 else 'black')
    ax.set_title('Correlación de Pearson · desarrollo 2017–2022');fig.colorbar(im,ax=ax,shrink=.8);fig.tight_layout();fig.savefig(FIG/'12_correlaciones.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4));x=np.arange(1,len(COLS)+1); ax.bar(x,pca.explained_variance_ratio_*100,color='#007e81');ax.plot(x,np.cumsum(pca.explained_variance_ratio_)*100,marker='o',color='#b66e4d',label='Acumulada');ax.set(xticks=x,xlabel='Componente',ylabel='% de varianza estandarizada',title='PCA · ajuste en desarrollo');ax.legend(frameon=False);fig.tight_layout();fig.savefig(FIG/'13_pca_varianza.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,3.5)); ax.scatter(data.index,labels+1,c=labels,cmap='tab10',s=25);ax.axvline(pd.Timestamp('2023-01-01'),color='#555',ls='--',label='Inicio periodo posterior');ax.set(yticks=np.arange(max(labels)+1)+1,ylabel='Grupo descriptivo',xlabel='Mes',title='Agrupaciones mensuales · sin etiquetas de riesgo');ax.legend(frameon=False);ax.grid(alpha=.15);fig.tight_layout();fig.savefig(FIG/'14_grupos_tiempo.png');plt.close(fig)
    loadings=pd.DataFrame(fa.components_.T,index=COLS,columns=['Factor 1','Factor 2']);fig,ax=plt.subplots(figsize=(8,5)); im=ax.imshow(loadings,vmin=-1,vmax=1,cmap='RdBu_r',aspect='auto');ax.set_yticks(range(len(COLS)),COLS);ax.set_xticks([0,1],loadings.columns)
    for i in range(len(COLS)):
        for j in range(2): ax.text(j,i,f'{loadings.iloc[i,j]:.2f}',ha='center',va='center',color='white' if abs(loadings.iloc[i,j])>.55 else 'black')
    ax.set_title('Cargas factoriales rotadas · desarrollo');fig.colorbar(im,ax=ax,shrink=.8);fig.tight_layout();fig.savefig(FIG/'15_factores.png');plt.close(fig)

def main():
    check();raw=load();ipc=read_ipc(ROOT/'data/territorial/raw/ipc_dane_oct2026.xlsx');d=build_features(raw,ipc)
    train,test,scaler,pca,fa,cluster,labels,sil,ztrain,ztest,zall,gmm=fit_analysis(d)
    OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
    ratio=pca.explained_variance_ratio_
    pcaload=pd.DataFrame(pca.components_.T*np.sqrt(pca.explained_variance_),index=COLS,columns=[f'PC{i+1}' for i in range(len(COLS))]);pcaload.to_csv(OUT/'pca_cargas.csv',index_label='variable')
    faload=pd.DataFrame(fa.components_.T,index=COLS,columns=['factor_1','factor_2']);faload['varianza_especifica']=fa.noise_variance_;faload.to_csv(OUT/'factor_cargas.csv',index_label='variable')
    coords=pca.transform(zall); scores=d.copy(); scores['grupo']=labels+1;scores['grupo_gmm']=gmm.predict(zall)+1;scores['probabilidad_mayor_grupo_gmm']=gmm.predict_proba(zall).max(axis=1);scores['PC1']=coords[:,0];scores['PC2']=coords[:,1];scores['periodo']=np.where(scores.index.year<=2022,'desarrollo','posterior')
    profiles=scores.groupby(['periodo','grupo'])[COLS].mean();profiles.to_csv(OUT/'perfiles_grupo.csv')
    sil.to_csv(OUT/'seleccion_grupos.csv',index=False)
    corr_train=train[COLS].corr();corr_test=test[COLS].corr();corr_train.to_csv(OUT/'correlacion_desarrollo.csv');corr_test.to_csv(OUT/'correlacion_posterior.csv')
    distances=cluster.transform(ztest).min(axis=1);training_distances=cluster.transform(ztrain).min(axis=1);threshold=float(np.quantile(training_distances,.95))
    scores['distancia_centro']=cluster.transform(zall).min(axis=1);scores['supera_p95_desarrollo']=scores.distancia_centro>threshold;scores.to_csv(OUT/'series_y_grupos.csv',index_label='fecha')
    zrecon_train=pca.inverse_transform(pca.transform(ztrain)*np.array([1,1,0,0,0,0,0]));zrecon_test=pca.inverse_transform(pca.transform(ztest)*np.array([1,1,0,0,0,0,0]))
    counts=scores.groupby(['periodo','grupo']).size().rename('meses').reset_index();counts.to_csv(OUT/'conteo_grupos.csv',index=False)
    report={'fecha_inicial':str(d.index.min().date()),'fecha_final':str(d.index.max().date()),'desarrollo_n':len(train),'posterior_n':len(test),'variables':COLS,'pca_varianza_explicada':ratio.tolist(),'factor_iteraciones':int(fa.n_iter_),'factor_convergencia':bool(fa.n_iter_<fa.max_iter),'grupos_elegidos':int(cluster.n_clusters),'silhouette_desarrollo':sil.to_dict('records'),'gmm_convergencia':bool(gmm.converged_),'gmm_covarianza':'diagonal','ari_kmeans_gmm_desarrollo':float(adjusted_rand_score(cluster.predict(ztrain),gmm.predict(ztrain))),'ari_kmeans_gmm_posterior':float(adjusted_rand_score(cluster.predict(ztest),gmm.predict(ztest))),'gmm_posterior_prob_max_inferior_080_pct':float(100*(gmm.predict_proba(ztest).max(axis=1)<.8).mean()),'distancia_p95_desarrollo':threshold,'distancia_posterior_supera_p95_desarrollo_pct':float(100*(distances>threshold).mean()),'reconstruccion_pca2_mse_desarrollo':float(np.mean((ztrain-zrecon_train)**2)),'reconstruccion_pca2_mse_posterior':float(np.mean((ztest-zrecon_test)**2)),'nota':'Exploración descriptiva retrospectiva; grupos no son categorías de riesgo, ni son independientes en el tiempo.'}
    (OUT/'resumen.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    plot_outputs(d,pca,fa,labels,train,report)
    fig,ax=plt.subplots(figsize=(10,4));ax.plot(scores.index,scores.distancia_centro,color='#007e81',label='Distancia al centro más cercano');ax.axhline(threshold,color='#b66e4d',ls='--',label='Percentil 95 en desarrollo');ax.axvline(pd.Timestamp('2023-01-01'),color='#555',ls=':',label='Inicio periodo posterior');ax.set(title='Distancia a grupos históricos en variables estandarizadas',ylabel='Distancia euclídea',xlabel='Mes');ax.legend(frameon=False);ax.grid(alpha=.15);fig.tight_layout();fig.savefig(FIG/'16_distancia_grupos.png');plt.close(fig)
    print(json.dumps(report,indent=2,ensure_ascii=False));print('\nCargas PCA\n',pcaload.iloc[:,:2].round(3).to_string());print('\nFactores\n',faload.round(3).to_string());print('\nGrupos\n',counts.to_string(index=False))

if __name__=='__main__': main()
