import json
import sys
from pathlib import Path
import pandas as pd
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contexto_economico import check, read_ipc, type_breakdown
from data import load
from modelo_ipc import make_features

def test_indice_ipc_fecha_y_origen():
    check()
    ipc=read_ipc(ROOT/'data/territorial/raw/ipc_dane_oct2026.xlsx').set_index('fecha')
    assert ipc.loc['2025-06-30','ipc']==pytest.approx(150.30)
    assert ipc.loc['2026-06-30','ipc']==pytest.approx(159.53)

def test_deflactacion_y_fuentes_por_tipo():
    result=json.loads((ROOT/'data/territorial/processed/crecimiento_real.json').read_text())
    expected=100*((result['cartera_final_pesos']/result['cartera_inicial_pesos'])/(result['ipc_final']/result['ipc_inicial'])-1)
    assert result['crecimiento_deflactado_ipc_pct']==pytest.approx(expected)
    types=type_breakdown().set_index('tipo')
    assert set(types.index)=={'1','2','4','32'}
    assert types.loc['1','diferencia_pesos']>0
    assert types.loc['1','diferencia_pesos']==pytest.approx(types.loc['1','niif_pesos']-types.loc['1','territorial_pesos'])

def test_cuarentena_no_es_homologacion_automatica():
    candidates=pd.read_csv(ROOT/'data/territorial/processed/candidatos_sensibilidad.csv',dtype={'cod_mpio':str})
    clean=pd.read_csv(ROOT/'data/territorial/processed/municipios.csv',dtype={'cod_mpio':str})
    assert not candidates.merge(clean,on=['fecha','cod_mpio']).shape[0]

def test_inflacion_usa_2_meses_de_rezago():
    raw=load(); ipc=read_ipc(ROOT/'data/territorial/raw/ipc_dane_oct2026.xlsx')
    df=make_features(raw,ipc)
    target=pd.Timestamp('2025-06-30')
    expected=ipc.set_index('fecha').loc['2025-04-30','inflacion_12m_pct']
    assert df.loc[target,'inflacion_12m_lag2']==pytest.approx(expected)
