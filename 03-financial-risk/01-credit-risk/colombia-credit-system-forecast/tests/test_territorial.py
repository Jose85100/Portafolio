import sys
from pathlib import Path
import pandas as pd
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from territorial import normalize, verify_inputs

def test_procedencia_y_normalizacion():
    verify_inputs()
    assert normalize('Bogotá, D.C.')=='BOGOTADC'
    assert normalize('NARI#O')=='NARINO'

def test_municipios_identificables_y_tasas_sin_duplicados():
    df=pd.read_csv(ROOT/'data/territorial/processed/municipios.csv',dtype={'cod_mpio':str})
    assert not df.duplicated(['fecha','cod_mpio']).any()
    assert (df.cartera>=0).all()
    assert not (df.nom_mpio.str.startswith('TOTAL')).any()
    subset=df.dropna(subset=['poblacion'])
    assert (subset.poblacion>0).all()
    assert ((subset.cartera/subset.poblacion-subset.cartera_por_habitante).abs()<1e-4).all()
    assert df[(df.fecha=='2026-06-30')&(df.cod_mpio=='11001')].shape[0]==1

def test_conciliacion_y_cuarentena():
    quality=pd.read_csv(ROOT/'data/territorial/processed/calidad.csv').set_index('fecha')
    assert abs(quality.loc['2026-06-30','diferencia_relativa'])<0.0001
    assert 99 < quality.loc['2026-06-30','cartera_homologada_pct'] <=100
    assert quality.loc['2026-06-30','filas_cuarentena']>0

def test_serie_macro_anual():
    df=pd.read_csv(ROOT/'data/territorial/processed/macro_anual.csv')
    assert not df.year.duplicated().any()
    assert set(range(2015,2026))==set(df.year)
    assert df.inflacion_promedio_anual.notna().all()
