import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vintage_core import build_vintage, summarize_vintage


def row(loan, client, mob, dpd, balance=100, cohort='2024-01'):
    return dict(loan_key=loan, merchant_key='m', client_id=client, corte_origen=cohort,
                mob=mob, dpd=dpd, saldo_capital_cop=balance, fecha_disponibilidad=f'2024-0{mob+1}-28')


class VintageTest(unittest.TestCase):
    def test_strict_threshold_amount_and_censoring(self):
        data = pd.DataFrame([row('a','1',1,0),row('a','1',2,31),row('a','1',3,0,200),
                             row('b','2',1,0),row('b','2',2,30),row('b','2',3,0,100),
                             row('c','3',1,0),row('c','3',3,50,80)])
        accounts, clients = build_vintage(data)
        out = summarize_vintage(accounts).iloc[0]
        self.assertEqual((out.universo,out.no_evaluables,out.n_maduros,out.n_eventos),(3,1,2,1))
        self.assertAlmostEqual(out.ever_numero,.5)
        self.assertAlmostEqual(out.ever_saldo,2/3)
        self.assertEqual(len(clients),3)

    def test_client_requires_complete_accounts(self):
        data = pd.DataFrame([row('a','1',1,31),row('a','1',2,0),row('a','1',3,0),
                             row('b','1',1,0),row('b','1',3,0)])
        accounts,clients=build_vintage(data)
        self.assertEqual(accounts.eligible.sum(),1)
        self.assertFalse(clients.iloc[0].eligible)
        self.assertTrue(pd.isna(clients.iloc[0].ever30))

    def test_missing_balance_does_not_remove_count(self):
        data=pd.DataFrame([row('a','1',1,31),row('a','1',2,0),row('a','1',3,0,None)])
        a,_=build_vintage(data);out=summarize_vintage(a).iloc[0]
        self.assertEqual(out.n_maduros,1); self.assertEqual(out.n_saldo_valido,0)
        self.assertTrue(pd.isna(out.ever_saldo));self.assertEqual(out.ever_numero,1)

    def test_duplicate_rejected_and_asof_censors(self):
        data=pd.DataFrame([row('a','1',1,0),row('a','1',2,0),row('a','1',3,0)])
        with self.assertRaises(ValueError): build_vintage(pd.concat([data,data.iloc[[0]]]))
        a,_=build_vintage(data,as_of='2024-03-31');self.assertFalse(a.iloc[0].eligible)

    def test_client_aggregates_all_represented_accounts(self):
        data=pd.DataFrame([row('a','1',1,31),row('a','1',2,0),row('a','1',3,0,100),
                           row('b','1',1,0),row('b','1',2,0),row('b','1',3,0,300)])
        _,clients=build_vintage(data)
        self.assertTrue(clients.iloc[0].eligible); self.assertTrue(clients.iloc[0].ever30)
        self.assertEqual(clients.iloc[0].balance,400)
        self.assertEqual(summarize_vintage(clients).iloc[0].ever_saldo,1)

    def test_invalid_data_and_cohort_conflicts_rejected(self):
        data=pd.DataFrame([row('a','1',1,0),row('a','1',2,0),row('a','1',3,0)])
        for column,value in [('dpd',-1),('dpd','unknown'),('mob',1.5)]:
            bad=data.copy();bad[column]=bad[column].astype(object);bad.loc[1,column]=value
            with self.assertRaises(ValueError): build_vintage(bad)
        bad=data.copy();bad.loc[1,'corte_origen']='2024-02'
        with self.assertRaises(ValueError): build_vintage(bad)

    def test_negative_balance_and_absent_asof_are_not_zero(self):
        data=pd.DataFrame([row('a','1',1,0),row('a','1',2,0),row('a','1',3,0,-1)])
        a,_=build_vintage(data);self.assertTrue(a.iloc[0].eligible);self.assertFalse(a.iloc[0].balance_valid)
        with self.assertRaises(ValueError):build_vintage(data.drop(columns='fecha_disponibilidad'),as_of='2024-04-30')

    def test_mob_zero_optional_and_zero_denominator(self):
        data=pd.DataFrame([row('a','1',0,31),row('a','1',1,0),row('a','1',2,0),row('a','1',3,0,0)])
        a,_=build_vintage(data);self.assertFalse(a.iloc[0].ever30)
        a,_=build_vintage(data,include_mob0=True); self.assertTrue(a.iloc[0].ever30)
        self.assertTrue(pd.isna(summarize_vintage(a).iloc[0].ever_saldo))

if __name__=='__main__': unittest.main()
