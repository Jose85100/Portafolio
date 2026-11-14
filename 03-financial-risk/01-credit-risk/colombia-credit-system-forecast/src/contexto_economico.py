"""IPC mensual y comparación por tipo de entidad; sin afirmar causalidad."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/territorial/raw'; OUT=ROOT/'data/territorial/processed'; FIG=ROOT/'reports/figures'
FILES={'1':('Bancos','sfc_bancos.xlsx'),'2':('Corporaciones financieras','sfc_corporaciones.xlsx'),'4':('Compañías de financiamiento','sfc_financiamiento.xlsx'),'32':('Cooperativas financieras','sfc_cooperativas.xlsx')}
MONTHS=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']

def check():
    manifest=json.loads((RAW/'contexto_manifest.json').read_text())
    for name in [v[1] for v in FILES.values()]+['ipc_dane_oct2026.xlsx']:
        if hashlib.sha256((RAW/name).read_bytes()).hexdigest()!=manifest[name]['sha256']: raise ValueError('Hash incorrecto: '+name)

def read_ipc(path):
    raw=pd.read_excel(path,sheet_name='IndicesIPC',header=None)
    if str(raw.iat[8,0]).strip()!='Mes': raise ValueError('Estructura IPC inesperada')
    result=[]
    for col in range(1,raw.shape[1]):
        try: year=int(raw.iat[8,col])
        except (ValueError,TypeError): continue
        for m in range(1,13):
            month=raw.iat[8+m,0]; value=raw.iat[8+m,col]
            if str(month).upper().strip()!=MONTHS[m-1]: raise ValueError('Mes IPC inesperado')
            if pd.notna(value): result.append({'fecha':pd.Timestamp(year,m,1)+pd.offsets.MonthEnd(),'ipc':float(value)})
    df=pd.DataFrame(result).sort_values('fecha')
    if df.fecha.duplicated().any() or (df.ipc<=0).any(): raise ValueError('IPC duplicado o no positivo')
    df['inflacion_12m_pct']=100*(df.ipc/df.ipc.shift(12)-1)
    return df

def type_breakdown():
    sfc=pd.read_json(RAW/'sfc_municipios.json',dtype=str)
    sfc=sfc[(sfc.fecha_de_corte.str.startswith('2026-06-30')) & (sfc.nombre_del_municipio=='TOTAL NACIONAL')].copy()
    sfc['cartera']=pd.to_numeric(sfc.cartera)
    geo=sfc.groupby('tipo_de_entidad').cartera.sum()
    rows=[]
    for kind,(label,file) in FILES.items():
        frame=pd.read_excel(RAW/file,sheet_name='CarteraPorModalidad',header=None)
        matches=frame.iloc[:,0].astype(str).str.strip().eq('TOTAL - BRUTO') & (frame.index<17)
        cols=frame.iloc[2,:].astype(str).str.strip().eq('JUNIO-2026')
        if matches.sum()!=1 or cols.sum()!=1 or kind not in geo.index: raise ValueError('Estructura NIIF por tipo inesperada: '+file)
        niif=float(frame.loc[matches,cols].iloc[0,0])*1e6
        rows.append({'tipo':kind,'grupo':label,'niif_pesos':niif,'territorial_pesos':float(geo[kind]),'diferencia_pesos':niif-float(geo[kind]),'procesado_niif':str(frame.iat[1,0])})
    result=pd.DataFrame(rows)
    if (result[['niif_pesos','territorial_pesos']]<0).any().any(): raise ValueError('Saldo negativo')
    return result

def run():
    check(); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    ipc=read_ipc(RAW/'ipc_dane_oct2026.xlsx'); ipc.to_csv(OUT/'ipc_mensual_dane.csv',index=False,float_format='%.6f')
    q=pd.read_csv(OUT/'calidad.csv',parse_dates=['fecha']).set_index('fecha')
    annual=q.loc[pd.to_datetime(['2023-06-30','2024-06-30','2025-06-30','2026-06-30']),['cartera_total_nacional']].copy()
    annual['ipc']=ipc.set_index('fecha').loc[annual.index,'ipc']
    annual['indice_nominal_2023']=100*annual.cartera_total_nacional/annual.cartera_total_nacional.iloc[0]
    annual['indice_real_ipc_2023']=annual.indice_nominal_2023*annual.ipc.iloc[0]/annual.ipc
    annual.to_csv(OUT/'serie_junio_real.csv',index_label='fecha',float_format='%.6f')
    dates=pd.to_datetime(['2025-06-30','2026-06-30']); vals=ipc.set_index('fecha').loc[dates,'ipc']
    previous=float(q.loc[dates[0],'cartera_total_nacional']); current=float(q.loc[dates[1],'cartera_total_nacional'])
    nominal=current/previous-1; inflation=float(vals.iloc[1]/vals.iloc[0]-1); real=(1+nominal)/(1+inflation)-1
    factors={'fecha_inicial':'2025-06-30','fecha_final':'2026-06-30','cartera_inicial_pesos':previous,'cartera_final_pesos':current,'ipc_inicial':float(vals.iloc[0]),'ipc_final':float(vals.iloc[1]),'crecimiento_nominal_pct':100*nominal,'inflacion_ipc_pct':100*inflation,'crecimiento_deflactado_ipc_pct':100*real,'advertencia':'Aproximación a precios de consumo nacional, no deflactor específico de crédito; no refleja inclusión, ni identifica una causa.'}
    (OUT/'crecimiento_real.json').write_text(json.dumps(factors,ensure_ascii=False,indent=2)+'\n')
    compare=type_breakdown();compare.to_csv(OUT/'brecha_por_tipo.csv',index=False,float_format='%.2f')
    plt.rcParams.update({'font.size':10,'figure.dpi':150,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(9,4.5));x=np.arange(len(compare)); dif=compare.diferencia_pesos/1e12
    bars=ax.barh(x,dif,color='#007e81');ax.bar_label(bars,labels=[f'{v:.2f}' if v>=.01 else '<0,01' for v in dif],padding=3);ax.set_yticks(x,compare.grupo)
    ax.set(xlabel='Diferencia NIIF − territorial · billones COP',title='Brecha entre fuentes por tipo · junio 2026');ax.set_xlim(0,dif.max()*1.25);ax.invert_yaxis();fig.tight_layout();fig.savefig(FIG/'08_fuentes_por_tipo.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4)); sel=ipc[ipc.fecha>='2020-01-01'];ax.plot(sel.fecha,sel.inflacion_12m_pct,color='#b66e4d');ax.axhline(0,color='#777',lw=.7);ax.set(title='Inflación anual del IPC nacional · DANE',ylabel='Variación a 12 meses (%)',xlabel='Mes');ax.grid(alpha=.15);fig.tight_layout();fig.savefig(FIG/'09_inflacion_mensual.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4.5)); ax.plot(annual.index,annual.indice_nominal_2023,marker='o',label='Nominal',color='#b66e4d');ax.plot(annual.index,annual.indice_real_ipc_2023,marker='s',label='Ajustado por IPC',color='#007e81');ax.set_xticks(annual.index,[f'Junio {date.year}' for date in annual.index]);ax.set(title='Cartera territorial nacional: junio de cada año',ylabel='Índice · junio 2023 = 100',xlabel='Corte');ax.grid(alpha=.15);ax.legend(frameon=False);fig.tight_layout();fig.savefig(FIG/'10_cartera_ajustada.png');plt.close(fig)
    print(json.dumps(factors,ensure_ascii=False,indent=2));print(compare.to_string(index=False))

if __name__=='__main__': run()
