"""Transformación trazable de agregados SFC y TRM, con controles fail-closed."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
MONTHS={s:i for i,s in enumerate(['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'],1)}
ROW_MAP={'bruto':'TOTAL - BRUTO','vigente':'TOTAL - VIGENTE','vencido':'TOTAL - VENCIDO','indicador':'TOTAL - CALIDAD MORA','comercial_bruto':'COMERCIAL - BRUTO','comercial_vencido':'COMERCIAL - VENCIDO','consumo_bruto':'CONSUMO - BRUTO','consumo_vencido':'CONSUMO - VENCIDO','vivienda_bruto':'VIVIENDA - BRUTO','vivienda_vencido':'VIVIENDA - VENCIDO','microcredito_bruto':'MICROCREDITO - BRUTO','microcredito_vencido':'MICROCREDITO - VENCIDO'}

def validate_manifest():
    folder=ROOT/'data/raw'; meta=json.loads((folder/'manifest.json').read_text())
    for name in ['sfc_total_ec_niif.xlsx','trm.json']:
        if hashlib.sha256((folder/name).read_bytes()).hexdigest()!=meta[name]['sha256']:
            raise ValueError(f'Hash no coincide: {name}')

def parse_sfc(path):
    sheet=pd.read_excel(path,sheet_name='CarteraPorModalidad',header=None)
    if 'Todos los EC sin Ioes' not in str(sheet.iat[0,0]):
        raise ValueError('Cobertura desconocida en hoja SFC')
    labels=sheet.iloc[:,0].astype(str).str.strip()
    dates=[]
    for item in sheet.iloc[2,1:]:
        parts=str(item).upper().strip().split('-')
        if len(parts)!=2 or parts[0] not in MONTHS or not parts[1].isdigit():
            raise ValueError(f'Fecha de columna no reconocida: {item}')
        dates.append(pd.Timestamp(int(parts[1]),MONTHS[parts[0]],1)+pd.offsets.MonthEnd())
    if len(set(dates))!=len(dates): raise ValueError('Fechas SFC duplicadas')
    result=pd.DataFrame(index=pd.DatetimeIndex(dates,name='fecha'))
    for key,label in ROW_MAP.items():
        matches=np.flatnonzero(labels.eq(label))
        # Hay secciones que repiten etiquetas: se utiliza la primera, por morosidad.
        if len(matches)==0: raise ValueError(f'Fila ausente: {label}')
        result[key]=pd.to_numeric(sheet.iloc[matches[0],1:].values,errors='coerce')
    if result.isna().any().any() or not np.isfinite(result.to_numpy()).all(): raise ValueError('SFC contiene vacíos o no finitos')
    if not result.index.equals(pd.date_range(result.index.min(),result.index.max(),freq='ME',name='fecha')): raise ValueError('Meses SFC ausentes')
    for col in ['bruto','comercial_bruto','consumo_bruto','vivienda_bruto','microcredito_bruto']:
        if (result[col]<=0).any(): raise ValueError(f'Denominador inválido: {col}')
    for col in ['vencido','vigente','comercial_vencido','consumo_vencido','vivienda_vencido','microcredito_vencido']:
        if (result[col]<0).any(): raise ValueError(f'Saldo negativo: {col}')
    computed=result.vencido/result.bruto
    err=(computed-result.indicador).abs()
    if err.max()>1e-6: raise ValueError(f'Indicador no concilia: {err.max()}')
    if ((result.vigente+result.vencido-result.bruto).abs()/result.bruto).max()>1e-7:
        raise ValueError('Cartera vigente y vencida no concilian con bruto')
    result['icv_pp']=computed*100
    for segment in ['comercial','consumo','vivienda','microcredito']:
        result[f'icv_{segment}_pp']=100*result[f'{segment}_vencido']/result[f'{segment}_bruto']
    result.attrs['max_ratio_difference']=float(err.max())
    return result

def parse_trm(path, dates):
    trm=pd.DataFrame(json.loads(path.read_text()))
    trm['inicio']=pd.to_datetime(trm.vigenciadesde); trm['fin']=pd.to_datetime(trm.vigenciahasta)
    trm['valor']=pd.to_numeric(trm.valor,errors='raise'); trm=trm.sort_values('inicio')
    if trm.inicio.duplicated().any() or (trm.valor<=0).any() or not (trm.unidad=='COP').all(): raise ValueError('TRM inválida')
    if (trm.fin<trm.inicio).any() or (trm.fin.shift(1).iloc[1:].to_numpy()>=trm.inicio.iloc[1:].to_numpy()).any(): raise ValueError('Vigencias TRM solapadas')
    probe=pd.DataFrame({'fecha':dates})
    joined=pd.merge_asof(probe,trm,left_on='fecha',right_on='inicio',direction='backward')
    if joined.valor.isna().any() or (joined.fecha>joined.fin).any(): raise ValueError('TRM sin vigencia para fecha consultada')
    return pd.Series(joined.valor.to_numpy(),index=dates,name='trm_cierre_cop_usd')

def load():
    validate_manifest()
    df=parse_sfc(ROOT/'data/raw/sfc_total_ec_niif.xlsx')
    df['trm_cierre_cop_usd']=parse_trm(ROOT/'data/raw/trm.json',df.index)
    return df
