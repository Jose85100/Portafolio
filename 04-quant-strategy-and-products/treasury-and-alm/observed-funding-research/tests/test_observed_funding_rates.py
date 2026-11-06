import importlib.util,pathlib,unittest
p=pathlib.Path(__file__).resolve().parents[1]/"src"/"observed_funding_rates.py"
spec=importlib.util.spec_from_file_location("observed_funding_rates",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RateTests(unittest.TestCase):
    def setUp(self):
        self.sfc=[{"fecha_corte":"2026-06-30","cdt":"10000"}]
        self.rates=[{"mes":"2026-03","dtf_promedio":"10"}]
    def test_assumed_pass_through(self):
        result=m.calculate(self.sfc,self.rates)
        self.assertEqual([x["annualized_increment_COP"] for x in result["scenarios"]],[0,50,100])
        self.assertFalse(result["actual_deposit_cost_observed"])
    def test_missing_rate_stays_missing(self):
        with self.assertRaisesRegex(ValueError,"no synthetic fill"):
            m.calculate(self.sfc,[])
    def test_invalid_pass_through(self):
        with self.assertRaisesRegex(ValueError,"pass-through"):
            m.calculate(self.sfc,self.rates,pass_through=(1.2,))
    def test_duplicate_month(self):
        with self.assertRaisesRegex(ValueError,"Duplicate DTF"):
            m.calculate(self.sfc,self.rates*2)
if __name__=="__main__":unittest.main()
