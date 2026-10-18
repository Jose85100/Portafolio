"""Independent identities, pathological inputs and end-to-end reconciliation."""
import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from numpy.testing import assert_allclose
sys.path.insert(0,str(Path(__file__).parents[1]))
from src.multimodel import *
from src.multimodel.contracts import default_curve, weights
from src.multimodel.lgd import FractionalLogit
from src.multimodel.data import synthetic_history, reporting_portfolio, standard_scenarios
from src.multimodel.experiment import fit_experiment
from src.multimodel.validation import binary_metrics


class TestCurves(unittest.TestCase):
    def test_survival_reconciles(self):
        q=np.array([[.1,.2,.3],[0,1,.3]])
        mass,survival=default_curve(q)
        assert_allclose(mass.sum(axis=1)+survival[:,-1],1)
        assert_allclose(mass[0],[.1,.18,.216]); assert_allclose(mass[1],[0,1,0])

    def test_reject_bad_curves(self):
        for q in [[[np.nan]], [[1.1]], [[-.1]], []]:
            with self.subTest(q=q), self.assertRaises(ValueError):default_curve(q)

    def test_markov_geometric_identity(self):
        # Counts imply monthly P(default|live)=.1 with one live state.
        t=pd.DataFrame({'from_state':[0]*10,'to_state':[0]*9+[1]})
        m=TransitionPD().fit(t,n_states=2,smoothing=0)
        p=m.predict_curve(pd.DataFrame({'rating':[0]}),[0]*24)
        assert_allclose(p.sum(),1-.9**24)
        assert_allclose(p[0,:3],[.1,.09,.081])

    def test_absorbing_state_rejects_cure(self):
        with self.assertRaises(ValueError):
            TransitionPD().fit(pd.DataFrame({'from_state':[3], 'to_state':[0]}))

    def test_missing_rating_unsmoothed(self):
        with self.assertRaises(ValueError):
            TransitionPD().fit(pd.DataFrame({'from_state':[0], 'to_state':[1]}),smoothing=0)

    def test_survival_rejects_post_default_rows(self):
        p=pd.DataFrame({'loan_id':[1,1], 'month':[1,2], 'age_months':[0,1],
            'score':[0,0], 'segment':[0,0], 'macro':[0,0], 'default':[1,0]})
        with self.assertRaises(ValueError):SurvivalPD().fit(p)

    def test_survival_rejects_duplicate_month(self):
        p=pd.DataFrame({'loan_id':[1,1], 'month':[1,1], 'age_months':[0,0],
            'score':[0,0], 'segment':[0,0], 'macro':[0,0], 'default':[0,1]})
        with self.assertRaises(ValueError):SurvivalPD().fit(p)

    def test_logit_requires_two_classes(self):
        c=pd.DataFrame({'score':[0,1], 'segment':[0,1], 'macro':[0,0], 'default_12m':[0,0]})
        with self.assertRaises(ValueError):LogisticPD().fit(c)


class TestLGDEAD(unittest.TestCase):
    def test_fractional_endpoints_and_bounds(self):
        model=FractionalLogit().fit(np.arange(10)[:,None],np.array([0]*5+[1]*5))
        p=model.predict(np.array([[-100],[100]]))
        self.assertTrue(((p>=0)&(p<=1)).all());self.assertLess(p[0],p[1])

    def test_fractional_dimension_and_nan(self):
        with self.assertRaises(ValueError):FractionalLogit().fit([[1],[2]],[np.nan,0])
        with self.assertRaises(ValueError):FractionalLogit().fit([[1],[2]],[2,0])

    def test_zero_rate_amortization_beginning_month(self):
        assert_allclose(annuity_exposure(120,0,3,5),[120,80,40,0,0])

    def test_full_prepayment_after_first_month(self):
        assert_allclose(annuity_exposure(120,0,3,5,1),[120,0,0,0,0])

    def test_prepayment_is_contractual_balance_times_retention(self):
        plain=annuity_exposure(100,.12,24,24)
        prep=annuity_exposure(100,.12,24,24,.2)
        assert_allclose(prep,plain*.8**(np.arange(24)/12))

    def test_bad_amortization(self):
        for args in [(100,0,0,12),(100,0,True,12),(np.nan,0,12,12),(100,0,12,12,1.1)]:
            with self.subTest(args=args), self.assertRaises(ValueError):annuity_exposure(*args)

    def test_revolver_never_exceeds_limit(self):
        p=reporting_portfolio(10);p['product']='revolver';p['term_months']=12
        e=ExposureModel(fixed_ccf=1).predict(p,[0]*24)
        assert_allclose(e[:,:12],np.repeat(p['limit'].to_numpy()[:,None],12,axis=1))
        assert_allclose(e[:,12:],0)

    def test_recovery_delay_increases_lgd(self):
        p=reporting_portfolio(3); p['eir']=.1
        early=CashflowLGD(recovery_years=(0.,1.,2.)).predict(p,[0]*12,np.ones((3,12)))
        late=CashflowLGD(recovery_years=(1.,2.,3.)).predict(p,[0]*12,np.ones((3,12)))
        self.assertTrue((late>early).all())

    def test_recovery_discounted_once_to_default(self):
        p=pd.DataFrame({'collateral_ratio':[0.], 'eir':[.1]})
        m=CashflowLGD(cost_rate=0,unsecured_rate=.6,recovery_years=(2.,),recovery_weights=(1.,))
        assert_allclose(m.predict(p,[0],np.ones((1,1))),1-.6/1.1**2)


class TestStagingAndEngine(unittest.TestCase):
    def test_stage_precedence_and_zero_origin(self):
        p=reporting_portfolio(4);p['dpd']=[0,30,90,0];p['watchlist']=False
        p['origin_lifetime_pd']=0.;p['current_lifetime_pd']=[0,.1,.1,.1]
        assert_allclose(classify(p).stage,[1,2,3,2])

    def test_credit_impairment_flag_overrides_days(self):
        p=reporting_portfolio(2);p['dpd']=0;p['credit_impaired']=True
        assert_allclose(classify(p).stage,3)

    def test_same_horizon_pd_absolute_and_relative(self):
        p=reporting_portfolio(3);p['dpd']=0;p['watchlist']=False
        p['origin_lifetime_pd']=[.001,.04,.10];p['current_lifetime_pd']=[.003,.09,.11]
        assert_allclose(classify(p).stage,[1,2,1])

    def test_stage1_default_window_not_recovery_window(self):
        mass=np.zeros((2,24));mass[:,11]=.1;mass[:,12]=.2
        lgd=np.full((2,24),.5);ead=np.full((2,24),100.)
        e12,life,selected,c=component_ecl(mass,lgd,ead,[0,0],[1,2])
        assert_allclose(e12,[5,5]);assert_allclose(life,[15,15]);assert_allclose(selected,[5,15])

    def test_ecl_rejects_probability_doublecount(self):
        with self.assertRaises(ValueError):component_ecl([[.6,.6]],[[.5,.5]],[[100,100]],[0],[1])

    def test_invalid_scenario_weights(self):
        for w in [{},{'a':2,'b':-1},{'a':np.nan},{'a':.9}]:
            with self.subTest(w=w),self.assertRaises(ValueError):weights(w)

    def test_single_cashflow_discount_analytic(self):
        a=component_ecl([[.1]],[[.5]],[[100]],[.12],[1])
        assert_allclose(a[2],5/1.12**(1/12))

    def test_components_equal_direct_cash_shortfall(self):
        # 10% probability of default in month 12; gross 100, recover 60
        # two years after default. Direct PV at reporting is a separate formula.
        mass=np.zeros((1,12));mass[0,11]=.1
        lgd=np.full((1,12),1-.6/1.1**2)
        result=component_ecl(mass,lgd,np.full((1,12),100.),[.1],[1])[2]
        direct=.1*(100/1.1-60/1.1**3)
        assert_allclose(result,direct)

    def test_simple_matrix_exposure_weighting(self):
        complete=pd.DataFrame({'bucket':['a','a'],'exposure':[100.,900.],'discounted_shortfall':[10.,180.]})
        m=ProvisionMatrix().fit(complete)
        current=pd.DataFrame({'bucket':['a'],'exposure':[1000.]})
        assert_allclose(m.predict(current,{'base':(1.,1.)}),190)
        with self.assertRaises(ValueError):m.predict(pd.DataFrame({'bucket':['x'],'exposure':[1.]}),{'b':(1.,1.)})


class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.ex=fit_experiment(n_history=500,n_reporting=12)

    def test_18_configurations_finite(self):
        c=self.ex['comparison'];self.assertEqual(len(c),18)
        self.assertTrue(np.isfinite(c.ecl).all());self.assertTrue((c.ecl>=0).all())
        assert_allclose(c.stage_1+c.stage_2+c.stage_3,c.ecl)

    def test_train_oot_disjoint_with_embargo(self):
        e=self.ex;c=e['cohort'];train=c[c.loan_id.isin(e['train_ids'])]
        self.assertTrue(set(e['oot'].loan_id).isdisjoint(e['train_ids']))
        self.assertLess(train.origination_month.max()+36,e['oot'].origination_month.min())

    def test_logit_monthly_conversion_identity(self):
        e=self.ex;m=e['pd_models'][0];p=e['loans'].iloc[:3]
        annual=m.estimator.predict_proba(np.column_stack([p.score,p.segment,np.zeros(3)]))[:,1]
        assert_allclose(m.predict_curve(p,[0]*12).sum(axis=1),annual)

    def test_all_pd_masses_reconcile(self):
        for model in self.ex['pd_models']:
            mass=model.predict_curve(self.ex['loans'].query('stage != 3'),[0]*36)
            self.assertTrue(np.isfinite(mass).all());self.assertTrue((mass>=0).all());self.assertTrue((mass.sum(axis=1)<=1+1e-12).all())

    def test_scenario_and_monthly_reconciliation(self):
        e=self.ex;r=run_ecl(e['loans'],e['pd_models'][0],e['lgd_models'][0],e['ead_models'][0],e['scenarios'])
        assert_allclose(r['loans'].ecl.sum(),r['scenarios'].weighted_ecl.sum())
        monthly=r['monthly'].query('selected').groupby(['loan_id','scenario']).contribution.sum()
        live=r['scenarios'].query('stage != 3').set_index(['loan_id','scenario']).ecl
        assert_allclose(monthly.reindex(live.index),live)

    def test_stage3_independent_of_model_pd(self):
        e=self.ex;p=e['loans'].iloc[:1].copy();p['stage']=3;p['term_months']=36
        a=run_ecl(p,e['pd_models'][0],e['lgd_models'][0],e['ead_models'][0],e['scenarios'])
        p['score']=-100;p['rating']=2
        b=run_ecl(p,e['pd_models'][2],e['lgd_models'][2],e['ead_models'][1],e['scenarios'])
        assert_allclose(a['loans'].ecl,b['loans'].ecl)
        # Independent discounting calculation for base scenario.
        gross=p.balance.iloc[0];flows=np.asarray(p.recovery_cashflows.iloc[0]);rate=p.eir.iloc[0]
        expected=gross-np.sum(flows/(1+rate)**np.array([1,2,3]))
        assert_allclose(a['scenarios'].query("scenario == 'base'").ecl,expected)

    def test_rejects_broadcast_pd_curve(self):
        class BrokenPD:
            model_id='broken'
            def predict_curve(self,loans,macro):return np.full((1,len(macro)),.001)
        e=self.ex;p=e['loans'].copy();p['stage']=1
        with self.assertRaises(ValueError):run_ecl(p,BrokenPD(),e['lgd_models'][0],e['ead_models'][0],e['scenarios'])

    def test_loan_order_does_not_change_id_result(self):
        e=self.ex;args=[e['pd_models'][0],e['lgd_models'][1],e['ead_models'][1],e['scenarios']]
        a=run_ecl(e['loans'],*args)['loans'].sort_index()
        b=run_ecl(e['loans'].sample(frac=1,random_state=2),*args)['loans'].sort_index()
        assert_allclose(a.ecl,b.ecl)

    def test_reject_short_horizon_and_duplicate_id(self):
        e=self.ex;p=e['loans'].copy();args=[e['pd_models'][0],e['lgd_models'][0],e['ead_models'][0]]
        with self.assertRaises(ValueError):run_ecl(p,*args,standard_scenarios(1))
        p['loan_id']=1
        with self.assertRaises(ValueError):run_ecl(p,*args,e['scenarios'])

    def test_metrics_one_class_auc_absent(self):
        m=binary_metrics([0,0],[.1,.2]);self.assertIsNone(m['auc'])

if __name__=='__main__':unittest.main()
