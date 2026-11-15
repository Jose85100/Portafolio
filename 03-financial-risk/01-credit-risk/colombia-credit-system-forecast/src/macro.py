"""Contexto anual WDI para Colombia; no se usa como predictor en el backtest."""
import datetime as dt
import hashlib
import json
import ssl
from pathlib import Path
from urllib.request import urlopen
import certifi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/territorial/raw'; OUT=ROOT/'data/territorial/processed'; FIG=ROOT/'reports/figures'
INDICATORS={'inflacion_promedio_anual':'FP.CPI.TOTL.ZG'}
URL='https://api.worldbank.org/v2/country/COL/indicator/{}?format=json&per_page=100&date=2015:2025'

def download():
    manifest={}; RAW.mkdir(parents=True,exist_ok=True)
    for name,indicator in INDICATORS.items():
        url=URL.format(indicator)
        with urlopen(url,timeout=90,context=ssl.create_default_context(cafile=certifi.where())) as r: data=r.read()
        payload=json.loads(data)
        if len(payload)!=2 or not payload[1] or payload[0]['pages']!=1: raise ValueError('WDI vacío o paginado: '+name)
        file=RAW/(name+'.json');file.write_bytes(data)
        manifest[file.name]={'url':url,'sha256':hashlib.sha256(data).hexdigest(),'lastupdated':payload[0].get('lastupdated')}
    manifest['descargado_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
    (RAW/'macro_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

def run():
    manifest=json.loads((RAW/'macro_manifest.json').read_text()); series=[]
    for name,indicator in INDICATORS.items():
        f=RAW/(name+'.json')
        if hashlib.sha256(f.read_bytes()).hexdigest()!=manifest[f.name]['sha256']: raise ValueError('Hash macro incorrecto')
        payload=json.loads(f.read_text())[1]
        if any(row['countryiso3code']!='COL' or row['indicator']['id']!=indicator for row in payload): raise ValueError('Indicador o país incorrecto')
        df=pd.DataFrame([{'year':int(row['date']),name:row['value']} for row in payload])
        if df.year.duplicated().any(): raise ValueError('Año duplicado')
        series.append(df)
    frame=series[0].sort_values('year')
    OUT.mkdir(parents=True,exist_ok=True);frame.to_csv(OUT/'macro_anual.csv',index=False,float_format='%.6f')
    plt.rcParams.update({'font.size':10,'figure.dpi':150,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10,4.5)); ax.axhline(0,color='#777',lw=.8)
    ax.plot(frame.year,frame.inflacion_promedio_anual,marker='o',label='Inflación del IPC, promedio anual',color='#b06442')
    ax.set(title='Colombia: contexto macroeconómico anual · Banco Mundial',ylabel='Variación anual (%)',xlabel='Año');ax.set_xticks(frame.year);ax.legend(frameon=False);ax.grid(alpha=.15);fig.tight_layout();fig.savefig(FIG/'07_contexto_macro.png');plt.close(fig)
    print(frame.to_string(index=False))

if __name__=='__main__':
    import sys
    if '--download' in sys.argv: download()
    run()
