import calendar,importlib.util,pathlib,unittest
p=pathlib.Path(__file__).resolve().parents[1]/"src"/"observed_alm.py"
s=importlib.util.spec_from_file_location("observed_alm",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def item(y,month):
    return {"fecha_corte":f"{y}-{month:02d}-{calendar.monthrange(y,month)[1]}","depositos_corriente":"20",
            "depositos_ahorro":"40","cdt":"40","cartera_creditos":"80",
            "creditos_vivienda":"10","numero_oficinas":"1"}
class Tests(unittest.TestCase):
    def setUp(self):
        self.rows=[item(y,mth) for y in (2024,2025) for mth in (3,6,9,12)]
    def test_observed_metrics(self):
        r=m.calculate(self.rows)
        self.assertEqual(r["observed_quarters"],8)
        self.assertAlmostEqual(r["latest_observed"]["ratio_cartera_depositos"],.8)
        self.assertEqual(r["latest_observed"]["evidence"],"OBSERVED_AGGREGATE_NOT_BANK_LCR")
    def test_stress_is_not_observation(self):
        r=m.calculate(self.rows)
        self.assertTrue(all(s["assumption_class"]=="HYPOTHETICAL_NOT_OBSERVED" for s in r["scenarios"]))
        self.assertEqual([s["ratio_after_runoff"] for s in r["scenarios"]],
                         sorted(s["ratio_after_runoff"] for s in r["scenarios"]))
    def test_no_duplicate_quarter(self):
        with self.assertRaisesRegex(ValueError,"Duplicate"):m.calculate(self.rows+[self.rows[0]])
    def test_missing_quarter_is_rejected(self):
        rows=self.rows+[item(2026,3)]
        del rows[2]
        with self.assertRaisesRegex(ValueError,"Missing quarter"):m.calculate(rows)
    def test_invalid_quarter_end_is_rejected(self):
        rows=[dict(x) for x in self.rows];rows[0]["fecha_corte"]="2024-03-30"
        with self.assertRaisesRegex(ValueError,"Bad quarter"):m.calculate(rows)
    def test_no_negative_balances(self):
        r=[dict(x) for x in self.rows];r[0]["cdt"]="-1"
        with self.assertRaisesRegex(ValueError,"Negative"):m.calculate(r)
    def test_quantile(self):
        self.assertEqual(m.quantile([1,2,3,4],.5),2.5)
if __name__=="__main__":unittest.main()
