import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from analisis_multivariado import COLS,build_features,fit_analysis
from contexto_economico import read_ipc
from data import load

def test_variables_reales_alineacion_y_deflactacion():
    raw=load(); ipc=read_ipc(ROOT/'data/territorial/raw/ipc_dane_oct2026.xlsx')
    d=build_features(raw,ipc)
    assert list(d.columns)==COLS and not d.isna().any().any()
    assert d.index.min()==pd.Timestamp('2017-01-31')
    s=ipc.set_index('fecha').ipc
    expected=100*((raw.loc['2025-06-30','bruto']/raw.loc['2024-06-30','bruto'])/(s.loc['2025-06-30']/s.loc['2024-06-30'])-1)
    assert d.loc['2025-06-30','crecimiento_real_cartera_pct']==pytest.approx(expected)

def test_parametros_no_cambian_con_periodo_posterior():
    d=build_features(load(),read_ipc(ROOT/'data/territorial/raw/ipc_dane_oct2026.xlsx'))
    modified=d.copy();modified.loc['2023-01-01':,COLS]*=3
    a=fit_analysis(d);b=fit_analysis(modified)
    np.testing.assert_allclose(a[2].mean_,b[2].mean_)
    np.testing.assert_allclose(a[3].explained_variance_,b[3].explained_variance_)
    np.testing.assert_allclose(a[4].components_,b[4].components_)
    np.testing.assert_allclose(a[5].cluster_centers_,b[5].cluster_centers_)
    np.testing.assert_allclose(a[11].means_,b[11].means_)

def test_ipc_incompleto_falla():
    raw=load();ipc=read_ipc(ROOT/'data/territorial/raw/ipc_dane_oct2026.xlsx')
    with pytest.raises(ValueError,match='IPC incompleto'):
        build_features(raw,ipc[ipc.fecha!=pd.Timestamp('2020-05-31')])
