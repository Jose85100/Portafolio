import sqlite3
import unittest
from pathlib import Path

class MultimodelSchemaTests(unittest.TestCase):
    def test_stage_basis_and_references(self):
        c=sqlite3.connect(':memory:')
        c.executescript((Path(__file__).parents[1]/'sql/multimodel_results_schema.sql').read_text())
        for name in ['PD','LGD','EAD','POLICY']:
            c.execute('INSERT INTO model_version VALUES (?,?,?,?,?)',(name,'1',name,'a'*64,'{}'))
        c.execute("INSERT INTO ecl_run VALUES ('run','2026-10-18','synthetic','PD','1','LGD','1','EAD','1','POLICY','1','research')")
        c.execute("INSERT INTO ecl_scenario VALUES ('run','base',1.)")
        self.assertEqual(c.execute('SELECT valid FROM scenario_weight_audit').fetchone()[0],1)
        c.execute("INSERT INTO ecl_result VALUES ('run','a','base',3,'funded_recovery_cashflows',10.)")
        with self.assertRaises(sqlite3.IntegrityError):
            c.execute("INSERT INTO ecl_result VALUES ('run','b','base',3,'monthly_components',10.)")
        with self.assertRaises(sqlite3.IntegrityError):
            c.execute("INSERT INTO ecl_result VALUES ('run','c','missing',1,'monthly_components',10.)")
        c.close()
