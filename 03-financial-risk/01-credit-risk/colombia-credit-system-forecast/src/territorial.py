"""Cruce SFC municipal–DIVIPOLA–población, con cuarentena y conciliación."""
import hashlib
import json
import re
import unicodedata
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/territorial/raw'; OUT=ROOT/'data/territorial/processed'; FIG=ROOT/'reports/figures'

def normalize(text):
    text=unicodedata.normalize('NFKD',str(text).upper().replace('#','Ñ'))
    return re.sub(r'[^A-Z0-9]','', ''.join(c for c in text if not unicodedata.combining(c)))

def verify_inputs():
    manifest=json.loads((RAW/'manifest.json').read_text())
    for name in ['sfc_municipios.json','sfc_duplicados.json','divipola.json','poblacion_dane.xlsx']:
        if hashlib.sha256((RAW/name).read_bytes()).hexdigest()!=manifest[name]['sha256']: raise ValueError('Hash no coincide: '+name)
    if json.loads((RAW/'sfc_duplicados.json').read_text()): raise ValueError('SFC contiene claves duplicadas')

def run():
    verify_inputs(); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    records=pd.read_json(RAW/'sfc_municipios.json',dtype=str)
    for key in ['cartera','filas','filas_con_cartera']: records[key]=pd.to_numeric(records[key],errors='raise')
    if records[['cartera','filas','filas_con_cartera']].isna().any().any() or (records.filas!=records.filas_con_cartera).any(): raise ValueError('SFC: valores faltantes')
    if (records.cartera<0).any(): raise ValueError('SFC: cartera negativa')
    records['fecha']=pd.to_datetime(records.fecha_de_corte).dt.strftime('%Y-%m-%d')
    keys=['fecha','tipo_de_entidad','c_digo_del_departamento','c_digo_del_municipio','nombre_del_municipio']
    if records.duplicated(keys).any(): raise ValueError('Grano agregado SFC duplicado')
    # Se excluyen IOE para aproximar el universo NIIF; fuentes y tratamientos no son idénticos.
    s=records[records.tipo_de_entidad!='22'].copy()
    national=s[s.nombre_del_municipio=='TOTAL NACIONAL'].groupby('fecha').cartera.sum()
    subtotal=s[s.c_digo_del_municipio=='999'].copy()
    city=s[(s.c_digo_del_municipio!='999')&(s.nombre_del_municipio!='TOTAL NACIONAL')].copy()
    # SFC usa otro código departamental. Los subtotales identifican el nombre del departamento.
    names=subtotal[['c_digo_del_departamento','nombre_del_municipio']].drop_duplicates()
    if names.c_digo_del_departamento.duplicated().any(): raise ValueError('Nombre departamental SFC ambiguo')
    names['sfc_depto']=names.nombre_del_municipio.str.replace('TOTAL ','',regex=False)
    special={'N. SANTANDER':'NORTE DE SANTANDER','S. ANDRES Y PROV.':'ARCHIPIELAGO DE SAN ANDRES PROVIDENCIA Y SANTA CATALINA','GUAJIRA':'LA GUAJIRA'}
    names['sfc_depto']=names.sfc_depto.replace(special)
    names=pd.concat([names[['c_digo_del_departamento','sfc_depto']],pd.DataFrame([{'c_digo_del_departamento':'3','sfc_depto':'BOGOTA D C'}])],ignore_index=True)
    div=pd.read_json(RAW/'divipola.json',dtype=str)
    div['dept_norm']=div.dpto.map(normalize); names['dept_norm']=names.sfc_depto.map(normalize)
    depts=div[['cod_dpto','dept_norm']].drop_duplicates()
    if depts.dept_norm.duplicated().any(): raise ValueError('Departamentos DANE ambiguos')
    cross=names.merge(depts,on='dept_norm',how='left',validate='one_to_one')
    if cross.cod_dpto.isna().any(): raise ValueError('Departamento no homologado: '+str(cross[cross.cod_dpto.isna()].to_dict('records')))
    city=city.merge(cross[['c_digo_del_departamento','cod_dpto']],on='c_digo_del_departamento',how='left',validate='many_to_one')
    city['cod_mpio']=city.cod_dpto+city.c_digo_del_municipio.str.zfill(3)
    if div.cod_mpio.duplicated().any(): raise ValueError('DIVIPOLA con códigos duplicados')
    city=city.merge(div[['cod_mpio','nom_mpio','dpto','latitud','longitud']],on='cod_mpio',how='left',validate='many_to_one')
    city['nombre_coincide']=(city.nombre_del_municipio.map(normalize)==city.nom_mpio.map(normalize))
    # Alias oficiales de ciudades principales, comprobados junto al código DIVIPOLA.
    aliases={'11001':('BOGOTA','BOGOTA D C'),'76001':('CALI','SANTIAGO DE CALI'),'13001':('CARTAGENA','CARTAGENA DE INDIAS'),'54001':('CUCUTA','SAN JOSE DE CUCUTA')}
    for code,(sfc_name,dane_name) in aliases.items():
        mask=(city.cod_mpio==code)&(city.nombre_del_municipio.map(normalize)==normalize(sfc_name))&(city.nom_mpio.map(normalize)==normalize(dane_name))
        city.loc[mask,'nombre_coincide']=True
    # Sin coincidencia exacta o alias revisado no se asume equivalencia.
    valid=city[city.nom_mpio.notna() & city.nombre_coincide].copy()
    unmatched=city[~(city.nom_mpio.notna() & city.nombre_coincide)].copy()
    unmatched.to_csv(OUT/'cuarentena_homologacion.csv',index=False)
    municipalities=valid.groupby(['fecha','cod_mpio','nom_mpio','dpto','latitud','longitud'],dropna=False,as_index=False).agg(cartera=('cartera','sum'),filas=('filas','sum'))
    # DANE: proyección anual para total de cada municipio, no dato censal observado al corte.
    pop=pd.read_excel(RAW/'poblacion_dane.xlsx',sheet_name='PobMunicipalxÁrea',header=7,dtype={'MPIO':str})
    pop=pop[(pop['ÁREA GEOGRÁFICA']=='Total') & (pop['AÑO'].isin([2025,2026]))][['MPIO','AÑO','TOTAL']].copy()
    pop.columns=['cod_mpio','year','poblacion']; pop.cod_mpio=pop.cod_mpio.str.zfill(5)
    if pop.duplicated(['cod_mpio','year']).any() or (pop.poblacion<0).any(): raise ValueError('Población DANE inválida')
    # Cero es posible en áreas no municipalizadas; no es un denominador válido.
    pop.loc[pop.poblacion==0,'poblacion']=np.nan
    municipalities['year']=pd.to_datetime(municipalities.fecha).dt.year
    municipalities=municipalities.merge(pop,on=['cod_mpio','year'],how='left',validate='one_to_one')
    for col in ['latitud','longitud']: municipalities[col]=pd.to_numeric(municipalities[col].str.replace(',','.',regex=False),errors='coerce')
    municipalities['cartera_por_habitante']=municipalities.cartera/municipalities.poblacion
    municipalities['cartera_billones']=municipalities.cartera/1e12
    municipalities.to_csv(OUT/'municipios.csv',index=False,float_format='%.6f')
    # Diferencia sin aproximaciones entre suma municipal y total reportado: Bogotá es municipio y distrito.
    city_sum=city.groupby('fecha').cartera.sum()
    ratio=(city_sum/national)
    if (ratio.sub(1).abs()>1e-4).any(): raise ValueError('Diferencia municipal/nacional supera 0,01 %: '+str(ratio.to_dict()))
    summary=[]
    for date,g in municipalities.groupby('fecha'):
        total=float(national[date]); unmatched_g=unmatched[unmatched.fecha==date]
        summary.append({'fecha':date,'cartera_total_nacional':total,'cartera_municipios_conciliados':float(city_sum[date]),'diferencia_relativa':float(ratio[date]-1),'municipios_homologados':len(g),'municipios_sin_poblacion':int(g.poblacion.isna().sum()),'municipios_sin_coordenadas':int(g[['latitud','longitud']].isna().any(axis=1).sum()),'cartera_homologada_pct':float(100*g.cartera.sum()/total),'filas_cuarentena':len(unmatched_g),'cartera_cuarentena_pct':float(100*unmatched_g.cartera.sum()/total)})
    summary=pd.DataFrame(summary); summary.to_csv(OUT/'calidad.csv',index=False)
    d=municipalities[municipalities.fecha=='2026-06-30'].copy(); d['departamento']=d.dpto
    dept=d.groupby('departamento',as_index=False).agg(cartera=('cartera','sum'),poblacion=('poblacion','sum'),municipios=('cod_mpio','count'))
    dept['participacion_total_nacional_pct']=100*dept.cartera/float(national['2026-06-30'])
    dept.to_csv(OUT/'departamentos_2026.csv',index=False,float_format='%.6f')
    plt.rcParams.update({'font.size':9,'figure.dpi':150,'axes.spines.top':False,'axes.spines.right':False})
    plot=d.dropna(subset=['latitud','longitud','poblacion']); plot=plot[plot.cartera>0]
    fig,ax=plt.subplots(figsize=(7,8)); im=ax.scatter(plot.longitud,plot.latitud,c=np.log10(plot.cartera/1e6),s=8,alpha=.8,cmap='viridis',linewidths=0)
    fig.colorbar(im,ax=ax,label='log10 de cartera en millones COP'); ax.set(title='Cartera municipal reportada · junio 2026',xlabel='Longitud',ylabel='Latitud'); ax.set_aspect('equal',adjustable='box');ax.grid(alpha=.15);fig.tight_layout();fig.savefig(FIG/'05_cartera_municipal.png');plt.close(fig)
    top=dept.nlargest(10,'cartera').sort_values('cartera'); fig,ax=plt.subplots(figsize=(9,5));bars=ax.barh(top.departamento,top.cartera/1e12,color='#007e81');ax.bar_label(bars,fmt='%.1f',padding=3);ax.set(xlabel='Billones COP corrientes',title='Cartera reportada: departamentos homologados · junio 2026');ax.set_xlim(0,top.cartera.max()/1e12*1.2);fig.tight_layout();fig.savefig(FIG/'06_cartera_departamental.png');plt.close(fig)
    print(summary.to_string(index=False));print(dept.nlargest(8,'cartera').to_string(index=False));print('Cuarentena ejemplos',unmatched[['c_digo_del_departamento','c_digo_del_municipio','nombre_del_municipio','nom_mpio']].drop_duplicates().head(20).to_string(index=False))

if __name__=='__main__': run()
