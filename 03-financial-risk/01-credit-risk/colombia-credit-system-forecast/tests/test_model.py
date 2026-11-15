import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from data import load, parse_sfc
from model import features, FEATS, forecast

def test_real_data_reconciles_and_has_monthly_grain():
    df=load()
    assert len(df)>=120 and not df.index.has_duplicates
    assert ((df.vencido/df.bruto-df.indicador).abs()<1e-6).all()
    assert ((df.vigente+df.vencido-df.bruto).abs()/df.bruto<1e-7).all()
    assert df.index.max()==pd.Timestamp('2026-09-30')

def test_future_observations_do_not_change_features_or_prediction():
    raw=load(); start=pd.Timestamp('2024-06-30')
    original=features(raw)
    modified=raw.copy()
    for col in ['icv_pp','icv_consumo_pp','trm_cierre_cop_usd','bruto']:
        modified.loc[modified.index>=start-pd.offsets.MonthEnd(1),col]*=1.3
    changed=features(modified)
    pd.testing.assert_series_equal(original.loc[start,FEATS],changed.loc[start,FEATS])
    cutoff=start-pd.offsets.MonthEnd(2)
    assert forecast(original.loc[:cutoff],original.loc[start],'ridge')==pytest.approx(forecast(changed.loc[:cutoff],changed.loc[start],'ridge'))

def test_missing_source_fails(tmp_path):
    with pytest.raises(FileNotFoundError): parse_sfc(tmp_path/'missing.xlsx')
