"""Reproduce observed input failures and distinguish already impaired losses."""
import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.ifrs9_engine import (cartera_sintetica,stage,pd_lifetime,ecl_componentes,
    ponderar_escenarios,credit_impaired_shortfall,backtest_pd)

class ContractTests(unittest.TestCase):
    def setUp(self): self.frame=cartera_sintetica(60,17)
    def test_negative_and_nonfinite_weights_rejected(self):
        for weights in ({'base':2.,'severo':-1.},{'base':np.nan},{'base':np.inf},{},{'base':.999999}):
            with self.subTest(weights=weights),self.assertRaises(ValueError):ponderar_escenarios(self.frame,weights)
    def test_duplicate_and_missing_ids_rejected(self):
        for value in (self.frame.loan_id.iloc[1],np.nan):
            frame=self.frame.copy();frame.loc[0,'loan_id']=value
            with self.assertRaises(ValueError):ecl_componentes(frame)
    def test_nonfinite_and_out_of_bounds_portfolio(self):
        for column,value in [('ead',np.inf),('ead',-1),('ccf',1.1),('lgd_base',-.1),('pd_12m',1.),('pd_origen',0.),('dpd',1.5)]:
            with self.subTest(column=column,value=value):
                frame=self.frame.copy();frame['dpd']=0;frame[column]=frame[column].astype(float);frame.loc[0,column]=value
                with self.assertRaises(ValueError):ecl_componentes(frame)
    def test_stage_index_mismatch_rejected(self):
        with self.assertRaises(ValueError):stage(self.frame.pd_12m,self.frame.pd_origen.iloc[::-1],self.frame.dpd)
    def test_stage_dpd_boundaries(self):
        index=['a','b','c','d'];current=pd.Series([.01]*4,index=index)
        result=stage(current,current,pd.Series([29,30,89,90],index=index))
        self.assertEqual(result.tolist(),[1,2,2,3]);self.assertEqual(result.index.tolist(),index)
    def test_survival_reconciles_and_zero_hazard(self):
        probabilities=pd.Series([0.,.01,.2,.99]);conditional,marginal=pd_lifetime(probabilities,8,.1)
        survival=np.cumprod(1-conditional,axis=1)
        np.testing.assert_allclose(np.cumsum(marginal,axis=1),1-survival,atol=1e-14)
        self.assertTrue(np.all(marginal>=0));self.assertTrue(np.all(marginal.sum(axis=1)<=1+1e-14))
        self.assertEqual(marginal[0].sum(),0.)
    def test_curve_rejects_invalid_parameters(self):
        for probabilities,horizon,growth in [([1.2],5,.1),([np.nan],5,.1),([1.],5,.1),([.1],0,.1),([.1],True,.1),([.1],5,np.inf),([.1],5,-2.)]:
            with self.subTest(probabilities=probabilities,horizon=horizon),self.assertRaises(ValueError):pd_lifetime(pd.Series(probabilities),horizon,growth)
    def test_high_base_pd_is_not_reduced_by_hidden_cap(self):
        frame=self.frame.iloc[[0]].copy();frame['pd_12m']=.99;frame['pd_origen']=.99;frame['dpd']=0
        result=ecl_componentes(frame,horizonte=1,tasa_descuento=0.)
        expected=.99*frame.lgd_base.iloc[0]*(frame.ead.iloc[0]+frame.ccf.iloc[0]*frame.undrawn.iloc[0])
        self.assertAlmostEqual(result.ecl.iloc[0],expected)
    def test_funded_impaired_cashflow_identity(self):
        result=credit_impaired_shortfall(100,[55,60.5],[1,2],.1)
        self.assertAlmostEqual(result['pv_expected_recoveries'],100.)
        self.assertAlmostEqual(result['ecl'],0.)
        lower=credit_impaired_shortfall(100,[50],[1],.1)
        self.assertAlmostEqual(lower['ecl'],100-50/1.1)
    def test_recovery_delay_increases_loss(self):
        early=credit_impaired_shortfall(100,[60],[1],.1)
        late=credit_impaired_shortfall(100,[60],[3],.1)
        self.assertGreater(late['ecl'],early['ecl'])
    def test_recovery_surplus_is_visible(self):
        result=credit_impaired_shortfall(100,[120],[0],.1)
        self.assertEqual(result['ecl'],0.);self.assertEqual(result['raw_shortfall'],-20.)
        self.assertEqual(result['recovery_surplus'],20.)
    def test_impaired_does_not_depend_on_future_default_pd(self):
        frame=self.frame.iloc[[0]].copy();frame['dpd']=95
        a=ecl_componentes(frame)
        frame['pd_12m']=1.;b=ecl_componentes(frame)
        self.assertEqual(a.ecl.iloc[0],b.ecl.iloc[0])
        self.assertEqual(b.ecl_basis.iloc[0],'funded_recovery_cashflows')
        self.assertTrue(b.ecl_12m.isna().all());self.assertTrue(b.ecl_lifetime.isna().all())
    def test_impaired_rejects_missing_recovery_inputs(self):
        frame=self.frame.iloc[[0]].copy();frame['dpd']=95
        with self.assertRaises(ValueError):ecl_componentes(frame.drop(columns=['recovery_cashflows']))
    def test_recovery_contract_rejects_nonfinite_and_times(self):
        for flows,times,rate in [([np.nan],[1],.1),([1],[np.inf],.1),([1,2],[2,1],.1),([1],[1],-1.),([-1],[1],.1)]:
            with self.subTest(flows=flows,times=times),self.assertRaises(ValueError):credit_impaired_shortfall(100,flows,times,rate)
    def test_scenario_weighted_loss_inside_convex_hull(self):
        result=ponderar_escenarios(self.frame,{'base':.5,'adverso':.3,'severo':.2})
        self.assertTrue((result.ecl_ponderada>=result[['base','adverso','severo']].min(axis=1)-1e-9).all())
        self.assertTrue((result.ecl_ponderada<=result[['base','adverso','severo']].max(axis=1)+1e-9).all())
    def test_calibration_rejects_nonbinary_or_misaligned_labels(self):
        with self.assertRaises(ValueError):backtest_pd(pd.Series([.1,.2]),pd.Series([0,2]),2)
        with self.assertRaises(ValueError):backtest_pd(pd.Series([.1,.2],index=[0,1]),pd.Series([0,1],index=[1,0]),2)
